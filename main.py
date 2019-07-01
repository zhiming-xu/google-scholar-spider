import util
import json
from collections import defaultdict
import random
import time
random.seed(2333)

def univ_collection():
    '''
    this function use api defined in util.py, collect faculty lists of universities provided in config.json
    and covert the Chinese to name represent by pinyin followed by the full name of this university
    params:
        None
    return value:
        defaultdict, each key is the university's name, and the value is a list of all faculty members' pinyin names
        with this alias
    '''
    configs = util.read_config()
    univ_faculty_collection = util.crawl_faculty_list(configs)
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
        connection_dict = defaultdict()
        for member in univ_faculty_collection[univ]:
            scholar_page = util.google_search(member+' '+univ)
            if scholar_page:
                time.sleep(random.randint(0, 1))    # hard code for now
                connection = util.parse_scholar(scholar_page)
                connection = util.process_institutions(connection)
                if connection:
                    connection_dict[member] = connection
        connections[univ] = connection_dict
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
            for institute in connections[univ][member]:
                count[institute] += 1
        counts[univ] = sorted(count.items(), key=lambda x: x[1], reverse=True)
    counts = dict(counts)
    with open('counts.json', 'w') as cnt:
        json.dump(dict(counts), cnt)
    return counts

if __name__ == '__main__':
    univ_faculty_collection = univ_collection()
    connection = find_connections(univ_faculty_collection)
    count = compute_frequency(connection)
