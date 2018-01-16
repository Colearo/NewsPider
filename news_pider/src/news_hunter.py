#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import http.cookiejar
import re
import os
import time
import random
import gzip
import sys
from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from multiprocessing import Pool
from crawler_util.block_extractor import extractor
from crawler_util.selenium_tool import drivertool 

class news_hunter:

    def __init__(self, site_url):
        self.start_url = site_url
        self.filename = 'cookie.txt'
        self.cookie = http.cookiejar.MozillaCookieJar(self.filename)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]
        self.extractor = extractor()
        self.web_driver = drivertool(self.start_url, True)

    def save_img(self, image_url, path_name):
        with urllib.request.urlopen(image_url) as files:
            data = files.read()
        with open(path_name, 'wb') as f:
            f.write(data)
            print('Saving one pic named ', path_name)

    def mkdir(self, path_name):
        path = path_name.strip()
        is_exist = os.path.exists(path)
        if not is_exist:
            print('Now creating', path, 'directory')
            os.makedirs(path)
            return True
        else :
            print('Path', path, 'has been created')
            return False

    def get_item_image(self, soup, path_name):
        big_pic = soup.find('div', id = 'big-pic')
        for pics in big_pic.find_all('img') :
            img_name = re_num.search(pics['alt']).group(1) + '.jpg'
            pics_path = os.path.join(path_name.strip(), img_name)
            is_exist = os.path.exists(pics_path)
            if not is_exist:
                self.save_img(pics['src'], pics_path)
            else :
                print('Pic ', pics_path, 'has been created')
            
    def get_item_content(self, soup, path_name):
        self.extractor.reset()
        content = self.extractor.get_content(soup)
        if content is not None :
            try :
                f = open(path_name.strip(), 'wb')
            except :
                pass
            else :
                for line in content:
                    if line.strip() is not '' :
                        f.write(str.encode(line.strip()) + b'\n')
            print('Saving one article named ', path_name.strip())

    def get_page_items(self, soup):
        links = self.extractor.get_valued_links(soup, 
        self.start_url.strip())
        for link in links :
            try :
                response = self.opener.open(link) 
                is_charset_gb = self.extractor.is_charset_gb(
                        response)
                if is_charset_gb is True :
                    soup = BeautifulSoup(response, "html.parser", 
                    from_encoding = 'gb18030')
                else :
                    soup = BeautifulSoup(response, "html.parser")

                title = self.extractor.get_title(soup)
                if title is None :
                    continue
                print('%s [%s]' % (title[0], link))
            except :
                print('Bad link: ', link)
                continue
            self.get_item_content(soup, title[0])
        # time.sleep(random.random() * 4 + 1)

    def get_page(self):
        # print(self.start_url)
        # with self.opener.open(self.start_url) as files :
        files = self.web_driver.load_full() 
        # self.cookie.save(ignore_discard=True, ignore_expires=True)
        soup = BeautifulSoup(files, "html.parser")
        self.get_page_items(soup)

    def get_list_page(self, page_index):
        url = self.start_url + '/channel_2595' + str(page_index)
        print(url)
        with self.opener.open(self.start_url) as files :
            self.cookie.save(ignore_discard=True, ignore_expires=True)
            soup = BeautifulSoup(files, "html.parser")
            self.get_page_items(soup)

    def get_pages(self, start, end):
        for i in range(start, end + 1):
            print("NOW IN CHANNEL[%d]" % i)
            self.get_list_page(i)
            time.sleep(40)

def scheduler(site_url):
    url = site_url.strip()
    if not url :
        return
    hunter = news_hunter(url)
    print('Task for %s starts running' % url)
    start = time.time()
    hunter.get_page()
    end = time.time()
    print('Task for %s runs %0.2f seconds' % (url, (end - start)))

news_url = os.path.join(os.path.dirname(__file__), './resource/news_url')
with open(news_url, 'r') as f :
    p = Pool()
    p.map(scheduler, (url for url in f.readlines()))
    p.close()
    p.join()

