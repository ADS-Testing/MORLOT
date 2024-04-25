#!/usr/bin/env python

# Copyright (c) 2018-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
This module provides the ScenarioManager implementations.
It must not be modified and is for reference only!
"""

from __future__ import print_function

import random
import signal
import sys
import time

import py_trees
import carla

from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.timer import GameTime
from srunner.scenariomanager.watchdog import Watchdog

from leaderboard.autoagents.agent_wrapper import AgentWrapper, AgentError
from leaderboard.envs.sensor_interface import SensorReceivedNoData
from leaderboard.utils.result_writer import ResultOutputProvider
from leaderboard.scenarios.fitness_value_extractor import FitnessExtractor
from leaderboard.config import abs_path,scenario
from os import path
import os


class ScenarioManager(object):
    """
    Basic scenario manager class. This class holds all functionality
    required to start, run and stop a scenario.

    The user must not modify this class.

    To use the ScenarioManager:
    1. Create an object via manager = ScenarioManager()
    2. Load a scenario via manager.load_scenario()
    3. Trigger the execution of the scenario manager.run_scenario()
       This function is designed to explicitly control start and end of
       the scenario execution
    4. If needed, cleanup with manager.stop_scenario()
    """

    def __init__(self, timeout, debug_mode=False):
        """
        Setups up the parameters, which will be filled at load_scenario()
        """
        self.scenario = None
        self.scenario_tree = None
        self.scenario_class = None
        self.ego_vehicles = None
        self.other_actors = None

        self._debug_mode = debug_mode
        self._agent = None
        self._running = False
        self._timestamp_last_run = 0.0
        self._timeout = float(timeout)

        # Used to detect if the simulation is down
        watchdog_timeout = 1000  # max(5, self._timeout - 2) change
        self._watchdog = Watchdog(watchdog_timeout)

        # Avoid the agent from freezing the simulation
        agent_timeout = 1000  # watchdog_timeout - 1 change -
        self._agent_watchdog = Watchdog(agent_timeout)

        self.scenario_duration_system = 0.0
        self.scenario_duration_game = 0.0
        self.start_system_time = None
        self.end_system_time = None
        self.end_game_time = None
        self.fe = FitnessExtractor()
        # Register the scenario tick as callback for the CARLA world
        # Use the callback_id inside the signal handler to allow external interrupts
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """
        Terminate scenario ticking when receiving a signal interrupt
        """
        self._running = False

    def cleanup(self):
        """
        Reset all parameters
        """
        self._timestamp_last_run = 0.0
        self.scenario_duration_system = 0.0
        self.scenario_duration_game = 0.0
        self.start_system_time = None
        self.end_system_time = None
        self.end_game_time = None

    def load_scenario(self, scenario, agent, rep_number):
        """
        Load a new scenario
        """

        GameTime.restart()
        self._agent = AgentWrapper(agent)
        self.scenario_class = scenario
        self.scenario = scenario.scenario
        self.scenario_tree = self.scenario.scenario_tree
        self.ego_vehicles = scenario.ego_vehicles
        self.vif = scenario.vif
        self.ped = scenario.ped
        self.other_actors = scenario.other_actors
        self.repetition_number = rep_number

        self.throttle = 0.5
        self.steering = 0
        self.sun_altitude_angle = 90
        self.weather = 0
        self.fog = 0
        self.wetness = 0
        self.ped_speed = 0.1
        self.ped_x = -1
        self.ped_y = 0
        self.precipitation = 0
        self.precipitation_deposits = 0
        self.cloudiness = 0
        self.wetness = 0

        # To print the scenario tree uncomment the next line
        # py_trees.display.render_dot_tree(self.scenario_tree)

        self._agent.setup_sensors(self.ego_vehicles[0], self._debug_mode)

    def run_scenario(self):
        """
        Trigger the start of the scenario and wait for it to finish/fail
        """
        self.start_system_time = time.time()
        self.start_game_time = GameTime.get_time()

        self._watchdog.start()
        self._running = True

        while self._running:
            timestamp = None
            world = CarlaDataProvider.get_world()
            if world:
                snapshot = world.get_snapshot()
                if snapshot:
                    timestamp = snapshot.timestamp
            if timestamp:
                self._tick_scenario(timestamp)

    def write_state(self):
        i = 5

    def update_values_for_action(self):

        action_file = abs_path + "RL-comps/action.txt"
        while not path.exists(action_file):
            time.sleep(0.01)
        action = open(action_file, "r").read()
        if not action:
            time.sleep(0.05)
            action = open(action_file, "r").read()

        action = int(action)
        if path.exists(action_file):
            os.remove(action_file)
        addition = -1
        if action == 0:
            if self.throttle < 0.9:
                self.throttle = self.throttle + 0.1

        elif action == 1:
            if self.throttle > 0.1:
                self.throttle = self.throttle - 0.1

        elif action == 2:
            if self.steering < 1:
                self.steering = self.steering + 0.01
        elif action == 3:
            if self.steering > -1:
                self.steering = self.steering - 0.01
        # elif action == 4:
        #     self.steering = 0.0
        elif action == 5 + addition:
            if self.sun_altitude_angle < 160:
                self.sun_altitude_angle = self.sun_altitude_angle + 2.5
        elif action == 6 + addition:
            if self.sun_altitude_angle > -30:
                self.sun_altitude_angle = self.sun_altitude_angle - 2.5

        elif action == 7 + addition:
            if self.weather < 100:
                self.weather = self.weather + 2.5
        elif action == 8 + addition:
            if self.weather > 0:
                self.weather = self.weather - 2.5

        elif action == 9 + addition:
            if self.fog < 90:
                self.fog = self.fog + 2.5

        elif action == 10 + addition:
            if self.fog > 0:
                self.fog = self.fog - 2.5

        elif action == 11 + addition:
            if self.ped_speed < 1.5:
                self.ped_speed = self.ped_speed + 0.05

        elif action == 12 + addition:
            if self.ped_speed > 0.3:
                self.ped_speed = self.ped_speed - 0.05

        elif action == 13 + addition:
            if self.ped_x < 1:
                self.ped_x = self.ped_x + 0.1
        elif action == 14 + addition:
            if self.ped_x > -0.5:
                self.ped_x = self.ped_x - 0.1
        elif action == 15 + addition:
            if self.ped_y < -0.1:
                self.ped_y = self.ped_y + 0.1
        elif action == 16 + addition:
            if self.ped_y > -1:
                self.ped_y = self.ped_y - 0.1
        else:
            print("do nothing")

    def apply_RL_action(self):
        self.update_values_for_action()
        if self.weather == 0:
            self.cloudiness = 0
            self.precipitation = 0
            self.precipitation_deposits = 0
            self.wetness = 0
        else:
            self.cloudiness = self.weather  # * 10
            self.precipitation = self.weather  # * 10
            self.precipitation_deposits = self.weather  # * 10
            self.wetness = self.weather  # *10

        # self.sun_altitude_angle = -90

        weather = carla.WeatherParameters(
            cloudiness=self.cloudiness, precipitation=self.precipitation,
            precipitation_deposits=self.precipitation_deposits, wind_intensity=0.0, sun_azimuth_angle=0.0,
            sun_altitude_angle=self.sun_altitude_angle, fog_density=self.fog, fog_distance=self.fog,
            wetness=self.wetness)

        CarlaDataProvider.get_world().set_weather(weather)

        vif_action = carla.VehicleControl()
        vif_action.throttle = self.throttle
        vif_action.steer = self.steering

        ped_control = carla.WalkerControl(direction=carla.Vector3D(self.ped_x, self.ped_y, 0.0), speed=self.ped_speed)
        ego_y = abs(self.ego_vehicles[0].get_location().y)
        ped_y = abs(self.ped.get_location().y)

        if int(scenario) == 0:
            if abs (self.vif.get_location().y) < abs(self.ego_vehicles[0].get_location().y):
                print("Stopping simulation due to location of VIF ")
                terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                terminate_algo.write("$L_VIF")
                terminate_algo.close()

            if -180.0 < self.vif.get_transform().rotation.yaw < 30 or 150 < self.vif.get_transform().rotation.yaw < 180:
                self.vif.apply_control(vif_action)
            else:
                print("Stopping simulation due to direction of VIF ")
                vif_action = carla.VehicleControl()
                vif_action.throttle = 0
                terminate_algo = open(abs_path+"RL-comps/terminate.txt", 'w')
                terminate_algo.write("$D_VIF")
                terminate_algo.close()
                vif_action.steer = 0
                self.vif.apply_control(vif_action)

        elif int(scenario) == 1:

            if abs(self.ego_vehicles[0].get_location().y)<70:
                if abs(self.vif.get_location().y) < abs(self.ego_vehicles[0].get_location().y):
                    print("Stopping simulation due to location of VIF ")
                    terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                    terminate_algo.write("$L_VIF")
                    terminate_algo.close()
            else:
                if abs(self.vif.get_location().x) > abs(self.ego_vehicles[0].get_location().x):
                    print("Stopping simulation due to location of VIF ")
                    terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                    terminate_algo.write("$L_VIF")
                    terminate_algo.close()




            if -180 < self.vif.get_transform().rotation.yaw < 30 or 150 < self.vif.get_transform().rotation.yaw < 180:
                self.vif.apply_control(vif_action)
            else:
                print("Stopping simulation due to direction of VIF ")
                vif_action = carla.VehicleControl()
                vif_action.throttle = 0
                terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                terminate_algo.write("$D_VIF")
                terminate_algo.close()
                vif_action.steer = 0
                self.vif.apply_control(vif_action)
        elif int(scenario) == 2:
            if  abs(self.ego_vehicles[0].get_location().x)<85:
                if abs(self.vif.get_location().x) < abs(self.ego_vehicles[0].get_location().x):
                    print("Stopping simulation due to location of VIF ")
                    terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                    terminate_algo.write("$L_VIF")
                    terminate_algo.close()
            else:
                if abs(self.vif.get_location().y) > abs(self.ego_vehicles[0].get_location().y):
                    print("Stopping simulation due to location of VIF ")
                    terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                    terminate_algo.write("$L_VIF")
                    terminate_algo.close()
            #
            if -120 < self.vif.get_transform().rotation.yaw < 120: #or -180 < self.vif.get_transform().rotation.yaw < -150:
                self.vif.apply_control(vif_action)
            else:
                print("Stopping simulation due to direction of VIF ")
                vif_action = carla.VehicleControl()
                vif_action.throttle = 0
                terminate_algo = open(abs_path + "RL-comps/terminate.txt", 'w')
                terminate_algo.write("$D_VIF")
                terminate_algo.close()
                vif_action.steer = 0
                self.vif.apply_control(vif_action)


        if int(scenario) == 2:
            if abs(self.ped.get_location().x - self.ego_vehicles[0].get_location().x) < 2.5:
                print("not applying pedestrian control")
            else:
                self.ped.apply_control(ped_control)
        else:
            if abs(ped_y - ego_y) < 2.5:
                print("not applying pedestrian control")
            else:
                self.ped.apply_control(ped_control)

    def get_difference_speed(self, ego_vehicle, vif):
        e_v = ego_vehicle.get_velocity();
        o_v = vif.get_velocity()

        distance_x = o_v.x - e_v.x
        distance_y = o_v.y - e_v.y
        distance_x = round(distance_x, 1)

        distance_y = round(distance_y, 1)
        return e_v.x, e_v.y, distance_x, distance_y

    def get_difference_acc(self, ego_vehicle, vif):
        e_v = ego_vehicle.get_acceleration();
        o_v = vif.get_acceleration()

        distance_x = o_v.x - e_v.x
        distance_y = o_v.y - e_v.y
        distance_x = round(distance_x, 1)

        distance_y = round(distance_y, 1)

        return e_v.x, e_v.y, distance_x, distance_y

    def get_min_distance_from_other_vehicle(self, ego_vehicle, vehicle_infront):
        ego_vehicle_location = ego_vehicle.get_location()
        distances = [1000]

        e_v_x = ego_vehicle_location.x / 12
        e_v_y = ego_vehicle_location.y / 12

        target_vehicle = vehicle_infront

        distance = ego_vehicle_location.distance(target_vehicle.get_location())
        distances.append(distance)

        distance_x = round(target_vehicle.get_location().x - ego_vehicle_location.x, 1)
        distance_y = round(target_vehicle.get_location().y - ego_vehicle_location.y, 1)
        return min(distances), e_v_x, e_v_y, distance_x, distance_y

    def get_state(self):
        self.speed_x, self.speed_y, self.speed_diff_x, self.speed_diff_y = self.get_difference_speed(
            self.ego_vehicles[0], self.vif)
        self.acc_x, self.acc_y, self.acc_diff_x, self.acc_diff_y = self.get_difference_acc(self.ego_vehicles[0],
                                                                                           self.vif)
        self.distance, self.dist_x, self.dist_y, self.distance_x, self.distance_y = self.get_min_distance_from_other_vehicle(
            self.ego_vehicles[0], self.vif)

        self.state = [self.distance,
                      self.dist_x, self.dist_y, self.distance_x, self.distance_y,
                      self.speed_x, self.speed_y, self.speed_diff_x, self.speed_diff_y,
                      self.acc_x, self.acc_y, self.acc_diff_x, self.acc_diff_y, self.weather, self.fog,
                      self.ped_x, self.ped_y, self.ped_speed, self.sun_altitude_angle
                      ]
        return str(self.state).replace("[", "").replace("]", "").replace(" ", "")

    def get_reward_and_state(self):
        reward_file_name = abs_path + "RL-comps/reward.txt"

        to_write = "1,1,1,1,1,1#" + self.get_state()

        reward_file = open(reward_file_name, 'w')
        reward_file.write(to_write)
        reward_file.close()

    def write_reward_and_state(self, rewards):
        reward_file_name = abs_path + "RL-comps/reward.txt"

        to_write = rewards + "#" + self.get_state()

        reward_file = open(reward_file_name, 'w')
        reward_file.write(to_write)
        reward_file.close()

    def _tick_scenario(self, timestamp):
        """
        Run next tick of scenario and the agent and tick the world.
        """

        if self._timestamp_last_run < timestamp.elapsed_seconds and self._running:
            self._timestamp_last_run = timestamp.elapsed_seconds

            self._watchdog.update()
            # Update game time and actor information
            GameTime.on_carla_tick(timestamp)
            CarlaDataProvider.on_carla_tick()

            try:
                ego_action = self._agent()

            # Special exception inside the agent that isn't caused by the agent
            except SensorReceivedNoData as e:
                raise RuntimeError(e)

            except Exception as e:
                raise AgentError(e)

            check_file = abs_path + "RL-comps/start_RL.txt"
            if not os.path.exists(check_file):
                chk_file = open(check_file, 'x')
                self.get_reward_and_state()

            self.ego_vehicles[0].apply_control(ego_action)

            self.apply_RL_action()
            if self.sun_altitude_angle < 0.0:
                self.ego_vehicles[0].set_light_state(
                    carla.VehicleLightState(carla.VehicleLightState.Position | carla.VehicleLightState.LowBeam))

            values = self.fe.extract_from_world(self.ego_vehicles[0], CarlaDataProvider.get_world(), self.vif, self.ped)
            self.write_reward_and_state(values)

            # Tick scenario
            self.scenario_tree.tick_once()

            if self._debug_mode:
                py_trees.display.print_ascii_tree(
                    self.scenario_tree, show_status=True)
                sys.stdout.flush()

            if self.scenario_tree.status != py_trees.common.Status.RUNNING:
                self._running = False

            spectator = CarlaDataProvider.get_world().get_spectator()
            ego_trans = self.ego_vehicles[0].get_transform()
            spectator.set_transform(carla.Transform(ego_trans.location + carla.Location(z=25),
                                                    carla.Rotation( pitch = -90)))

        if self._running and self.get_running_status():
            CarlaDataProvider.get_world().tick(self._timeout)

    def get_running_status(self):
        """
        returns:
           bool: False if watchdog exception occured, True otherwise
        """
        return self._watchdog.get_status()

    def stop_scenario(self):
        """
        This function triggers a proper termination of a scenario
        """
        self._watchdog.stop()

        self.end_system_time = time.time()
        self.end_game_time = GameTime.get_time()

        self.scenario_duration_system = self.end_system_time - self.start_system_time
        self.scenario_duration_game = self.end_game_time - self.start_game_time

        if self.get_running_status():
            if self.scenario is not None:
                self.scenario.terminate()

            if self._agent is not None:
                self._agent.cleanup()
                self._agent = None

            self.analyze_scenario()

    def analyze_scenario(self):
        """
        Analyzes and prints the results of the route
        """
        global_result = '\033[92m' + 'SUCCESS' + '\033[0m'

        for criterion in self.scenario.get_criteria():
            if criterion.test_status != "SUCCESS":
                global_result = '\033[91m' + 'FAILURE' + '\033[0m'

        if self.scenario.timeout_node.timeout:
            global_result = '\033[91m' + 'FAILURE' + '\033[0m'

        ResultOutputProvider(self, global_result)
