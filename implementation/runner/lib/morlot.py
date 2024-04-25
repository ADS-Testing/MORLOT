import copy
import os.path
import random
import numpy as np
import pandas as pd

from objective import Objective
from objective_list import Objective_list
from environment import Environment
from archive import Archive
from data_handler import check_valid
from test_case import Test_Case
import logging
from datetime import datetime
import time
from config import abs_path
import math

class MORLAT:
    def __init__(self, objectives, actions):
        self.obj_list = Objective_list()
        self.env = Environment()
        self.actions = actions
        self.archive = Archive()
        self.epsilon = 1
        self.action_count = 0
        self.total_objs = objectives
        for i in range(objectives):
            self.obj_list.add_to_list(Objective(i, actions))

    def get_obj_list(self):
        return self.obj_list

    def get_env(self):
        return self.env

    def get_actions(self):
        return self.actions

    def get_archive(self):
        return self.archive

    def choose_action(self, observation, rewards):
        self.action_count = self.action_count+1


        print("Epsilon: "+str(self.epsilon))

        if not rewards:
            return random.randint(0, len(self.actions)-1)
        uncovered_list = self.obj_list.get_all_uncovered()
        rewards_of_interests = []
        for i in range(len(rewards)):
            if i in uncovered_list:
                rewards_of_interests.append(rewards[i])
        max_index = rewards_of_interests.index(max(rewards_of_interests))
        q_table_index = uncovered_list[max_index]



        return self.obj_list.choose_action(q_table_index, observation,self.epsilon)

    def learn(self, state, action, reward, next_state):
        self.obj_list.learn(state, action, reward, next_state)

    def write_file(self, fn):
        file = open(abs_path+'RL-comps/' + fn + ".txt", 'w')
        file.write("aaa")
        file.close()

    def terminate(self):
        check_file = abs_path+"RL-comps/terminate.txt"
        if os.path.exists(check_file):
            return True
        return False

    def remove_unnecessary_files(self):
        temp_terminate_file = abs_path+"RL-comps/terminate.txt"
        if os.path.exists(temp_terminate_file):
            os.remove(temp_terminate_file)
        temp_terminate_file = abs_path+"RL-comps/start_RL.txt"
        if os.path.exists(temp_terminate_file):
            os.remove(temp_terminate_file)

    def get_logger(self):
        logger = logging.getLogger()

        now = datetime.now()
        log_file = 'output/MORLAT/' + str(now) + '_transfuser.log'
        logging.basicConfig(filename=log_file,
                            format='%(asctime)s %(message)s')

        logger.setLevel(logging.DEBUG)
        logger.info("Started")
        return logger

    def run(self, number_of_actions, obj_thresholds):
        budget_finished = False
        start_time = time.time()
        end_time = None
        while not budget_finished:
            if end_time is None:
                self.epsilon = 1
            else:
                time_in_minutes = (end_time - start_time)/60
                print(time_in_minutes)
                if time_in_minutes >= 48: #20 % of 240 minutes
                    self.epsilon = 0.1
                else:
                    self.epsilon = (54 - time_in_minutes)/54
            if self.epsilon <= 0.1:
                self.epsilon = 0.1
            tc = Test_Case()
            s = None
            a = None
            rewards = []
            self.remove_unnecessary_files()
            self.env.reset()
            actions_taken = 0
            stopping_condition = False

            logger = self.get_logger()

            while not stopping_condition and not self.terminate():
                s = self.env.observe()
                a = self.choose_action(s, rewards)
                rewards, next_state = self.env.perform(a)
                logger.info(str(s) + "#" + str(a) + "#" + str(rewards))
                self.obj_list.learn(s, a, rewards, next_state)
                tc.update([s, a])
                actions_taken = actions_taken + 1
                if actions_taken > number_of_actions:
                    stopping_condition = True
                print("Action: " + str(a) + " Total Count: " + str(actions_taken))
                for index in range(self.total_objs):
                    if rewards[index] > obj_thresholds[index]:
                        self.obj_list.remove_from_uncovered(index)
                        if tc.get_reward() > -1:  # one test case satisfying multiple objectives
                            tc = copy.deepcopy(tc)
                        tc.update_reward(rewards[index])
                        self.archive.update(tc, index)
            if rewards[4] > 0.05:
                if check_valid():
                    self.obj_list.remove_from_uncovered(4)
                    rewards[4] = 1000000
                    tc.update_reward(rewards[4])
                    self.archive.update(tc, 4)
                    logger.info(str(s) + "#" + str(a) + "#" + str(rewards))
            end_time = time.time()
