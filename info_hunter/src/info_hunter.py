#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scheduler.sched_workload import Scheduler, Workload

def workload(url):
    wl = Workload(url)
    wl.run()
    return wl.stat

class InfoHunter:

    def __init__(self, urls_path):
        self.sched = Scheduler()
        self.urls_path = urls_path

    def start_url_add(self):
        with open(self.urls_path, 'r') as f :
            for url in f.readlines() :
                url = url.strip()
                if url == '' :
                    continue
                self.sched.submit_workload(workload, url)

    def run(self):
        self.sched.start()
        self.start_url_add()
        self.sched.stop(600)

