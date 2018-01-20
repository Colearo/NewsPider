#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from scheduler.sched_status import WLEnum 
import redis
import asyncio

class Salvager:

    def __init__(self, table_name = 'news_content') :
        self.table_name = table_name
        self.redis = redis.Redis(host = 'localhost', port = 6379, 
                decode_responses = True)

    async def salvage(self, content) :
        self.redis.sadd(self.table_name, content)

