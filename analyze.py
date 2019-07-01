import numpy as np
import matplotlib.pyplot as plt
import json
from collections import defaultdict

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

def compute_total_connection(connections):
    '''
    this function computes the average connection per faculty member of a given institution
    have. Note: since we set `top_k` for maximum number of google scholar coauthors, this
    value might have a certain upper bound, you can change this by passing a specific top_k
    to util.parse_scholar.
    params:
        connections: dict of dict, saved by main.find_connections,
            key: university name, value: dict, 
            secondary key: faculty member's name, secondary value: list of cooperating institutions 
    return value:
        dict:
            key: institution name
            value: average connection per faculty member
    '''
    t_avg_cons = dict()
    for univ in connections:
        cnt = 0
        for member in connections[univ]:
            cnt += len(connections[univ][member])
        t_avg_con = {'total': cnt, 'avg': cnt/len(connections[univ])}
        t_avg_cons[univ] = t_avg_con
    return t_avg_cons

def compute_inner_connection(counts, t_avg_cons):
    '''
    this function computes the ratio of inner connections to total connections
    params:
        counts: dict of dict, saved by main.compute_frequency
            key: institution name, value: dict,
            secondary key: institute's name, secondary key: number of occurrance
        t_avg_cons: dict of dict, returned by compute_total_connection
            key: institution name, value: dict
            secondary key: 'total', 'avg', value: total connections, avg per member
    return value:
        dict:
            key: institution name, value: dict
            secondary key: 'total', 'avg', 'inner', value: total connections,
            avg per member, ratio of inner connections
    '''
    for univ in counts:
        for ins in counts[univ]:
            if ins.lower()==univ:
                t_avg_cons[univ]['inner'] = counts[univ][ins] / t_avg_cons[univ]['total']
                t_avg_cons[univ]['unique'] = len(counts[univ])
                break
    return t_avg_cons

