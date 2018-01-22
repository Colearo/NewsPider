#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sched
import time
import os
from info_hunter import InfoHunter
from multiprocessing import Process

timer = sched.scheduler(time.time, time.sleep)

def wait_hunter(end_t, wait_t):
        now = time.time()
        duration = now - end_t
        if duration > wait_t :
            return
        mins = int(duration/60)
        secs = int(duration)
        if secs != 0 and secs == mins * 60 :
            secs = 0
        else :
            secs = secs - mins * 60
        print('\rScheduler wait [%d min %d sec]' % (mins, secs), end = '')
        timer.enter(1, 2, wait_hunter, (end_t, wait_t))

def main_hunter():
    sites_path = os.path.join(os.path.dirname(__file__), './resource/news_url')
    hunter = InfoHunter(sites_path)
    hunter.run()

def sched_hunter(wait_t):
    _process = Process(target = main_hunter, args = ())
    _process.start()
    _process.join()
    _process.terminate()
    wait_hunter(time.time(), wait_t)
    timer.enter(wait_t, 1, sched_hunter, (wait_t, ))
    timer.run()
 
sched_hunter(1200)
