#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import traceback
import asyncio
import multiprocessing
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait
from hunter.summoner import Summoner
from hunter.purifier import Purifier
from .sched_status import WLEnum

class Workload:

    def __init__(self, start_url) :
        self.start_url = start_url
        self.summoner = Summoner()
        self.purifier = Purifier(start_url)

    async def task_info_hunter(self, stat):
        status, response = await self.summoner.summon(self.start_url, False)
        stat[status] += 1
        if status is WLEnum.WL_SUMMON_FAIL :
            return
        status, links = await self.purifier.purify(response, False)
        stat[status] += 1
        if status is WLEnum.WL_PURIFY_FAIL :
            return 
        for link in links :
            status, response = await self.summoner.summon(link, True)
            stat[status] += 1
            if status is WLEnum.WL_SUMMON_FAIL :
                continue
            status, content = await self.purifier.purify(response, True)
            stat[status] += 1
            if status is WLEnum.WL_PURIFY_FAIL :
                continue
            print(content)

    def run(self, status):
        oldloop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try :
            loop.run_until_complete(self.task_info_hunter(status))
        except Exception:
            traceback.print_exc()
        finally:
            loop.close()
            asyncio.set_event_loop(oldloop)

class Scheduler:
    def __init__(self) :
        self.process_pool = ProcessPoolExecutor()
        self.manager = multiprocessing.Manager()
        self.future_list = []
        self.finished_list = []
        self.status = self.manager.dict({
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
        self.start_t = 0
        self.end_t = 0

    def start(self) :
        self.start_t = time.time()
        print('Scheduler starts running')

    def stop(self) :
        self.process_pool.shutdown(True)
        print(self.status)
        self.manager.shutdown()
        self.end_t = time.time()
        print('Scheduler runs %0.2f seconds' % (self.end_t - self.start_t))

    def submit_workload(self, func, *args) :
        future = self.process_pool.submit(func, *args)
        self.future_list.append(future)

    def update_workload_status(self, when = 'FIRST_COMPLETED', 
            time = None) :
            (done, notdone) = wait(self.future_list, timeout = time, 
                    return_when = when)
            self.future_list = list(notdone)
            for future in done :
                try:
                    flag = future.result()
                except Exception:
                    traceback.print_exc()
                else:
                    self.finished_list.append(future)


