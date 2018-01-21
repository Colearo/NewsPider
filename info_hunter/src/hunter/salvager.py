#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from scheduler.sched_status import WLEnum 
import redis
import asyncio

class Salvager:

    def __init__(self, table_name = 'news_content') :
        self.table_name = table_name
        self.redis = redis.Redis(host = 'localhost', port = 6379)

    async def salvage(self, content) :
        try :
            self.redis.sadd(self.table_name, content)
        except :
            return WLEnum.WL_SALVAGE_FAIL
        else :
            return WLEnum.WL_SALVAGE_SUCC

