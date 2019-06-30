import json
import os
from collections import defaultdict
from pypinyin import lazy_pinyin
import requests
from lxml import etree
from bs4 import BeautifulSoup
import random

# pretend to browse with Chrome 72 on Windows 10 (shamelessly)

header = \
        {'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
               'Connection': 'keep-alive',
               'Referer': 'https://www.google.com/'
        }

# proxy to access Google services
socks5 = dict(http='socks5h://user:pass@127.0.0.1:1080', https='socks5h://user:pass@127.0.0.1:1080')

# read all alternative google sites provided by search.json
# search with them randomly to avoid being blocked by google (shamelessly +1)
with open('search.json', 'r') as googles:
    google_sites = json.load(googles)

def read_config(filename):
    '''
    this function read configuration from config.json, which stores university name, url, xpath
    params:
        None
    return value:
        a list, each entry is a dict, key is "university", "url" and "xpath"
    '''
    with open(filename, 'r') as conf:
        configs = json.load(conf)
    return configs

def crawl_faculty_list(configs):
    '''
    this function crawl faculty list according to configs
    params:
        a list, each entry is a dict, key is university name ("university"), target website ("url"), and
        target path ("xpath")
    return value:
        a defaultdict, each key is a university, and the value is a 'raw' list of faculty list
        (Chinese name, potentially with title and degree)
    '''
    university_faculty = defaultdict(list)
    for univ in configs:
        req = requests.get(univ['url'], headers=header).text
        tree = etree.HTML(req)
        university_faculty[univ['university']] = tree.xpath(univ['xpath'])
    return university_faculty

def extract_name(raw_dict):
    '''
    this function processes Chinese name, removing irrelevant title and punctuations
    params:
        a defaultdict returned by crawl_faculty_list containing faculty names, including 
        Professor, Associate Professor and Lecturer, might also mixed with position, title and degree
    return value:
        a defaultdict, each corresponding entry is a Chinese name, without any other attributes
    '''
    for univ in raw_dict:
        for idx in range(len(raw_dict[univ])):
            name = raw_dict[univ][idx].replace(' ', '')
            name = name.split('(')[0].split('（')[0]
            raw_dict[univ][idx] = name
    return raw_dict

def name_to_pinyin(zh_dict):
    '''
    this functions converts Chinese name (characters) to pinyin for searching in Google Scholar
    params:
        a defaultdict, returned by extract_name
    return value:
        a defaultdict, each corresponding entry is a converted name in pinyin,
        with form '[given name] [surname]'
    '''
    for univ in zh_dict:
        for idx in range(len(zh_dict[univ])):
            # FIXME: this method only works for surname of exactly one character, 
            # and does not take into composite surname, such as 欧阳
            full_name_zh = zh_dict[univ][idx]
            surname = lazy_pinyin(full_name_zh[0])     # surname is a list of str
            give_name = lazy_pinyin(full_name_zh[1:])  # given_name is a list of str
            full_name_pinyin = ''
            for char in give_name:
                full_name_pinyin += char
            full_name_pinyin += ' '
            for char in surname:
                full_name_pinyin += char
            zh_dict[univ][idx] = full_name_pinyin
    return zh_dict

def google_search(query):
    '''
    this function searches for a given query on Google
    params:
        query, a string containing a faculty member's pinyin name with the affiliated institution for disambiguity
        an example: "san zhang nju"
    return value:
        the hyperref to this faculty member's Google Scholar page
    '''
    region_url = random.choice(google_sites)
    region = region_url['region']
    url_prefix = region_url['url']
    # query = query.replace(' ', '+') # convert space to + to insert in searching url
    search_url = url_prefix + query
    # FIXME: I have already found some mistakes made by googling like this, e.g., an irrelevant faculty found
    try:
        page = requests.get(url=search_url, headers=header, proxies=socks5).text
    except:
        print('Error occurred when browsing with url {} in region {}'.format(url_prefix, region))
        return None
    sp = BeautifulSoup(page, "html.parser")
    for link in sp.find_all('a'):
        url = link.get('href')
        if url and 'scholar.google.com' in url:
            break
    # we assume that after restricting query to a faculty member's name and affiliated institution,
    # the first result containing an href to google scholar should be his/hers
    return url

def parse_scholar(url):
    '''
    this function browse the google scholar page returned by google_search, and return a list of institutions with
    which this faculty member has cooperated
    params:
        a url to the faculty member's google scholar page
    return value:
        a list, each entry is a name of some institution, might have duplicates
    '''
    raise NotImplementedError