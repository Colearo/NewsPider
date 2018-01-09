#!/usr/bin/env python3
import urllib.request
import http.cookiejar
import re
import os
import time
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from multiprocessing import Pool
from block_extractor import block_extractor

class news_hunter:

    def __init__(self):
        self.start_url = 'http://www.thepaper.cn'
        self.filename = 'cookie.txt'
        self.cookie = http.cookiejar.MozillaCookieJar(self.filename)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]
        self.extractor = block_extractor()

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
        content = self.extractor.get_content(soup, path_name)
        with open(path_name, 'wb') as f:
            for line in content:
            # for line in content:
                f.write(str.encode(line + '\n'))
        print('Saving one article named ', path_name)

    def get_page_items(self, soup):
        for item in soup.find_all('h2') :
            item_path = item.find('a', target = '_blank')
            if not item_path :
                continue
            item_url = urljoin(self.start_url, item_path['href'])
            print(item_url)
            article_name = item_path.string.strip()
            with self.opener.open(item_url) as result :
                soup_article = BeautifulSoup(result, "html.parser")
                self.get_item_content(soup_article, article_name)
            time.sleep(random.random() * 4 + 1)

    def get_list_page(self, page_index):
        url = self.start_url + '/channel_2595' + str(page_index)
        print(url)
        with self.opener.open(url) as files :
            self.cookie.save(ignore_discard=True, ignore_expires=True)
            soup = BeautifulSoup(files, "html.parser")
            self.get_page_items(soup)

    def get_pages(self, start, end):
        for i in range(start, end + 1):
            print("NOW IN CHANNEL[%d]" % i)
            self.get_list_page(i)
            time.sleep(40)

def scheduler(index):
    hunter = news_hunter()
    print('Task %d starts running' % index)
    start = time.time()
    hunter.get_pages(index, index)
    end = time.time()
    print('Task %s runs %0.2f seconds' % (index, (end - start)))

p = Pool()
p.map(scheduler, (i for i in range(4)))
p.close()
p.join()

