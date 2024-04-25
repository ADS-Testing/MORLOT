

class Archive:
    def __init__(self):
        self.record = dict()
    def update(self,ts,objective_no):
        if not objective_no in self.record.keys():
            self.record[objective_no] = ts
        else:
            ts_arc = self.record[objective_no]
            if ts_arc.get_reward() > ts.get_reward():
                self.record[objective_no] = ts
        print("archive updated")
