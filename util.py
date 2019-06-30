import json
import os
from collections import defaultdict
from pypinyin import lazy_pinyin
import requests
from lxml import etree

HEADER = {'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.8',
               'Cache-Control': 'max-age=0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
               'Connection': 'keep-alive',
               'Referer': 'https://www.google.com/'
        }

def read_config(filename):
    '''
    this function read configuration from config.json, which stores university name, url, xpath
    params:
        None
    return value:
        a listm each entry is a dict, key is "university", "url" and "xpath"
    '''
    with open(filename, 'r') as conf:
        configs = json.load(conf)
    return configs

def crawl_faculty_list(configs):
    '''
    this function crawl faculy list according to configs
    params:
        a list, each entry is a dict, key is university name ("university"), target website ("url"), and
        target path ("xpath")
    return value:
        a defaultdict, each key is a university, and the value is a 'raw' list of faculty list
        (Chinese name, potentially with title and degree)
    '''
    university_faculy = defaultdict(list)
    for config in configs:
        req = requests.get(config['url'], headers=HEADER).text
        s = etree.HTML(req)
        university_faculy[config['university']] = s.xpath(config['xpath'])
    return university_faculy

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
            surname = lazy_pinyin(full_name_zh[0])     # now surname is a list of str
            give_name = lazy_pinyin(full_name_zh[1:])  # now given_name is a list of str
            full_name_pinyin = ''
            for char in give_name:
                full_name_pinyin += char
            full_name_pinyin += ' '
            for char in surname:
                full_name_pinyin += char
            zh_dict[univ][idx] = full_name_pinyin
    return zh_dict
