#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait

class WLEnum(Enum) :
    WL_RUNNING = 'wl_running'
    WL_COMPLETED = 'wl_completed'

    WL_SALVAGE = 'wl_salvage'
    WL_SALVAGE_SUCC = 'wl_salvage_succ'
    WL_SALVAGE_FAIL = 'wl_salvage_fail'

    WL_SUMMON = 'wl_summon'
    WL_SUMMON_SUCC = 'wl_summon_succ'
    WL_SUMMON_FAIL = 'wl_summon_fail'

    WL_PURIFY = 'wl_purify'
    WL_PURIFY_SUCC = 'wl_purify_succ'
    WL_PURIFY_FAIL = 'wl_purify_fail'

class Workload:
    def __init__(self, scheduler) :
        self.scheduler = scheduler

    def submit(self) :
        return NotImplementedError

    def finish(self) :
        return NotImplementedError

class Scheduler:
    def __init__(self) :
        self.thread_pool = ThreadPoolExecutor()
        self.process_pool = ProcessPoolExecutor()
        self.future_list = []
        self.finished_list = []
        self.summon_list = []
        self.purify_list = []
        self.salvage_list = []
        self.start_t = 0
        self.end_t = 0

    def start(self) :
        self.start_t = time.time()
        print('Scheduler starts running')

    def stop(self) :
        self.thread_pool.shutdown(True)
        self.process_pool.shutdown(True)
        self.end_t = time.time()
        print('Scheduler runs %0.2f seconds' % (self.end_t - self.start_t))


    def submit_workload(self, func, flag) :
        if flag is WLEnum.WL_SUMMON or flag is WLEnum.WL_SALVAGE :
            future = self.thread_pool.submit(func)
            self.future_list.append(future)
        elif flag is WLEnum.WL_PURIFY :
            future = self.process_pool.submit(func)
            self.future_list.append(future)

    def update_workload_status(self, when = 'FIRST_COMPLETED') :
            (done, notdone) = wait(self.future_list, return_when = when)
            self.future_list = list(notdone)
            for future in done :
                try:
                    flag, data = future.result()
                except Exception as exc:
                    print('Generated an exception: %s' %  exc)
                else:
                    if flag is WLEnum.WL_SUMMON :
                        self.summon_list.append(data)
                    elif flag is WLEnum.WL_PURIFY :
                        self.purify_list.append(data)
                    elif flag is WLEnum.WL_SALVAGE :
                        self.salvage_list.append(data)
                    self.finished_list.append(future)









