import json, random, time, re
from collections import defaultdict
from pypinyin import lazy_pinyin
import requests
from lxml import etree
from bs4 import BeautifulSoup
import numpy as np
from googletrans import Translator

translator = Translator(service_urls=['translate.google.cn'])
random.seed(202)
# use socks5 proxy for google sites as default, may change accordingly to other setup
proxies=dict(http='socks5h://127.0.0.1:1080', https='socks5h://127.0.0.1:1080')

def load_data(filename):
    '''
    this function will load the json file saved by main.py, return it as a dictionary
    params:
        filename: str, the path to file
    return value:
        a dict derived from the json file
    '''
    with open(filename, 'r') as f:
        ret = json.load(f)
    return ret

# pretend to browse with some browsers on some platform (shamelessly)
headers = load_data('config/user-agent.json')

# read all alternative google sites provided by search.json
# search with them randomly to avoid being blocked by google (shamelessly +1)
google_sites = load_data('config/search.json')

# rules for parsing google scholar list
interested_parties = {'composite': ['university', 'academy', 'institute'],
                      'single':  ['cas', 'hkust', 'eth', 'mit', 'sustech', 'tencent', 'microsoft', 'google', \
                      'facebook', 'amazon', 'uber', 'intel', 'aws', 'apple', 'alibaba', 'baidu', \
                      'sensetime', 'face++', 'huawei', 'samsang', 'meituan', 'jd', 'didi']}

def read_config(filename='config/institutions.json'):
    '''
    this function read configuration from config.json, which stores university name, url, xpath
    params:
        filename: str, path to the config file, default is "config.json" 
    return value:
        a list, each entry is a dict, key is "university", "url" and "xpath"
    '''
    with open(filename, 'r') as conf:
        configs = json.load(conf)
    return configs

def crawl_faculty_list(configs, target_alias=None):
    '''
    this function crawl faculty list according to configs, if target_alias is given, only faculty members affiliated
    with those institutions in it will be crawled
    params:
        configs: list, each entry is a dict, key is university name ("university"), target website ("url"), and
        target path ("xpath")
        target_alias: list of str, each str is an alias of a target institution. Any alias other than those in config
        will be ignored without notification
    return value:
        a defaultdict, each key is a university, and the value is a 'raw' list of faculty list
        (Chinese name, potentially with title and degree)
    '''
    university_faculty = defaultdict(list)
    for univ in configs:
        s_start = time.time()
        if target_alias is not None and univ['alias'] not in target_alias:
            continue
        attemp_cnt = 0
        while attemp_cnt < 10:
            header = random.choice(headers)
            req = requests.get(univ['url'], headers=header)
            # gb2312 fails to encode some rare characters, so we change it to gbk
            req.encoding = 'gbk' if req.apparent_encoding=='GB2312' else req.apparent_encoding
            text = req.text
            tree = etree.HTML(text)
            name_list = tree.xpath(univ['xpath'])
            if name_list:
                university_faculty[univ['university']] = name_list
                print("-----finish faculty collection for {} after {:.3} sec-----".format(univ['university'], \
                                                                                    time.time()-s_start))
                s_start = time.time()
                break
            attemp_cnt += 1
            if attemp_cnt == 10:
                print('fail to find faculty for {} after 10 retries'.format(univ['university']))
    return university_faculty

def extract_name(raw_dict):
    '''
    this function processes Chinese name, removing irrelevant title and punctuations
    params:
        raw_dict: defaultdict returned by crawl_faculty_list containing faculty names, including 
        Professor, Associate Professor and Lecturer, might also mixed with position, title and degree
    return value:
        a defaultdict, each corresponding entry is a Chinese name, without any other attributes
    '''
    for univ in raw_dict:
        for idx in range(len(raw_dict[univ])):
            name = raw_dict[univ][idx]
            name = name.split('(')[0].split('（')[0]
            raw_dict[univ][idx] = name
    return raw_dict

def name_to_pinyin(zh_dict):
    '''
    this functions converts Chinese name (characters) to pinyin for searching in Google Scholar
    params:
        zh_dict: defaultdict, returned by extract_name
    return value:
        a defaultdict, each corresponding entry is a converted name in pinyin,
        with form '[given name] [surname]'
    '''
    for univ in zh_dict:
        if univ == 'Zhejiang University':   # we found the Pinyin name for zju faculty
            for idx in range(len(zh_dict[univ])):
                zh_dict[univ][idx] = ' '.join(reversed(zh_dict[univ][idx].split(' ')))
            continue
        for idx in range(len(zh_dict[univ])):
            # FIXME: this method only works for surname of exactly one character, 
            # and does not take into composite surname, such as 欧阳
            full_name_zh = zh_dict[univ][idx]
            raw_pinyin = lazy_pinyin(full_name_zh)
            raw_pinyin = [c for c in raw_pinyin if c.isalpha()]
            zh_dict[univ][idx] = ''.join(raw_pinyin[1:]) + ' ' + raw_pinyin[0]
    return zh_dict

