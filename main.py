import util
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
                time.sleep(random.randint(2, 5))    # hard code for now
                connection = util.parse_scholar(scholar_page)
                connection = util.process_institutions(connection)
                if connection:
                    connection_dict[member] = connection
        connections[univ] = connection_dict
    with open('connections', 'w') as con:
        con.write(str(connections))
    return connections

def compute_frequency(connections, top_k):
    '''

    '''
    raise NotADirectoryError

if __name__ == '__main__':
    univ_faculty_collection = univ_collection()

