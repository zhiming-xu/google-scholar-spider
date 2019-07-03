import util
import json
from collections import defaultdict
import time
import argparse
from ast import literal_eval

parser = argparse.ArgumentParser(description="collection connections and save to json")
parser.add_argument('--range', type=str, default=None, help='the institutions you want to find connection for')
parser.add_argument('--crawl', type=str, default='False', help='set to True if you want recollect connection, \
                    False if you want to use file specified by --connection')
parser.add_argument('--connection', type=str, default='connections.json', help='the connection collected by this program, \
                    it should be a dict of dict saved in json format, first key being institution name, second key being \
                    faculty member name')
args = parser.parse_args()

def univ_collection(target_alias=None):
    '''
    this function use api defined in util.py, collect faculty lists of universities provided in config.json
    and covert the Chinese to name represent by pinyin followed by the full name of this university
    params:
        target_alias: str, list of str, or None. the institutions we would like to find connection for, if set to None
        find for all institutions supported by config.json
    return value:
        defaultdict, each key is the university's name, and the value is a list of all faculty members' pinyin names
        with this alias
    '''
    configs = util.read_config()
    print('find connection for {}'.format(target_alias if target_alias else 'all'))
    univ_faculty_collection = util.crawl_faculty_list(configs, target_alias)
    univ_faculty_collection = util.extract_name(univ_faculty_collection)
    univ_faculty_collection = util.name_to_pinyin(univ_faculty_collection)
    return univ_faculty_collection

def find_connections(univ_faculty_collection):
    '''
    this function process faculty members' name list, and associate a name with corresponding google scholar page
    params:
        univ_faculty_collection: defaultdict, key: university name, value: list of faculty members' names with institutions'
        name attached to them
    return value:
        defaultdict of defaultdict, key: university name, value: defaultdict, 
                                    secondary key: faculty member's name, secondary value: list of cooperating institutions
    '''
    connections = defaultdict(defaultdict)
    for univ in univ_faculty_collection:
        s_time = time.time()
        connection_dict = defaultdict()
        for member in univ_faculty_collection[univ]:
            scholar_page = util.google_search(member+' '+univ)
            if scholar_page:
                # time.sleep(random.randint(0, 1)) -> it appears that crawling google scholar user page is permitted
                connection = util.parse_scholar(scholar_page)
                # save the following line for compute_frequency
                # we should be careful now since this could be empty
                connection_dict[member] = connection
        connections[univ] = connection_dict
        print('-----finish connection finding for {} after {:.5} sec-----'.format(univ, time.time()-s_time))
        s_time = time.time()
    with open('connections.json', 'w') as con:
        json.dump(dict(connections), con)
    return connections

def compute_frequency(connections, top_k=10):
    '''
    this function counts the connections, each institute's each occurrance counts for once
    params:
        connections: returned by find_connections
        defaultdict of defaultdict, key: university name, value: defaultdict, 
                                    secondary key: faculty member's name, secondary value: list of cooperating institutions 
        top_k: int, count the first top_k connections of a faculty member, default to 10, same as that in util.parse_scholar
    return value:
        count: defaultdict of defaultdict, key: university name, value: defaultdict,
                                           secondary key: institute's name, secondary key: number of occurrance
    '''
    counts = defaultdict(defaultdict)
    for univ in connections:
        count = defaultdict(int)
        for member in connections[univ]:
            connections[univ][member] = util.process_institutions(connections[univ][member])
            # some faculty member might have no connection on google scholar
            if connections[univ][member]:
                for institute in connections[univ][member]:
                    count[institute] += 1
        counts[univ] = dict(sorted(count.items(), key=lambda x: x[1], reverse=True))
    with open('counts.json', 'w') as cnt:
        json.dump(dict(counts), cnt)
    return counts

if __name__ == '__main__':
    target_alias = args.range
    if literal_eval(args.crawl):
        print('-----begin to recollect connection------')
        univ_faculty_collection = univ_collection(target_alias)
        connection = find_connections(univ_faculty_collection)
        count = compute_frequency(connection)
    else:
        print('-----begin to recount connection-----')
        connection = util.load_data(args.connection)
        count = compute_frequency(connection)