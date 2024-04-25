import sys
import multiprocessing
import glob
import os
sys.path.append('lib/')
from morlot import MORLoT
import logging
from datetime import datetime
import time


def run():
    number_of_actions = list(range(17))
    print(number_of_actions)
    morlot = MORLOT(6,number_of_actions)
    morlot.run(2500,[100000, 100000, 100000, 100000, 100000, 100000])

if __name__ == "__main__":
    #
    print("in main")
    times_of_repetitions = 4

    for i in range(0, times_of_repetitions):
        manager = multiprocessing.Manager()
        archive = manager.list()
        p = multiprocessing.Process(target=run, name="run")
        p.start()
        for t in range(240):
            if p.is_alive():
                time.sleep(60)
            else:
                break
        p.terminate()
        # Cleanup
        p.join()
