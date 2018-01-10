#!/usr/bin/env python3
import urllib.request
import http.cookiejar
import re
import os
import time
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup

re_num = re.compile(r'-(\d+).jpg')

class pic_hunter_for_elitebabe:

    def __init__(self):
        # self.start_url = 'http://www.elitebabes.com/model/mila-azul/'
        # self.start_url = 'http://www.elitebabes.com/model/emily-bloom/'
        # self.start_url = 'http://www.elitebabes.com/model/saloma/'
        # self.start_url = 'http://www.elitebabes.com/model/lapa-a/'
        # self.start_url = 'http://www.elitebabes.com/model/lilit-a/'
        # self.start_url = 'http://www.elitebabes.com/model/sloan-kendricks/'
        self.start_url = 'http://www.elitebabes.com/model/katie-a/'
        self.filename = 'cookie.txt'
        self.cookie = http.cookiejar.MozillaCookieJar(self.filename)
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36'), ('Connection', 'keep-alive'), ('Upgrade-Insecure-Requests', '1')]

    def save_img(self, image_url, path_name, referer):
        print(referer)
        self.opener.addheaders = [('Referer', referer)]
        with self.opener.open(image_url) as files :
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

    def get_item_image(self, soup, path_name, referer):
        big_pic = soup.find('article').ul
        for pics in big_pic.find_all('li') :
            print(pics.a['href'])
            pics_url = pics.a['href']
            if not re_num.search(pics_url):
                continue
            img_name = re_num.search(pics_url).group(1) + '.jpg'
            pics_path = os.path.join(path_name, img_name)
            is_exist = os.path.exists(pics_path)
            if not is_exist:
                self.save_img(pics_url, pics_path, referer)
                time.sleep(random.random() * 4 + 1)
            else :
                print('Pic ', pics_path, 'has been created')

    def get_item_content(self, soup, path_name, url):
        self.get_item_image(soup, path_name, url)

    def get_page_items(self, soup):
        for gallery in soup.find_all('ul', class_ = 'gallery-a b') :
            for item in gallery.find_all('li') :
                item_path = item.a['title']
                item_url = item.a['href']
                print(item_url)
                self.mkdir(item_path)
                self.addheaders = [('Referer', self.start_url)]
                with self.opener.open(item_url) as result :
                    self.cookie.save(ignore_discard=True, ignore_expires=True)
                    soup_img = BeautifulSoup(result, "html.parser")
                    self.get_item_content(soup_img, item_path, item_url)

    def get_list_page(self):
        url = self.start_url 
        print(url)
        with self.opener.open(url) as files :
            soup = BeautifulSoup(files, "html.parser")
            self.get_page_items(soup)

def scheduler(index):
    hunter = pic_hunter_for_elitebabe()
    print('Task %d starts running' % index)
    start = time.time()
    hunter.get_list_page()
    end = time.time()
    print('Task %s runs %0.2f seconds' % (index, (end - start)))

# p = Pool()
# for i in range(4):
    # p.map(scheduler, (i for i in range(4)))
# p.close()
# p.join()
scheduler(0)
