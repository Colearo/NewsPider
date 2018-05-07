#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime
import mysql.connector
import redis

DB_NAME = 'db_news'
cnx = mysql.connector.connect(user = 'root', password = 'lemon', database = DB_NAME)
cursor = cnx.cursor()
r = redis.Redis(host = 'localhost', port = 6379, decode_responses = True, password = "lemonHUHUHE")

insert_new_news = (
        "INSERT IGNORE INTO news "
        "(news_title, news_date, news_content, news_source, news_link)"
        "VALUES (%s, %s, %s, %s, %s)"
        )

for i in r.sscan_iter("news_content") :
    d = eval(i)
    content = d.get('Content')
    if content is None or content.strip() == '':
        continue
    date = d.get('Date')
    if date is None :
        continue
    date = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M')
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    d_tuple = (d.get('Title'), date, content, d.get('Source'), d.get('Link')) 
    try :
        print('Insert news %s ' % d.get('Title'), end = '')
        cursor.execute(insert_new_news, d_tuple)
        cnx.commit()
    except mysql.connector.Error as err :
        print(err.msg)
    except Exception as e :
        print(e, '[', d.get('Link'), ']')
        cnx.rollback()
    else :
        print('OK')

cursor.close()
cnx.close()

