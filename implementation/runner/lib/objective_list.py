from qtable import QTable


class Objective_list:
    def __init__(self):
        self.uncovered_objective_list = []
        self.covered_objective_list = []
    def number_of_objs(self):
        return len (self.uncovered_objective_list)+ len(self.covered_objective_list)

    def get_uncovered_objective_list(self):
        return self.uncovered_objective_list

    def remove_from_uncovered(self, indx):
        obj_to_remove = None
        for obj in self.uncovered_objective_list:
            if obj.obj_no == indx:
                obj_to_remove = obj
                break
        if obj_to_remove is not None:
            if obj in self.uncovered_objective_list:
                self.uncovered_objective_list.remove(obj)
            if obj not in self.covered_objective_list:
                self.covered_objective_list.append(obj)

    def get_covered_objective_list(self):
        return self.covered_objective_list

    def add_to_list(self, obj):
        self.uncovered_objective_list.append(obj)

    def get_all_uncovered(self):
        uncovered = []
        for u in self.uncovered_objective_list:
            uncovered.append(u.obj_no)
        return uncovered

    def add_to_covered(self, obj_no):
        for u in self.uncovered_objective_list:
            if u.obj_no == obj_no:
                self.covered_objective_list.append(u)
                self.uncovered_objective_list.remove(u)

    def choose_action(self, q_table_no, observation,epsilon):
        for u in self.uncovered_objective_list:
            if u.get_obj_no() == q_table_no:
                return u.get_action(observation,epsilon)

    def learn(self, state, action, reward, next_state):
        for u in self.uncovered_objective_list:
            u.learn_q_table(state, action, reward[u.get_obj_no()], next_state)
        for o in self.covered_objective_list:
            o.learn_q_table(state, action, reward[o.get_obj_no()], next_state)
