#!/usr/bin/env python3
import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup

filename = 'cookie.txt'
cookie = http.cookiejar.MozillaCookieJar(filename)
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)
postdict = {
        'username':'2014220305026',
        'password':'3041957'
        }
login_url = 'http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F'
opener.add_headers = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/13.10586")]
with opener.open(login_url) as files:
    cookie.save(ignore_discard=True, ignore_expires=True)
    soup = BeautifulSoup(files, "html.parser")
    form_tag = soup.form
    if form_tag['id'] == 'casLoginForm' :
        for child in form_tag.children :
            if child.name == 'input' :
                print (child['name'], child['value'])
                postdict[child['name']] = child['value']

postdata = urllib.parse.urlencode(postdict).encode('ascii')
print(postdata)
with opener.open(login_url, postdata) as files:
    print (files.read().decode('utf-8'))

grade_url = 'http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR'
with opener.open(grade_url) as result:
    soup = BeautifulSoup(result, "html.parser")
    if soup.a.string is None :
        print("NO CONTINUE")
    else :
        grade_url = soup.a['href'] 
        print(grade_url, "CONTINUE")
        with opener.open(grade_url) as result:
            soup = BeautifulSoup(result, "html.parser")
    
    for table in soup.find_all("table", id=True) :
        table_head_tag = table.thead
        for child in table_head_tag.stripped_strings:
            print(child, end = '|\t')
        print('\n')
        for child_body in table.tbody.children :
            print('\n')
            for child_string in child_body.stripped_strings :
                print(child_string, end = '|\t')
    print('\n')