def google_search(query):
    '''
    this function searches for a given query on Google
    params:
        query: str, containing a faculty member's pinyin name with the affiliated institution for disambiguity,
        an example: "san zhang nju"
    return value:
        the hyperref to this faculty member's Google Scholar page
    '''
    query = query.lower()
    region_url = random.choice(google_sites)
    region = region_url['region']
    url_prefix = region_url['url']
    search_url = url_prefix + query
    header = random.choice(headers)
    # FIXME: I have already found some mistakes made by googling like this, e.g., an irrelevant faculty found
    try:
        page = requests.get(url=search_url+query, headers=header, proxies=proxies).text
    except:
        print('Error occurred when browsing with url {} in region {}'.format(url_prefix, region))
        if url_prefix != google_sites[0]['url']:
            page = requests.get(url=google_sites[0]['url'], headers=header, proxies=proxies).text
        else:
            return None
    sp = BeautifulSoup(page, "html.parser")
    for link in sp.find_all('a'):
        url = link.get('href')
        if url and 'scholar.google.com' in url:
            # we assume that after restricting query to a faculty member's name and affiliated institution,
            # the first result containing an href to google scholar should be his/hers
            return url
    # if not found on the first page (so it is very likely this member does not have a google scholar page),
    # just return None
    return None

def parse_scholar(url, top_k=10):
    '''
    this function browse the google scholar page returned by google_search, and return a list of institutions with
    which this faculty member has cooperated
    params:
        url: str, a url to the faculty member's google scholar page
        top_k: int, include how many coauthors' institutions from top to bottom
    return value:
        a list, each entry is a name of a coauthor's affiliated institution, might have also include his/her title/position,
        need to be furthur processed
    '''
    header = random.choice(headers)
    try:
        page = requests.get(url, headers=header, proxies=proxies).text
    except:
        print('Error occurred when browsing google scholar page at {}'.format(url))
        return None
    tree = etree.HTML(page)
    raw_list = tree.xpath('//*[@id="gsc_rsb_co"]/ul/li/div/span[2]/span[1]/text()')
    raw_list = raw_list[:top_k]
    return raw_list

def process_institutions(raw_list):
    '''
    this function processes the list returned by parse_scholar, remove potential title/position in each entry, and
    (hopefully) only preserve the full name of an institution
    params:
        raw_list: list of str, each entry is some raw information about a coauthor
    return value:
        a list of the same length, each corresponding entry contains only the name of a coauthor's institution
    '''
    processed_list = []
    if raw_list is None or raw_list == []:
        return processed_list
    for idx in range(len(raw_list)):
        # FIXME: the cases for handling troublesome punctuations are apparently non-exhausted, try to polish this part later
        delimiters = [',', '/', ';']
        # some of the institution's name is in Chinese, translate to English
        raw_list[idx] = translator.translate(raw_list[idx], src='zh-cn', dest='en').text
        entities = [raw_list[idx].lower()]
        for delimiter in delimiters:
            sep = []
            for entity in entities:
                sep += entity.split(delimiter)
            entities = sep
        # only look for universities and a few companies now
        found = False
        entities.reverse()  # university often comes after a specific institute or college, but the former is more useful
        for entity in entities:
            # address institution name in chinese
            for ins in interested_parties:
                for party in interested_parties[ins]:
                    if party in entity:
                        found = True
                        '''
                        # remove leading white space
                        while entity and entity[0].isalpha() is False:
                            entity = entity[1:]
                        while entity and entity[-1].isalpha() is False:
                            entity = entity[:-1]
                        '''
                        if entity: entity = entity.strip()  # remove leading and trailing spaces
                        # replace "&" with "and"
                        entity = entity.replace(' & ', ' and ').replace('at ', '')
                        # replace other punctuations, preserving only alphabet, digit, and white space
                        entity = re.sub(r"[^a-zA-z0-9 -']", '', entity)
                        processed_list.append(entity if ins != 'single' else party)
                        break   # we will assume that each person is affiliated with only one institution
                if found:
                    break
            if found:
                break
    return processed_list

def normal_to_01(arr):
    '''
    this function normalize a sequence of data to range [0, 1]
    params:
        arr: 1d numpy array
    return value:
        numpy array of same length, with data normalized to range [0, 1]
    '''
    return (arr-arr.min()) / (arr.max()-arr.min() + np.finfo('float').eps)

def normal_to_m1p1(arr):
    '''
    this function normalize a sequence of data to range [-1, 1]
    params:
        arr: 1d numpy array
    return value:
        numpy array of same length, with data normalized to range [-1, 1]
    '''
    return 2 * (arr-arr.min()) / (arr.max()-arr.min() + np.finfo('float').eps) - 1