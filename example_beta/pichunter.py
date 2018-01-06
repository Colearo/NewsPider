#!/usr/bin/env python3
import urllib.request
import http.cookiejar
import re
import os
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup


re_end_page = re.compile(r'[a-zA-Z/]+(\d+)_(\d+).html$')
re_num = re.compile(r'第\s*(\d+)张')

class pic_hunter:

    def __init__(self):
        self.start_url = 'https://www.aitaotu.com/guonei/'
        self.filename = 'cookie.txt'
        self.cookie = http.cookiejar.MozillaCookieJar(self.filename)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.opener.add_headers = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]

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
        print(big_pic)
        for pics in big_pic.find_all('img') :
            print(pics['src'], pics['alt'])
            img_name = re_num.search(pics['alt']).group(1) + '.jpg'
            pics_path = os.path.join(path_name, img_name)
            self.save_img(pics['src'], pics_path)

    def get_item_content(self, soup, path_name):
        self.get_item_image(soup, path_name)
        end_page = soup.find('a', text = '末页')
        print(end_page['href'])
        end_path = re_end_page.match(end_page['href']).group(2)
        middle_path = re_end_page.match(end_page['href']).group(1)
        for index in range(2, int(end_path) + 1) :
            item_url = self.start_url + middle_path + '_' + str(index) + '.html' 
            print(item_url)
            with self.opener.open(item_url) as next_result :
                next_soup = BeautifulSoup(next_result, "html.parser")
                self.get_item_image(next_soup, path_name)
            time.sleep(4)

    def get_page_items(self, soup):
        for item in soup.find('div', class_ = 'Clbc_Game_l_a').find_all('div', class_ = 'item masonry_brick') :
            item_path = item.find('a', target = '_blank')
            item_url = urljoin(self.start_url, item_path['href'])
            print(item_url)
            album_name = item_path.img['alt']
            self.mkdir(album_name)
            with self.opener.open(item_url) as result :
                soup_img = BeautifulSoup(result, "html.parser")
                self.get_item_content(soup_img, album_name)

    def get_list_page(self, page_index):
        url = self.start_url + 'list_' + str(page_index) + '.html'
        print(url)
        with self.opener.open(url) as files :
            self.cookie.save(ignore_discard=True, ignore_expires=True)
            soup = BeautifulSoup(files, "html.parser")
            self.get_page_items(soup)

    def get_pages(self, start, end):
        for i in range(start, end + 1):
            self.get_list_page(i)
            time.sleep(40)

hunter = pic_hunter()
hunter.get_pages(3, 10)


