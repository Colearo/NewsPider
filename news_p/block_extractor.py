#!/usr/bin/env python3
from bs4 import BeautifulSoup

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
        for i in range(1, len(self.blocks_len)) :
            cur_block_rate = float(self.blocks_len[i] /
                    self.blocks_len[i-1])
            if (cur_block_rate > self.max_block_surge and 
            self.blocks_len[i] > 120 and len(content[i]) > 2 and
            i <= self.max_block_len_index) :
                self.max_block_surge = cur_block_rate
                self.surge_index = i
            elif (cur_block_rate < 1 and 
            i >= self.max_block_len_index and self.blocks_len[i + 1] < 40 
            and self.blocks_len[i + 2] < 40) :
                self.min_block_dive = cur_block_rate
                self.dive_index = i - 1 
                break
        print(self.max_block_surge, ' : ', self.blocks_len[self.surge_index], ' | ', self.min_block_dive, ' : ', self.blocks_len[self.dive_index])
            
    def get_content(self, soup, path_name):
        self.reset()
        for x in soup.find_all('script') :
            x.extract()
        content = str(soup.get_text('\n', 'br')).split('\n')
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

        return content[self.surge_index : self.dive_index]

