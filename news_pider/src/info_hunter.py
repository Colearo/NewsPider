#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import time
import random
import sys
from scheduler.sched_workload import Scheduler, WLEnum 
from scheduler.sched_summoner import Summoner 

class InfoHunter:

    def __init__(self, urls_path):
        self.sched = Scheduler()
        self.urls_path = urls_path

    def url_summon(self):
        with open(self.urls_path, 'r') as f :
            for url in f.readlines() :
                url = url.strip()
                if not url :
                    continue
                summoner = Summoner(self.sched, url, True)
                summoner.submit()

    def run(self):
        self.sched.start()
        self.url_summon()
        while True :
            self.sched.update_workload_status()
            if len(self.sched.summon_list) == 0 :
                break
            (soup, flag) = self.sched.summon_list.pop()
            print(soup.head.title)
        self.sched.stop()
        

sites_path = os.path.join(os.path.dirname(__file__), './resource/news_url')
hunter = InfoHunter(sites_path)
hunter.run()

