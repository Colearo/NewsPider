#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request  
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse,urljoin

REGEXES = {
        'positive_re' : re.compile(r'news|article|center|'
        r'entry|main|pagination|post|text|blog|fix|con|'
        r'story|headline|newsbox|header|news_li|box|news_list', re.I),
        'negative_re' : re.compile('index|combx|comment|com-|'
        'contact|foot|footer|footnote|masthead|media|meta|'
        'outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|'
        'shopping|tag|tool|widget|javascript|categor|ad|'
        'video|qzone|twitter|pages|homes|img', re.I),
        'video_re' : re.compile(r'video|interactive', re.I),
        'unlikely_link_re' : re.compile(r'javascript|index|'
        r'extra|ad-break|ad-banner|\blist|categor|\bchannel|tag|commentid|'
        r'[\?\&]|mailto|photo|column|snapshot|mob|special|about|\bcomment',
        re.I),
        'unlikely_div_re' : re.compile(r'news_photoview|news_special|'
        r'bx-viewport', re.I), 
        'unlikely_title_re' : re.compile('视频|问我|图集'),
        'likelytag_re' : re.compile(r'h3|h2|li|ul'),
        'likelynum_re' : re.compile(r'(\d+)'),
        'host_re' : re.compile(r'\.([a-zA-Z0-9]+)\.(com|cn)'),
        'title_re' : re.compile(r'\_|\||\-'),
        'charset_re' : re.compile(r'charset=(gb[a-zA-Z0-9]+)', re.I),
        'madarin_re' : re.compile(r'[0-9a-zA-Z\:\!\：\(\)《》]'),
        'ltag_re' : re.compile(r'<[^>]+>', re.S),
        'rtag_re' : re.compile(r'</[^>]+>', re.S),
        'tag_br_re' : re.compile(r'<br(/*)>'),
        'redundancy_re' : re.compile(r'[\s\n\t\r]'),
        'comment_re' : re.compile(r'<!--.*?-->'),
        'date_re' : re.compile(
            r'(\d{4})\s*[-/年]\s*(\d{2})[-/月]\s*(\d{2})日?\s?(\d{2}):(\d{2})'), 
        'source_re' : re.compile(r'["@\s]+来源：@*([^"@]+)["@]?'),
        'redundant_tag' : ['script', 'style', 'var', 'cite', 'code', 
            'img', 'span', 'figure', 'h3'], 
        'ab_comment_re' : re.compile(r'<!--\[if !IE\]>.*?<!\[endif\]-->', 
            re.M|re.S),
        'nextline_re' : re.compile(r'[\n\t\r]', re.M),
        }

