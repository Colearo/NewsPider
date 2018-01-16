#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import time

load_more_xpath = '//div[contains(@class, \'loader-bd\') or contains(@class, \'load-more\')]'

class drivertool:
    def __init__(self, site_url, is_headless = False):
        self.url = site_url
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        if is_headless is True :
            self.driver = webdriver.Chrome(chrome_options = options)
        elif is_headless is False :
            self.driver = webdriver.Chrome()
        else :
            print('Parameter false, please check the doc.')

    def load_full(self, scroll_times = 7):
        self.driver.get(self.url)
        time.sleep(1)
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
            time.sleep(1)
        text = self.driver.page_source
        self.driver.quit()
        return text

