#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Semaphore
from hunter.summoner import Summoner
from hunter.purifier import Purifier
from hunter.salvager import Salvager
from .sched_status import WLEnum

t_sem = Semaphore(2)

class Workload:

    def __init__(self, start_url) :
        self.start_url = start_url
        self.summoner = Summoner()
        self.purifier = Purifier(start_url)
        self.salvager = Salvager()
        self.stat = dict({
                WLEnum.WL_SUMMON : 0,
                WLEnum.WL_SUMMON_SUCC : 0,
                WLEnum.WL_SUMMON_FAIL : 0,
                WLEnum.WL_PURIFY : 0,
                WLEnum.WL_PURIFY_SUCC : 0,
                WLEnum.WL_PURIFY_FAIL : 0,
                WLEnum.WL_SALVAGE : 0,
                WLEnum.WL_SALVAGE_SUCC : 0,
                WLEnum.WL_SALVAGE_FAIL : 0
                })

    def task_info_hunter(self):
        t_sem.acquire()
        status, response = self.summoner.summon(self.start_url, False)
        t_sem.release()
        self.stat[status] += 1
        if status is WLEnum.WL_SUMMON_FAIL :
            return
        status, links = self.purifier.purify(response, False)
        self.stat[status] += 1
        if status is WLEnum.WL_PURIFY_FAIL :
            return 
        for link in links :
            status, response = self.summoner.summon(link, True)
            self.stat[status] += 1
            if status is WLEnum.WL_SUMMON_FAIL :
                continue
            status, content = self.purifier.purify(response, True)
            self.stat[status] += 1
            if status is WLEnum.WL_PURIFY_FAIL :
                continue
            content['Link'] = link
            status = self.salvager.salvage(content)
            self.stat[status] += 1
            print(content)

    def run(self):
        # oldloop = asyncio.get_event_loop()
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # try :
            # loop.run_until_complete(self.task_info_hunter())
        # except Exception:
            # traceback.print_exc()
        # finally:
            # loop.close()
            # asyncio.set_event_loop(oldloop)
        self.task_info_hunter()

class Scheduler:
    def __init__(self) :
        self.future_list = set()
        self.start_t = 0
        self.end_t = 0
        self.status = dict({
                WLEnum.WL_SUMMON : 0,
                WLEnum.WL_SUMMON_SUCC : 0,
                WLEnum.WL_SUMMON_FAIL : 0,
                WLEnum.WL_PURIFY : 0,
                WLEnum.WL_PURIFY_SUCC : 0,
                WLEnum.WL_PURIFY_FAIL : 0,
                WLEnum.WL_SALVAGE : 0,
                WLEnum.WL_SALVAGE_SUCC : 0,
                WLEnum.WL_SALVAGE_FAIL : 0
                })
        self.thread_pool = ThreadPoolExecutor(max_workers = 10)

    def start(self) :
        self.start_t = time.time()
        print(' ')
        print('***********************')
        print('Scheduler starts running')

    def stop(self, timeout) :
        self.update_workload_status(time = timeout)
        print(self.status)
        self.end_t = time.time()
        print('Scheduler runs %0.2f seconds' % (self.end_t - self.start_t))

    def submit_workload(self, func, *args) :
        future = self.thread_pool.submit(func, *args)
        self.future_list.add(future)

    def update_workload_status(self, when = 'ALL_COMPLETED', 
            time = None) :
            (done, notdone) = wait(self.future_list, timeout = time, 
                    return_when = when)
            for future in notdone:
                future.cancel()

            for future in done :
                try:
                    stat = future.result()
                except Exception:
                    traceback.print_exc()
                else:
                    if stat is not None :
                        for enum in WLEnum :
                            self.status[enum] += stat[enum]

