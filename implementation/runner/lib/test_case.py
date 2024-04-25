

class Test_Case:
    def __init__(self):
        self.tc = []
        self.max_reward = -1
    def update(self,set):
        self.tc.append(set)
    def update_reward(self,rev):
        self.max_reward = rev;
    def get_reward(self):
        return self.max_reward