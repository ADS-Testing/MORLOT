import os

from config import abs_path,scenario

def get_values(fv):
    file_name = fv
    file_handler = open(file_name, "r")
    DfC_min = 1
    DfV_min = 1
    DfP_min = 1
    DfM_min = 1
    DT_max = -1
    traffic_lights_max = 1
    first = True
    distance_Max = -1

    fileename= os.path.basename(file_name)
#    print(os.path.basename(file_name))
    file_name_ex = os.path.dirname(file_name)+'/ex'+fileename
    print(file_name_ex)
    if os.path.exists(file_name_ex):
        file_handler_ex = open(file_name_ex, "r")
        for line_ex in file_handler_ex:
            if "red_light" in line_ex:
                print("Red_light invasion")
                traffic_lights_max = 0
            if "lane" in line_ex:
                print("lane invasion")
                DfC_min = 0
            if "vehicle" in line_ex:
                print("vehicle collision")
                DfV_min = 0
            if "pedestrian" in line_ex:
                DfP_min = 0


    for line in file_handler:
        line_parts = line.split('>')
        clean_line_parts = line_parts[1].replace('DfC:','').replace('DfV:','').replace('DfP:','').replace('DfM:','').replace('DT:','')
        double_parts= clean_line_parts.split(',')
        DfC = float(double_parts[0])
        DfV = float(double_parts[1])
        DfP = float(double_parts[2])
        DfM = float(double_parts[3])
        DT  = float(double_parts[4])

        if DT < 0:
            DT_max = 1
            break

        if first:
            first = False
            distance_Max = DT

        DfC = 1 - (DfC)
        if DfV > 1:
            DfV = 1
        if DfP > 1:
            DfP = 1
        if DfM > 1:
            DfM = 1

        distance_travelled = distance_Max - DT
        if DfC < DfC_min:
            DfC_min = DfC
        if DfV < DfV_min:
            DfV_min = DfV
        if DfM < DfM_min:
            DfM_min = DfM
        if DfP < DfP_min:
            DfP_min = DfP
        if distance_travelled > DT_max:
            DT_max = distance_travelled




    # print (str(DfC_min)+","+str(DfV_max)+","+str(DfP_max)+","+str(DfM_max)+","+str(DT_max)+","+str(traffic_lights_max))

    if DT_max < 0.95:
        yparts= line_parts[0].split("y=")
        y1 = float(yparts[1].split(",")[0])
        y2 = float(yparts[2].split(",")[0])

        if int(scenario)==2:
            xparts = line_parts[0].split("x=")
            x1 = float(xparts[1].split(",")[0])
            x2 = float(xparts[2].split(",")[0])
            if abs(abs(x1) - abs(x2)) < 20:
                DT_max = 1

        else:
            if abs(abs(y1) - abs(y2)) < 20:
                DT_max = 1
        check_file = abs_path+"RL-comps/terminate.txt"
        if os.path.exists(check_file):
            txt = open(check_file).read()
            if "VIF" in txt:
                DT_max = 1

    return  line_parts[0],DfC_min, DfV_min, DfP_min, DfM_min, DT_max, traffic_lights_max


def check_valid():
    file_handler = open(abs_path+"RL-comps/all-data.txt", "r")
    check_file = abs_path+"RL-comps/terminate.txt"
    if os.path.exists(check_file):
        txt = open(check_file).read()
        if "VIF" in txt:
            return False
    line = ""
    for line in file_handler:
        continue
    line_parts = line.split('>')
    yparts = line_parts[0].split("y=")
    y1 = float(yparts[1].split(",")[0])
    y2 = float(yparts[2].split(",")[0])

    if int(scenario) == 2:
        xparts = line_parts[0].split("x=")
        x1 = float(xparts[1].split(",")[0])
        x2 = float(xparts[2].split(",")[0])
        if abs(abs(x1) - abs(x2)) < 20:
            return False
    else:
        if abs(abs(y1) - abs(y2)) < 20:
            return False
    return True


def main():
    print("in main")
if __name__ == "__main__":
    main()
