#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import urlparse,urljoin
import urllib.request  
from bs4 import BeautifulSoup
import re

REGEXES = {
        'positive_re' : re.compile(r'news|article|center|'
        r'entry|main|pagination|post|text|blog|fix|con|'
        r'story|headline|_blank', re.I),
        'negative_re' : re.compile('index|combx|comment|com-|'
        'contact|foot|footer|footnote|masthead|media|meta|'
        'outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|'
        'shopping|tag|tool|widget|list|javascript|categor|ad|'
        'video|qzone|twitter|pages|homes', re.I),
        'video_re' : re.compile(r'video|interactive', re.I),
        'unlikely_re' : re.compile('javascript|index|'
        'extra|ad-break|ad-banner|list|categor|\bchannel|tag|'
        '[\?\&]|mailto|photo|column|snapshot|mob', re.I),
        'likelytag_re' : re.compile(r'h3|h2|li'),
        'likelynum_re' : re.compile(r'(\d+)'),
        'host_re' : re.compile(r'\.([a-zA-Z0-9]+)\.(com|cn)'),
        'title_re' : re.compile(r'\_|\||\-'),
        'charset_re' : re.compile(
        r'charset\s*=\s*\"*(\w*gb\w+)\"*\s*', re.I),
        'madarin_re' : re.compile(r'[0-9a-zA-Z\:\!\：]')
        }

class block_extractor:

    def __init__(self):
        self.block_width = 3
    
    def reset(self):
        self.max_block_len = 0
        self.max_block_len_index = 0
        self.max_block_surge = float(0.0)
        self.surge_index = 0
        self.min_block_len = float('inf')
        self.min_block_dive = float('inf')
        self.dive_index = 0
        self.blocks_len = []

    def get_surge_dive(self, content) :
        for i in range(1, len(self.blocks_len) - 2) :
            cur_block_rate = float(self.blocks_len[i] /
                    self.blocks_len[i-1])
            # if (cur_block_rate > self.max_block_surge and 
            if (self.blocks_len[i] > 170 and 
            len(content[i]) > 5 and
            i <= self.max_block_len_index and 
            self.surge_index == 0) :
                self.max_block_surge = cur_block_rate
                self.surge_index = i
            elif (cur_block_rate < 1 and 
            i >= self.max_block_len_index and 
            self.blocks_len[i + 1] < 30 and 
            self.blocks_len[i + 2] < 30) :
                self.min_block_dive = cur_block_rate
                self.dive_index = i - 1 
                break
        print(self.max_block_surge, ' : ', self.blocks_len[self.surge_index], ' | ', self.min_block_dive, ' : ', self.blocks_len[self.dive_index])
            
    def sanitize(self, soup):
        [x.extract() for x in soup.find_all('script')]
        [span.extract() for span in soup.find_all('span')]
        [style.extract() for style in soup.find_all('style')]
        return soup

    def sanitize_links(self, soup):
        [a.extract() for a in soup.find_all('a', href = True)]
        return soup

    def score_item(self, item):
        score = 0

        if item.has_attr('class'):
            score += len(REGEXES['positive_re'].findall(
                str(item['class']))) * 2
            score += len(REGEXES['negative_re'].findall(
                str(item['class']))) * -4

        if item.has_attr('id'):
            score += len(REGEXES['positive_re'].findall(
                str(item['id']))) * 2
            score += len(REGEXES['negative_re'].findall(
                str(item['id']))) * -4

        if item.has_attr('target'):
            score += len(REGEXES['positive_re'].findall(
                str(item['target']))) * 1 

        if item.has_attr('href'):
            path = urlparse(item['href']).path
            score += len(REGEXES['positive_re'].findall(
                str(path))) * 2 
            score += len(REGEXES['negative_re'].findall(
                str(path))) * -4
            num_occur = len(REGEXES['likelynum_re'].findall(
            str(path))) 
            if num_occur > 0 :
                score += num_occur * 4 
            else :
                score += -8
            if len(str(item.string).strip()) > 8 :
                score += 2
            else :
                score += -2

        score += len(REGEXES['likelytag_re'].findall(
            str(item.name))) * 5

        return score

    def get_valued_links(self, soup, start_url):
        soup_sanitized = self.sanitize(soup)
        links = []
        for item_path in soup_sanitized.find_all('a', 
        href = True) :
            item_url = urljoin(start_url, 
                    item_path['href'].strip())
            cur_host = REGEXES['host_re'].search(
                    item_url)
            host = REGEXES['host_re'].search(start_url)
            if host is None or cur_host is None :
                continue
            if (REGEXES['video_re'].search(item_path['href']) or 
            REGEXES['unlikely_re'].search(item_path['href']) or
            host.group(1) != cur_host.group(1)) :
                continue

            if item_url not in links :
                score = self.score_item(item_path)
                for parent in item_path.find_parents(limit = 2) :
                    score += self.score_item(parent)
                for child in item_path.find_all('h3') :
                    score += 3
                if score > 0 :
                    links.append(item_url)
                    print(item_url)
        return links 

    def is_charset_gb(self, response):
        content_type = response.info().get('Content-Type')
        if content_type is not None :
            charset = REGEXES['charset_re'].search(content_type)
            if charset is not None :
                return True

        return False 
            
    def get_title(self, soup):
        title = REGEXES['title_re'].split(
                str(soup.head.title.string)) 
        if title is None :
            return None
        elif len(REGEXES['madarin_re'].sub(
            '',title[0].strip())) < 8 :
            return None
        else :
            return title 

    def get_content(self, soup):
        self.reset()
        soup_sanitized = self.sanitize(soup)
        content = str(soup_sanitized.get_text('\%\%', 'br')).split('\%\%')
        for i in range(len(content) - self.block_width) :
            cur_block_len = 0
            for j in range(self.block_width + 1) :
                cur_block_len += len(content[i + j].strip())
            if cur_block_len > self.max_block_len :
                self.max_block_len = cur_block_len
                self.max_block_len_index = i
            if cur_block_len < self.min_block_len :
                self.min_block_len = cur_block_len
            self.blocks_len.append(cur_block_len)
        
        self.get_surge_dive(content)
        if (self.max_block_surge == float(0.0) or
        self.min_block_dive == float('inf') or
        self.max_block_len < 120) :
            return None
        else :
            return content[self.surge_index : self.dive_index]

