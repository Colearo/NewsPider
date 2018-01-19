#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import http.cookiejar
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from scheduler.sched_status import WLEnum 
from crawler_util.selenium_tool import Drivertool 

class Summoner:

    def __init__(self) :
        self.web_driver = Drivertool(True)
        self.cookie_name = 'cookie.txt'
        self.cookie = http.cookiejar.MozillaCookieJar(self.cookie_name)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]

    async def summon_page(self, url) : 
        try :
            response = self.opener.open(url)
        except Exception as exc:
            print('Bad link: %s | %s' % (url, exc))
            return WLEnum.WL_SUMMON_FAIL, None
        else :
            print('Open link: ', url)
            return WLEnum.WL_SUMMON_SUCC, response

    async def summon_start_page(self, url) :
        response = self.web_driver.load_full(url) 
        if response is None :
            return WLEnum.WL_SUMMON_FAIL, None
        else :
            return WLEnum.WL_SUMMON_SUCC, response

    async def summon(self, url, is_content_page) :
        if is_content_page is True:
            return await self.summon_page(url)
        else :
            return await self.summon_start_page(url)


