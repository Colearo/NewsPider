#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import traceback
import time
import asyncio

load_more_xpath = '//div[contains(@class, \'loader-bd\') or contains(@class, \'load-more\') or @class=\'more\']'

class Drivertool:
    def __init__(self, is_headless = False):
        options = webdriver.ChromeOptions()
        if is_headless is True :
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options = options)

    def load_full(self, url, scroll_times = 7):
        try :
            self.driver.get(url)
        except Exception as exc :
            traceback.print_exc()
            return None
        else :
            time.sleep(3)
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
            self.driver.quit()
            return text

