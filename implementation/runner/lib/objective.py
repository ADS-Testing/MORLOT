from qtable import QTable

class Objective:
    def __init__(self, objective_number,action_no, learning_rate=0.01, reward_decay=0.9, e_greedy=0.1):
        self.obj_no = objective_number
        self.qtable = QTable(action_no)
        self.reward = -1
        self.is_satif = False

    def get_obj_no(self):
        return self.obj_no
    def get_action (self, observation,epsilon):
        return self.qtable.choose_action(observation,epsilon)
    def set_reward(self,reward):
        self.reward = reward
    def learn_q_table(self,state, action, reward, next_state):
        self.qtable.learn(str(state), action, reward, str(next_state))
    def is_satisfied (self):
        return self.is_satif
    def set_satisfied(self):
        self.is_satif = True