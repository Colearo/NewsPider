#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from scheduler.sched_status import WLEnum 
import mysql.connector
import redis
import datetime

insert_new_news = (
        "INSERT IGNORE INTO news "
        "(news_title, news_date, news_content, news_source, news_link)"
        "VALUES (%s, %s, %s, %s, %s)"
        )

class Salvager:

    def __init__(self, table_name = 'news_content') :
        self.table_name = table_name
        self.redis = redis.Redis(host = 'localhost', port = 6379, decode_responses = True, password = "lemonHUHUHE")
        DB_NAME = 'db_news'
        self.cnx = mysql.connector.connect(user = 'root', password = 'lemon', database = DB_NAME)
        self.cursor = self.cnx.cursor()

    def salvage(self, d) :
        content = d.get('Content')
        if content is None or content.strip() == '':
            return WLEnum.WL_SALVAGE_FAIL
        date = d.get('Date')
        if date is None :
            return WLEnum.WL_SALVAGE_FAIL
        date = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M')
        date = date.strftime('%Y-%m-%d %H:%M:%S')
        d_tuple = (d.get('Title'), date, content, d.get('Source'), d.get('Link')) 
        try :
            print('Insert news %s' % d.get('Title'), end = '')
            self.cursor.execute(insert_new_news, d_tuple)
            self.cnx.commit()
        except mysql.connector.Error as err :
            print(err.msg)
            return WLEnum.WL_SALVAGE_FAIL
        except Exception as e :
            print(e, '[', d.get('Link'), ']')
            self.cnx.rollback()
            return WLEnum.WL_SALVAGE_FAIL
        else :
            print('OK')
            return WLEnum.WL_SALVAGE_SUCC

    def stop(self) :
        self.cursor.close()
        self.cnx.close()

    def rem_repeat(self) :
        pass

