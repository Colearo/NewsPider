#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import time
import random
import sys
import asyncio
from queue import Queue
from scheduler.sched_workload import Scheduler, Workload
from concurrent.futures import ThreadPoolExecutor 

def workload(url, status):
    wl = Workload(url)
    wl.run(status)

class InfoHunter:

    def __init__(self, urls_path):
        self.sched = Scheduler()
        self.urls_path = urls_path
        self.new_urls = Queue()
        self.quit = False

    def start_url_add(self):
        with open(self.urls_path, 'r') as f :
            for url in f.readlines() :
                url = url.strip()
                if url == '' :
                    continue
                self.sched.submit_workload(workload, url, self.sched.status)

    def run(self):
        self.sched.start()
        self.start_url_add()
        self.sched.stop()
        
sites_path = os.path.join(os.path.dirname(__file__), './resource/news_url')
hunter = InfoHunter(sites_path)
hunter.run()

