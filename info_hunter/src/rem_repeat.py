#! /usr/bin/env python3 

import redis
r = redis.Redis(host = 'localhost', port = 6379, decode_responses = True)
hub = set()

for i in r.sscan_iter('news_content') :
    d = eval(i)
    if d['Title'] not in hub :
        hub.add(d['Title'])
        print(d['Title'])
    else :
        r.srem('news_content', d)

print(len(hub))
