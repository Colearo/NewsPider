#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sched
import time
import datetime
import os
from info_hunter import InfoHunter
from multiprocessing import Process

def main_hunter():
    sites_path = os.path.join(os.path.dirname(__file__), './resource/news_url')
    hunter = InfoHunter(sites_path)
    hunter.run()

def sched_hunter():
    _process = Process(target = main_hunter, args = ())
    _process.start()
    _process.join()
    _process.terminate()
    today = datetime.datetime.today()
    today = today.strftime('%Y/%m/%d %H:%M')
    print('[%s]' % today)

if __name__ == '__main__' :
    sched_hunter()
