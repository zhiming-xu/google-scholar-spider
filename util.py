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

def extract_name(raw_list):
    '''
    this function processes Chinese name, removing irrelevant title and punctuations
    params:
        a raw string returned by crawler containing faculty names (Professor, Associate Professor, Lecturer)
        might also mix with title and degree
    return value:
        a list of the same length, each corresponding entry is a Chinese name, without any other attributes
    '''
    for idx in range(len(raw_list)):
        raw_list[idx] = raw_list[idx].split(r' ')[0]
    return raw_list

def name_to_pinyin(name_list):
    '''
    this functions converts Chinese name (characters) to pinyin for searching in Google Scholar
    params:
        a list, whose element is a string representing a Chinese name (a few characters)
    return value:
        a list of the same length, each corresponding entry is a converted name in pinyin,
        with form '[given name] [surname]'
    '''
    for idx in range(len(name_list)):
        full_name = lazy_pinyin(name_list[idx])
        # FIXME: this method only works for surname of exactly one character, 
        # and does not take into composite surname, such as 欧阳
        surname = full_name[0]
        give_name = full_name[1:]
        pinyin_name = give_name + ' ' + surname
        name_list[idx] = pinyin_name
    return name_list
