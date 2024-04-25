import glob
import sys


def count_violations_for_RL(file_contents_parts):
    count = 0
    DfC_min_boolean = False;
    DfV_min_boolean = False;
    DfP_min_boolean = False;
    DfM_min_boolean = False;
    DT_max_boolean = False;
    traffic_lights_max_boolean = False;
    for part in file_contents_parts:
            if part.__contains__("#"):
                part_without_date = part.split("#")[2].replace("[","").replace("]","")
                feature_values = part_without_date.split("]:")[0]
                fitness_values = part_without_date

                fitness_values_parts = fitness_values.split(",")

#                print(fitness_values_parts)
                DfC_min = float(fitness_values_parts[0])
                DfV_min = float(fitness_values_parts[1])
                DfP_min = float(fitness_values_parts[2])
                DfM_min = float(fitness_values_parts[3])
                DT_max = float(fitness_values_parts[4])
                traffic_lights_max = float(fitness_values_parts[5])
                if not DfC_min_boolean:
                    if DfC_min >= 1000000:
                        count = count+1
                        DfC_min_boolean = True
                if not DfV_min_boolean:
                    if DfV_min >= 1000000:
                        count = count+1
                        DfV_min_boolean = True
                if not DfP_min_boolean:
                    if DfP_min >= 1000000:
                        count = count+1
                        DfP_min_boolean = True
                if not DfM_min_boolean:
                    if DfM_min >= 1000000:
                        count = count+1
                        DfM_min_boolean = True
                if not DT_max_boolean:
                    if DT_max >= 1000000:
                        count = count+1
                        DT_max_boolean = True
                                            
                if not traffic_lights_max_boolean:
                        if traffic_lights_max >= 1000000:
                            count = count + 1
                            traffic_lights_max_boolean = True
    
    return count

def count_violations(file_contents_parts):
    count = 0
    DfC_min_boolean = False;
    DfV_min_boolean = False;
    DfP_min_boolean = False;
    DfM_min_boolean = False;
    DT_max_boolean = False;
    traffic_lights_max_boolean = False;
    index = 0
    for index in range(0, len(file_contents_parts)):
            part = file_contents_parts[index]
            if part.__contains__("#"):
                part_without_date = part.split("#")[1]
                feature_values = part_without_date.split("]:")[0]
                fitness_values = part_without_date

                fitness_values_parts = fitness_values.split(",")


                DfC_min = float(fitness_values_parts[0])
                DfV_min = float(fitness_values_parts[1])
                DfP_min = float(fitness_values_parts[2])
                DfM_min = float(fitness_values_parts[3])
                DT_max = float(fitness_values_parts[4])
                traffic_lights_max = float(fitness_values_parts[5])
                if not DfC_min_boolean:
                    if DfC_min <= 0:
                        count = count+1
                        DfC_min_boolean = True
                if not DfV_min_boolean:
                    if DfV_min <= 0:
                        count = count+1
                        DfV_min_boolean = True
                if not DfP_min_boolean:
                    if DfP_min <= 0:
                        count = count+1
                        DfP_min_boolean = True
                if not DfM_min_boolean:
                    if DfM_min <= 0:
                        count = count+1
                        DfM_min_boolean = True
                if not DT_max_boolean:
                    if DT_max <= 0.95:
                        if not "VIF" in file_contents_parts[index-1]:
                                                count = count+1
                                                DT_max_boolean = True
                if not traffic_lights_max_boolean:
                    if traffic_lights_max <= 0:
                        count = count + 1
                        traffic_lights_max_boolean = True
    return count

def get_time(stime):
   return stime.split(",")[0]

def handle_config(folder_names,config):
    file_writer = open('Processed-data-RQ2.txt', 'w')
    # file_writer.write(str(i) + ',')
    for folder_n in range(len(folder_names)):
        for i in range(20, 260, 20):
            folder = folder_names[folder_n]
            file_writer.write(folder + '-' + str(i) + ", ")
            list_of_all_files = (glob.glob('Sample_data/RQ2'  + "/" + folder + "/*.log"))

            for file in list_of_all_files:
                count = 0
            
                file_reader = open(file, "r")
                file_contents_parts = []
                file_contents_ps = file_reader.read().split("\n")
                stime = file_contents_ps[0]
                if not "Started" in stime:
                    stime = file_contents_ps[1]
                if "Started" in stime:
                    stime = get_time(stime)
                    FMT = '%Y-%m-%d %H:%M:%S'
                    for content in file_contents_ps:
                        if '#' not in content:
                            continue
                        n_time = get_time(content)
                        if n_time == stime:
                            continue
                        time_diff = datetime.strptime(n_time, FMT) - datetime.strptime(stime, FMT)
                        minutes = divmod(time_diff.total_seconds(), 60)
                        if minutes[0] < i:
                            file_contents_parts.append(content)
                        else:
                            break
                else:
                    print("check me")
                if "MORLAT" in folder_names:
                    count = count + (count_violations_for_RL(file_contents_parts)/ 6.0)
                else:
                    count = count + (count_violations(file_contents_parts)/ 6.0)
                file_writer.write(str(count)+",")

            file_writer.write('\n')
if __name__ == "__main__":
    from datetime import datetime

    folder_names = ["RS"]
    handle_config(folder_names,'config-2')


