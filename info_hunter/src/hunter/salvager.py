#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from scheduler.sched_status import WLEnum 
import redis
import asyncio

class Salvager:

    def __init__(self, table_name = 'news_content') :
        self.table_name = table_name
        self.redis = redis.Redis(host = 'localhost', port = 6379, decode_responses = True, password = "lemonHUHUHE")

    def salvage(self, content) :
        try :
            self.redis.sadd(self.table_name, content)
        except :
            return WLEnum.WL_SALVAGE_FAIL
        else :
            return WLEnum.WL_SALVAGE_SUCC

    def rem_repeat(self) :
        hub = set()

        #for item in self.redis.hscan_iter("news") :
        #    v = eval(item[1])
        #    if v['Title'] in hub :
        #        self.redis.hdel("news", int(item[0]))
        #        print('###[FIND REPEAT]### %s' % v['Title'])
        #    else :
        #        hub.add(v['Title'])

        for i in self.redis.sscan_iter(self.table_name) :
            d = eval(i)
            if d['Title'] not in hub :
                hub.add(d['Title'])
                news_id = self.redis.incr("news_id_count", amount=1)
                self.redis.hset("news", news_id, d)
            self.redis.srem(self.table_name, d)

        print("Now news count is ", len(hub))


