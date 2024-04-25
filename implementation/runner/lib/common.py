import subprocess
import time
import os
import sys
import psutil
import multiprocessing
from config import abs_path

def terminate(logger):
        check_file = abs_path+"RL-comps/terminate.txt"
        if os.path.exists(check_file):
            time.sleep(1)
            logger.info(open(check_file).read())
            return True
        return False


def run_carla(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               universal_newlines=True, shell=True)
def run_command(cmd):
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True,shell = True)

        while True:
            output = process.stdout.readline()

            return_code = process.poll()
            if return_code is not None:
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    print(output.strip())
                break
            return return_code
def remove_unnecessary_files():
        temp_terminate_file = abs_path+"RL-comps/terminate.txt"
        if os.path.exists(temp_terminate_file):
            os.remove(temp_terminate_file)
        temp_terminate_file = abs_path+"RL-comps/start_RL.txt"
        if os.path.exists(temp_terminate_file):
            os.remove(temp_terminate_file)
def run():
        os.system('cd transfuser && ./leaderboard/scripts/run_evaluation.sh')
def run_sim():

        cmd = ['./transfuser/carla/CarlaUE4.sh' ]
        run_carla(cmd)
        print("Simulator runnning")
def run_single_scenario(actions,logger):
        remove_unnecessary_files()
        for proc in psutil.process_iter():
            try:
                if "carla".lower() in proc.name().lower():
                    proc.kill()
                if "run_evaluation".lower() in proc.name().lower():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        os.system("sudo kill -9 `sudo lsof -t -i:2000`")
        os.system("sudo kill -9 `sudo lsof -t -i:8000`")

        p_sim = multiprocessing.Process(target=run_sim(), name="run_sim")
        p_sim.start()
        time.sleep(5)

        p = multiprocessing.Process(target=run, name="run")
        p.start()
        time.sleep(10)
        countwaiting = 0
        temp_terminate_file = abs_path+"RL-comps/start_RL.txt"
        while not os.path.exists(temp_terminate_file):
            print('waiting for transfuser to run')
            time.sleep(1)
            countwaiting = countwaiting +1
            if countwaiting>120:
                run_single_scenario(actions)
                return

        indx =0
        for action in actions:
            print("action:" +str(action) + " count:"+str(indx))
            indx = indx+1

            rwa = abs_path+'RL-comps/reward.txt'
            if os.path.exists(rwa):
                os.remove(rwa)

            action_file = open(abs_path+'RL-comps/action.txt', "w")
            action_file.write(str(action))
            action_file.close()
            if terminate(logger):
                break
            while not os.path.exists(rwa):
                time.sleep(0.01)
                if terminate(logger):
                    return
            #            i = 1 #busy waiting

            time.sleep(0.01)


