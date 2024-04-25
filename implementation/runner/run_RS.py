import sys
import multiprocessing


sys.path.append('lib/')
import subprocess

from datetime import datetime
import os
import time
#
import random
import glob
from data_handler import get_values
import logging
from common import run_single_scenario
from config import abs_path
#
# logger = None;

class caseStudy():
    def __init__(self):
        logger = logging.getLogger()

        now = datetime.now()
        log_file = 'output/RS/' + str(now) + '_transfuser.log'
        logging.basicConfig(filename=log_file,
                            format='%(asctime)s %(message)s')

        logger.setLevel(logging.DEBUG)
        logger.info("Started")
        self.indx = 0


    def _evaluate(self,x):
        logger = logging.getLogger()
        run_single_scenario(x,logger)
        extra,DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max = get_values(
            abs_path+"RL-comps/all-data.txt")
        self.indx = self.indx+1
        logger.info(str(extra)+"$"+str(self.indx)+'#'+ str(DfC_min)+ ','+str( DfV_max)+','+str(DfP_max)+ ','
                    +str(DfM_max)+ ','+str( DT_max) +','+ str(traffic_lights_max))
        fo  = open (abs_path+"temp/"+str(self.indx)+'RS'+str(datetime.now())+'.txt','w')
        fo.write(str(x))
        fo.close()
        return [DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max]


def run(i,archive):
    cs = caseStudy()

    while True:
        actions =[]
        for i in range (2500):
            actions.append(random.randint(0,16))
        DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max = cs._evaluate(actions)

if __name__ == "__main__":
    #
    print("in main")
    times_of_repetitions = 10
    for i in range(0, times_of_repetitions):
        manager = multiprocessing.Manager()
        archive = manager.list()
        p = multiprocessing.Process(target=run, name="run", args=(i,archive,))

        p.start()

        for t in range(240):

            if p.is_alive():
                time.sleep(60)
            else:
                break

        p.terminate()

        # Cleanup
        p.join()
