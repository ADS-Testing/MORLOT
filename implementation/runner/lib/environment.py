from qtable import QTable
import subprocess
import time
import os
import sys
import psutil
import multiprocessing
from config import abs_path

class Environment:
    def run_command(self, cmd):
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True, shell=True)

    def run(self):
        os.system('cd transfuser && ./leaderboard/scripts/run_evaluation.sh')

    def run_sim(self):
        cmd = ['./transfuser/carla/CarlaUE4.sh']
        self.run_command(cmd)
        print("Simulator runnning")
        # os.system('./transfuser/carla/CarlaUE4.sh')

    def reset(self):
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

        p_sim = multiprocessing.Process(target=self.run_sim(), name="run_sim")
        p_sim.start()
        time.sleep(5)

        p = multiprocessing.Process(target=self.run, name="run")
        p.start()
        time.sleep(10)

        temp_terminate_file = abs_path+"RL-comps/start_RL.txt"
        countwaiting = 0
        while not os.path.exists(temp_terminate_file):
            print('waiting for transfuser to run')
            time.sleep(1)
            countwaiting = countwaiting + 1
            if countwaiting > 120:
                self.reset()
                return

    def observe(self):
        while not os.path.exists('RL-comps/reward.txt'):
            time.sleep(0.001)

        state = open('RL-comps/reward.txt').read().split("#")[1]

        state = [float(x) for x in state.split(",")]
        return state

    def perform(self, action):
        rwa = abs_path+'RL-comps/reward.txt'
        if os.path.exists(rwa):
            os.remove(rwa)

        action_file = open(abs_path+'RL-comps/action.txt', "w")
        action_file.write(str(action))
        action_file.close()

        while not os.path.exists(rwa):
            time.sleep(0.01)
        time.sleep(0.01)
        reward_content_parts = open(rwa, "r").read().split("#")
        reward_content = reward_content_parts[0]
        rewards = [float(x) for x in reward_content.split(',')]


        reward_0 = 0
        reward_1 = 0
        reward_2 = 0
        reward_3 = 0
        reward_4 = 0
        reward_5 = 0


        if rewards[0] <= 0:
            reward_0 = 1000000
        if rewards[1] <= 0:
            reward_1 = 1000000
        if rewards[2] <= 0:
            reward_2 = 1000000
        if rewards[3] <= 0:
            reward_3 = 1000000

        if rewards[5] == 0:
            reward_5 = 1000000

        if reward_0 != 1000000:
            reward_0 = 1 / rewards[0]

        if reward_1 != 1000000:
            reward_1 = 1 / rewards[1]

        if reward_2 != 1000000:
            reward_2 = 1 / rewards[2]

        if reward_3 != 1000000:
            reward_3 = 1 / rewards[3]

        if reward_4 != 1000000:
            reward_4 = rewards[4]


        rewards = [reward_0, reward_1, reward_2, reward_3, reward_4, reward_5]
        state = reward_content_parts[1]
        state = [float(x) for x in state.split(",")]
        return rewards, state

        # if os.path.exists('RL-comps/reward.txt'):
        #     base_file = open('RL-comps/state.txt', "r")
