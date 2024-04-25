import sys

from carla import Transform, Location

source_flags = None;
self_debug = 0
import os
import logging

logger = logging.getLogger()
from datetime import datetime
from leaderboard.config import abs_path,scenario


class FitnessExtractor:
    ego_vehicle_location = None;
    start_loc = None
    first = True;
    i = 0
    first_dist_negative = True

    def get_distance_from_center_lane(self, ego_vehicle, world):
        ego_vehicle_location = ego_vehicle.get_location()

        waypoint = world.get_map().get_waypoint(ego_vehicle_location, project_to_road=True)

        ego_vehicle_loc = Location(x=ego_vehicle_location.x, y=ego_vehicle_location.y, z=0.0)
        if self_debug == 1:
            print("Distance From center of Lane: " + str(ego_vehicle_loc.distance(waypoint.transform.location)))
        return ego_vehicle_loc.distance(waypoint.transform.location)

    def get_min_distance_from_other_vehicle(self, ego_vehicle, world, vehicle_infront):
        ego_vehicle_location = ego_vehicle.get_location()

        distances = [1000]
        target_vehicle = vehicle_infront
        distance = ego_vehicle_location.distance(target_vehicle.get_location())
        distances.append(distance)
        if self_debug == 1:
            print("Minimum Distance from other Vehicle: " + str(min(distances)))
        return min(distances)  # substracting distances from center of vehicle

    def get_min_distance_from_pedestrians(self, ego_vehicle, ped):
        distances = [1000]
        ego_vehicle_location = ego_vehicle.get_location()
        target_vehicle = ped
        distance = ego_vehicle_location.distance(target_vehicle.get_location())
        if self_debug == 1:
            print("Minimum Distance from Pedestrians: " + str(min(distances)))
        return distance  # substracting distances from center of vehicle

    def get_min_distance_from_static_mesh(self, ego_vehicle, world):
        distances = [1000]
        ego_vehicle_location = ego_vehicle.get_location()

        for target_vehicle in world.get_actors().filter('static.*'):
            distance = ego_vehicle_location.distance(target_vehicle.get_location())
            distances.append(distance)

        for target_vehicle in world.get_actors().filter('traffic.*.*'):
            distance = ego_vehicle_location.distance(target_vehicle.get_location())
            distances.append(distance)
        for target_vehicle in world.get_actors().filter('traffic.*'):
            distance = ego_vehicle_location.distance(target_vehicle.get_location())
            distances.append(distance)
        if self_debug == 1:
            print("Minimum Distance from static Mesh: " + str(min(distances)))
        return (min(distances))  # substracting distances from center of vehicle

    def get_distance_from_destination(self, ego_vehicle):
        ego_vehicle_location = ego_vehicle.get_location()
        if (self.first):
            import os
            file_name = abs_path+"RL-comps/all-data.txt"
            if os.path.exists(file_name):
                os.remove(file_name)
            file_name_2 = abs_path+"RL-comps/exall-data.txt"
            if os.path.exists(file_name_2):
                os.remove(file_name_2)

            self.first = False
            self.start_loc = ego_vehicle_location

            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s | %(message)s',
                                          '%m-%d-%Y %H:%M:%S')

            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.setFormatter(formatter)

            file_handler = logging.FileHandler(file_name)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            # logger.addHandler(stdout_handler)
        if int(scenario) == 0:
            self.final_destination = Location(x=37.542881, y=-136.170952,z=0) # Straight Road
        if int(scenario) == 1:
            self.final_destination = Location(x=1.05, y=-94.89, z=0)  # Left Turn Road

        if int(scenario) == 2:
            self.final_destination = Location(x=96.55, y=-38.23, z=0)  # Left Turn Road
        # dist = ego_vehicle_location.distance(self.start_loc);

        dist = ego_vehicle_location.distance(self.final_destination)  # 9.8 for v1
        # print(dist)
        if self_debug == 1:
            print("Distance from Final Destination: " + str(dist))

        return dist

    def extract_from_world(self, ego_vehicle, world, vehicle_infront, ped):
        divider = 116

        if int(scenario) == 1:
            divider = 123.6
        if int(scenario) == 2:
            divider = 109.6

        dist_center_lane = self.get_distance_from_center_lane(ego_vehicle, world) / 1.15
        dist_min_other_vehicle = self.get_min_distance_from_other_vehicle(ego_vehicle, world, vehicle_infront) / divider
        dist_min_pedestrian = self.get_min_distance_from_pedestrians(ego_vehicle, ped) / divider
        dist_min_mesh = self.get_min_distance_from_static_mesh(ego_vehicle, world) / divider
        dist_from_final_destnation = self.get_distance_from_destination(ego_vehicle) / divider

        print(vehicle_infront.get_transform().rotation)
        to_log = str(ego_vehicle.get_location()) + "$" + str(vehicle_infront.get_location()) + ">DfC:" + str(
            "{:.4f}".format(dist_center_lane)) + ",DfV:" + str("{:.2f}".format(dist_min_other_vehicle)) + ",DfP:" + str(
            "{:.2f}".format(dist_min_pedestrian)) + ",DfM:" + str("{:.2f}".format(dist_min_mesh)) + ",DT:" + str(
            "{:.2f}".format(dist_from_final_destnation))

        if dist_from_final_destnation >= 0:
            logging.info(to_log)

        file_name = abs_path+"RL-comps/all-data.txt"
        traffic_lights_max = 1

        RL = True

        if RL:
            dist_center_lane = 1 - dist_center_lane
            fileename = os.path.basename(file_name)
            file_name_ex = os.path.dirname(file_name) + '/ex' + fileename

            if os.path.exists(file_name_ex):
                file_handler_ex = open(file_name_ex, "r")
                for line_ex in file_handler_ex:
                    if "red_light" in line_ex:
                        print("Red_light invasion")
                        traffic_lights_max = 0
                    if "lane" in line_ex:
                        print("lane invasion")
                        dist_center_lane = 0
                    if "vehicle" in line_ex:
                        print("vehicle collision")
                        dist_min_other_vehicle = 0
                    if "pedestrian" in line_ex:
                        dist_min_pedestrian = 0
                os.remove(file_name_ex)

        to_write = str("{:.4f}".format(dist_center_lane)) + "," + str(
            "{:.2f}".format(dist_min_other_vehicle)) + "," + str(
            "{:.2f}".format(dist_min_pedestrian)) + "," + str("{:.2f}".format(dist_min_mesh)) + "," + str(
            "{:.2f}".format(dist_from_final_destnation) + "," + str(traffic_lights_max))
        return to_write
        # reward_file = open(reward_file_name,'w')
        # reward_file.write(to_write)
