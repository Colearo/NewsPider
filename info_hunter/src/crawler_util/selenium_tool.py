#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import traceback
import time
import asyncio

load_more_xpath = '//div[contains(@class, \'loader-bd\') or contains(@class, \'load-more\') or @class=\'more\']'

class Drivertool:
    def __init__(self, service_url, is_headless = False):
        self.options = webdriver.ChromeOptions()
        if is_headless is True :
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')
        self.service_url = service_url

    def load_full(self, url, scroll_times = 7):
        self.driver = webdriver.Remote(self.service_url, 
                self.options.to_capabilities())
        try :
            self.driver.get(url)
        except Exception as exc :
            traceback.print_exc()
            return None
        else :
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
                time.sleep(0.1)
        text = self.driver.page_source
        self.driver.quit()
        return text

