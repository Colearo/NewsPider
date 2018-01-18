#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import http.cookiejar
from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .sched_workload import Workload, WLEnum
from crawler_util.selenium_tool import drivertool 

class Summoner(Workload):
    def __init__(self, scheduler, url, is_start_url = False) :
        Workload.__init__(self, scheduler)
        self.url = url
        self.is_start_url = is_start_url
        if is_start_url is True :
            self.web_driver = drivertool(self.url, True)
        else :
            self.cookie_name = 'cookie.txt'
            self.cookie = http.cookiejar.MozillaCookieJar(self.cookie_name)
            self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
            self.opener = urllib.request.build_opener(self.handler)
            self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]

    def summon_page(self) : 
        try :
            response = self.opener.open(self.url)
            is_charset_gb = self.extractor.is_charset_gb(response)
            if is_charset_gb is True :
                soup = BeautifulSoup(response, "html.parser", 
                    from_encoding = 'gb18030')
            else :
                soup = BeautifulSoup(response, "html.parser")
        except :
            print('Bad link: ', self.url)
            soup = None
        return WLEnum.WL_SUMMON, (soup, self.is_start_url)

    def summon_start_page(self) :
        response = self.web_driver.load_full() 
        soup = BeautifulSoup(response, "html.parser")
        return WLEnum.WL_SUMMON, (soup, self.is_start_url)

    def submit(self) :
        if self.is_start_url is True:
            self.scheduler.submit_workload(self.summon_start_page, WLEnum.WL_SUMMON)
        else :
            self.scheduler.submit_workload(self.summon_page, WLEnum.WL_SUMMON)



