#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from scheduler.sched_status import WLEnum 
from crawler_util.block_extractor import Extractor


class Purifier:

    def __init__(self, start_url) :
        self.start_url = start_url
        self.extractor = Extractor()

    def purify_links(self, response) : 
        soup = BeautifulSoup(response, "html.parser")
        links = set(self.extractor.get_valued_links(soup, self.start_url))
        print(links)
        if links is None or len(links) == 0:
            return WLEnum.WL_PURIFY_FAIL, None
        else :
            return WLEnum.WL_PURIFY_SUCC, links

    async def purify_page(self, response) :
        content = dict()
        is_charset_gb = self.extractor.is_charset_gb(response)
        if is_charset_gb is True :
            soup = BeautifulSoup(response, "html.parser", 
                    from_encoding = 'gb18030')
        else :
            soup = BeautifulSoup(response, "html.parser")

        title = self.extractor.get_title(soup)
        content_str = ''
        if title is not None :
            content['Title'] = title[0]
            date = self.extractor.get_date(soup)
            if date is not None :
                content['Date'] = date
            source = self.extractor.get_source(soup)
            if source is not None :
                content['Source'] = source 
            news_content = self.extractor.get_content(soup)
            if news_content is not None :
                for line in news_content :
                    if line.strip() is not '' :
                        content_str = content_str + line.strip() + '\n'
                content['Content'] = content_str
            return WLEnum.WL_PURIFY_SUCC, content
        return WLEnum.WL_PURIFY_FAIL, None

    async def purify(self, response, is_content_page) :
        if is_content_page is True:
            return await self.purify_page(response)
        else :
            return self.purify_links(response)


