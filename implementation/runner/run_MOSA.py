import sys
import multiprocessing


sys.path.append('lib/')
import subprocess

from datetime import datetime
import sys
import time
#
import glob
import os
from mosa import *
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
        log_file = 'output/MOSA/' + str(now) + '_transfuser.log'
        logging.basicConfig(filename=log_file,
                            format='%(asctime)s %(message)s')

        logger.setLevel(logging.DEBUG)
        logger.info("Started")
        self.indx = 0


    def _evaluate(self,x):

        run_single_scenario(x)

        extra, DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max = get_values(
            abs_path+"RL-comps/all-data.txt")
        #
        self.indx = self.indx + 1

        logger = logging.getLogger()
        logger.info(
            str(extra) + "$" + str(self.indx) + '#' + str(DfC_min) + ',' + str(DfV_max) + ',' + str(DfP_max) + ','
            + str(DfM_max) + ',' + str(DT_max) + ',' + str(traffic_lights_max))

        #
        # return [DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max]
        fo  = open (abs_path+"temp/"+str(self.indx)+'mosa'+str(datetime.now())+'.txt','w')
        fo.write(str(x))
        fo.close()
        return [DfC_min, DfV_max, DfP_max, DfM_max, DT_max, traffic_lights_max]


def run(i,archive):
    size = 6
    lb = [0]*2500
    ub = [17]*2500

    threshold_criteria = [0,0,0,0,0.95,0]

    time_budget = 7200  # second
    no_of_Objectives = 6;


    now = datetime.now()
    global logger
    logger = logging.getLogger()
    log_file = 'output/MOSA/' + str(now) + '_transfuser.log'
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s %(message)s')

    logger.setLevel(logging.DEBUG)

    archive = minimize(caseStudy()._evaluate, size, lb, ub, no_of_Objectives, threshold_criteria, time_budget, logger,archive)
    logger.info("Iteration completed")


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
