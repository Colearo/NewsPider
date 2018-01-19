#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import asyncio

load_more_xpath = '//div[contains(@class, \'loader-bd\') or contains(@class, \'load-more\') or @class=\'more\']'

class Drivertool:
    def __init__(self, is_headless = False):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        if is_headless is True :
            self.driver = webdriver.Chrome(chrome_options = options)
        elif is_headless is False :
            self.driver = webdriver.Chrome()
        else :
            print('Parameter false, please check the doc.')

    def load_full(self, url, scroll_times = 7):
        self.driver.get(url)
        self.driver.implicitly_wait(1)
        last_height = 0
        for i in range(scroll_times):
            self.driver.execute_script('window.scrollTo'
            '(0,document.body.scrollHeight)')
            height = self.driver.execute_script(
            'var s=document.body.scrollHeight;return(s)')
            if int(height) > last_height :
                print(height)
                last_height = int(height)
            else :
                try :
                    more = self.driver.find_element_by_xpath(
                            load_more_xpath)
                    more.click()
                    print('!!!Click more')
                except :
                    print('Now has been to bottom')
                    break
            asyncio.sleep(0.1)
        text = self.driver.page_source
        self.driver.close()
        return text

