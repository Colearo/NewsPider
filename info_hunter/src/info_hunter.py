#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import time
import random
import sys
import asyncio
import sched
from queue import Queue
from scheduler.sched_workload import Scheduler, Workload
from concurrent.futures import ThreadPoolExecutor 

def workload(url, service_url):
    wl = Workload(url, service_url)
    wl.run()
    return wl.stat

class InfoHunter:

    def __init__(self, urls_path):
        self.sched = Scheduler()
        self.urls_path = urls_path
        self.new_urls = Queue()
        self.quit = False
        self.timer = sched.scheduler(time.time, time.sleep)
        self.wait_event = None
        self.run_event = None

    def start_url_add(self):
        with open(self.urls_path, 'r') as f :
            for url in f.readlines() :
                url = url.strip()
                if url == '' :
                    continue
                self.sched.submit_workload(workload, url, 
                        self.sched.service_url)

    def run(self):
        if self.wait_event is not None :
            self.timer.cancel(self.wait_event)
        self.sched.start()
        self.start_url_add()
        self.sched.stop()
        self.timer.enter(200, 1, self.run)
        self.wait()
        self.timer.run()

    def wait(self):
        self.sched.wait()
        self.timer.enter(1, 2, self.wait)
        
sites_path = os.path.join(os.path.dirname(__file__), './resource/news_url')
hunter = InfoHunter(sites_path)
hunter.run()

