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


re_end_page = re.compile(r'[a-zA-Z/]+(\d+)_(\d+).html')
re_num = re.compile(r'[a-zA-Z0-9/]+/(\d+).jpg')

class pic_hunter:

    def __init__(self):
        self.start_url = 'http://www.xieezhijia.com'
        self.filename = 'cookie.txt'
        self.cookie = http.cookiejar.MozillaCookieJar(self.filename)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]

    def save_img(self, image_url, path_name):
        with self.opener.open(image_url) as files:
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
        big_pic = soup.find('div', class_ = 'entry fl w100')
        pics = big_pic.img
        print(pics)
        img_name = re_num.search(pics['src']).group(1) + '.jpg'
        pics_path = os.path.join(path_name.strip(), img_name)
        pics_url = urljoin(self.start_url, pics['src'])
        is_exist = os.path.exists(pics_path)
        if not is_exist:
            self.save_img(pics_url, pics_path)
        else :
            print('Pic ', pics_path, 'has been created')

    def get_item_content(self, soup, path_name):
        self.get_item_image(soup, path_name)
        end_page = soup.find('div', class_ = 'digg').find('span', text = '..').find_next_sibling('a')
        print(end_page)
        end_path = re_end_page.search(end_page['href']).group(2)
        middle_path = re_end_page.search(end_page['href']).group(1)
        for index in range(2, int(end_path) + 1) :
            item_url = self.start_url + '/leisitubaobao/' + middle_path + '_' + str(index) + '.html' 
            print(item_url)
            with self.opener.open(item_url) as next_result :
                next_soup = BeautifulSoup(next_result, "html.parser")
                self.get_item_image(next_soup, path_name)

    def get_page_items(self, soup):
        for item in soup.find('ul', class_ = 'img-list high ilist').find_all('li') :
            item_path = item.find('a', target = '_blank')
            # item_url = urljoin(self.start_url, item_path['href'])
            item_url = item_path['href']
            print(item_url)
            album_name = item_path['title']
            self.mkdir(album_name)
            with self.opener.open(item_url) as result :
                soup_img = BeautifulSoup(result, "html.parser")
                self.get_item_content(soup_img, album_name)
            time.sleep(random.random() * 4 + 1)

    def get_list_page(self, page_index):
        url = self.start_url + '/leisitubaobao/' + str(page_index) 
        print(url)
        with self.opener.open(url) as files :
            self.cookie.save(ignore_discard=True, ignore_expires=True)
            soup = BeautifulSoup(files, "html.parser")
            self.get_page_items(soup)

    def get_pages(self, start, end):
        for i in range(start, end + 1):
            print("NOW IN INDEX[%d]" % i)
            self.get_list_page(i)
            time.sleep(40)

def scheduler(index):
    hunter = pic_hunter()
    print('Task %d starts running' % index)
    start = time.time()
    hunter.get_pages(index, index)
    end = time.time()
    print('Task %s runs %0.2f seconds' % (index, (end - start)))

p = Pool()
p.map(scheduler, (i + 1 for i in range(4)))
p.close()
p.join()

