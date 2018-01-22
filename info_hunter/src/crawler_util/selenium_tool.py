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
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        if is_headless is True :
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')

    def load_full(self, url, scroll_times = 7):
        driver = webdriver.Chrome(chrome_options = self.options)
        try :
            driver.get(url)
        except Exception as exc :
            traceback.print_exc()
            return None
        else :
            time.sleep(3)
            last_height = 0
            for i in range(scroll_times):
                driver.execute_script('window.scrollTo'
                '(0,document.body.scrollHeight)')
                height = driver.execute_script(
                'var s=document.body.scrollHeight;return(s)')
                if int(height) > last_height :
                    print(height)
                    last_height = int(height)
                else :
                    try :
                        more = driver.find_element_by_xpath(
                                load_more_xpath)
                        more.click()
                        print('!!!Click more')
                    except :
                        print('Now has been to bottom')
                        break
                time.sleep(0.1)
            text = driver.page_source
            driver.quit()
            return text