class Extractor:

    def __init__(self):
        self.block_width = 3
    
    def reset(self):
        self.max_block_len = 0
        self.max_block_len_index = 0
        self.surge_index = 0
        self.min_block_len = float('inf')
        self.dive_index = 0
        self.blocks_len = []

    def get_surge_dive(self, content) :
        for i in range(len(self.blocks_len) - self.block_width) :
            if (self.blocks_len[i] > 110 and 
            i <= self.max_block_len_index and self.surge_index == 0) :
                for j in range(self.block_width + 1) :
                    if self.blocks_len[i + j] == 0 :
                        self.surge_index = 0
                    else :
                        self.surge_index = i
            elif (i >= self.max_block_len_index and 
            self.blocks_len[i - 1] < 40 and
            self.blocks_len[i] == 0 and 
            self.blocks_len[i + 1] == 0) :
                self.dive_index = i 
                break
        # print(self.surge_index, ':', self.dive_index)
            
    def sanitize(self, soup):
        s_soup = REGEXES['nextline_re'].sub('', str(soup))
        s_soup = BeautifulSoup(s_soup, "html.parser")
        for tag in REGEXES['redundant_tag'] :
            [x.decompose() for x in s_soup.find_all(tag)]
        [a.extract() for a in s_soup.find_all('a')]
        # [span.decompose() for span in soup.find_all('span')]
        # [a.extract() for a in soup.find_all('a')]
        # text = soup.prettify()
        text = str(s_soup)
        text = REGEXES['nextline_re'].sub('', text)
        text = REGEXES['comment_re'].sub('', text)
        text = REGEXES['ab_comment_re'].sub('', text)
        text = REGEXES['rtag_re'].sub('\n', text)
        text = REGEXES['ltag_re'].sub('', text)
        # [span.extract() for span in soup.find_all('span')]
        # [style.extract() for style in soup.find_all('style')]
        # [img.extract() for img in soup.find_all('img')]
        return text

    def sanitize_links(self, soup):
        [x.extract() for x in soup.find_all('script')]
        [span.extract() for span in soup.find_all('span')]
        [style.extract() for style in soup.find_all('style')]
        [img.extract() for img in soup.find_all('img')]
        # [a.extract() for a in soup.find_all('a', href = True)]
        return soup

    def sanitize_tags(self, soup):
        [x.decompose() for x in soup.find_all('script')]
        [img.decompose() for img in soup.find_all('img')]
        soup = REGEXES['comment_re'].sub('', str(soup))
        soup = REGEXES['rtag_re'].sub('@', soup)
        soup = REGEXES['ltag_re'].sub('@', soup)
        return soup

    def score_item(self, item):
        score = 0

        if item.has_attr('class'):
            score += len(REGEXES['positive_re'].findall(
                str(item['class']))) * 2
            score += len(REGEXES['negative_re'].findall(
                str(item['class']))) * -4
            score += len(REGEXES['unlikely_div_re'].findall(
                str(item['class']))) * -20
        else :
            score += -4

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
                score += num_occur * 1 
            else :
                score += -8
            if len(str(item.string).strip()) > 10 :
                score += 2
            else :
                score += -2

        # score += len(REGEXES['likelytag_re'].findall(
        #     str(item.name))) * 5

        return score

    def get_valued_links(self, soup, start_url):
        soup_sanitized = self.sanitize_links(soup)
        links = []
        for item_path in soup_sanitized.find_all('a', href = True) :
            item_url = urljoin(start_url, item_path['href'].strip())
            cur_host = REGEXES['host_re'].search(item_url)
            host = REGEXES['host_re'].search(start_url)
            if host is None or cur_host is None :
                continue
            if (REGEXES['video_re'].search(item_url) or 
            REGEXES['unlikely_link_re'].search(item_url) or
            host.group(1) != cur_host.group(1)) :
                continue

            if item_url not in links :
                score = self.score_item(item_path)
                for parent in item_path.find_parents('div', limit = 2) :
                    score += self.score_item(parent)
                for parent in item_path.find_parents('h3', limit = 1) :
                    score += 2
                for parent in item_path.find_parents('h2', limit = 1) :
                    score += 2
                for child in item_path.find_all('h3') :
                    score += 2
                if score > 2 :
                    links.append(item_url)
        return links 

    def is_charset_gb(self, response):
        bs = response.read()
        charset = REGEXES['charset_re'].search(str(bs[0: 2048]))
        if charset is not None :
            return bs.decode('gb18030')

        return bs
            
    def get_title(self, soup):
        if soup.head is None :
            return None

        title = REGEXES['title_re'].split(
                str(soup.head.title.string)) 
        if title is None :
            return None
        elif len(REGEXES['madarin_re'].sub(
            '',title[0].strip())) < 8 :
            return None
        elif REGEXES['unlikely_title_re'].search(
            title[0].strip()) is not None :
            return None
        else :
            return title 

    def get_date(self, soup):
        date = REGEXES['date_re'].search(str(soup))
        if date is not None :
            date = (date.group(1) + '/' + date.group(2) + '/' +
            date.group(3) + ' ' + date.group(4) + ':' + date.group(5))
        return date

    def get_source(self, soup):
        soup = self.sanitize_tags(soup)
        source = REGEXES['source_re'].search(soup)
        if source is not None :
            source = source.group(1)
        return source

    def get_content(self, soup):
        self.reset()
        soup_sanitized = self.sanitize(soup)
        content = str(soup_sanitized).splitlines(True)
        for i in range(len(content) - self.block_width) :
            cur_block_len = 0
            for j in range(self.block_width + 1) :
                text = REGEXES['redundancy_re'].sub('', content[i + j])
                cur_block_len += len(text)
            if cur_block_len > self.max_block_len :
                self.max_block_len = cur_block_len
                self.max_block_len_index = i
            if cur_block_len < self.min_block_len :
                self.min_block_len = cur_block_len
            self.blocks_len.append(cur_block_len)
        
        # print(self.blocks_len)
        self.get_surge_dive(content)
        if self.max_block_len < 40 :
            return None
        else :
            return content[self.surge_index : self.dive_index]

