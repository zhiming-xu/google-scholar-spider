import numpy as np
import matplotlib.pyplot as plt
import json
from collections import defaultdict
from itertools import cycle

color_cycle = cycle('bgrcmk')

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
        t_avg_con = defaultdict(float)
        t_avg_con['total'] = cnt
        t_avg_con['avg'] = cnt / len(connections[univ])
        t_avg_cons[univ] = t_avg_con
    return t_avg_cons

def compute_inner_connection(counts, t_avg_cons):
    '''
    this function computes the ratio of inner connections to total connections
    params:
        counts: dict of dict, saved by main.compute_frequency
            key: institution name, value: dict,
            secondary key: institute's name, secondary key: number of occurrance
        t_avg_cons: dict of defaultdict, returned by compute_total_connection
            key: institution name, value: dict
            secondary key: 'total', 'avg', value: total connections, avg per member
    return value:
        defaultdict:
            key: institution name, value: dict
            secondary key: 'total', 'avg', 'inner', value: total connections,
            avg per member, ratio of inner connections
    '''
    for univ in counts:
        for ins in counts[univ]:    # ins: [institution_name, #connection]
            if ins[0].replace(' ', '').lower() == univ.replace(' ', '').lower():
                t_avg_cons[univ]['inner'] += ins[1] / t_avg_cons[univ]['total']
        t_avg_cons[univ]['unique'] = len(counts[univ])
    return t_avg_cons

def plot_field(stat):
    '''
    this function will visualize the data we collect, with x-axis being outer connection ratio,
    and y-axis being number of unique connections, size of plot being total connections
    params:
        stat: dict of dict
            key: institution name, value: dict
            secondary key: 'total', 'avg', 'inner', 'unique'
    return value:
        none
    '''
    plt.figure(figsize=(14, 10))
    plt.xlabel('collaborated')
    plt.ylabel('connected')
    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    # plt.ylim(100, 400)
    total, inner, unique = [], [], []
    for univ in stat:
        total.append(stat[univ]['total'])
        inner.append(1-stat[univ]['inner'])
        unique.append(stat[univ]['unique'])
    total, inner, unique = np.array(total), np.array(inner), np.array(unique)
    epsilon = 2e-8  # avoid divided by 0
    total = 2 * (total-total.min()) / (total.max()-total.min()+epsilon) - 1
    inner = 2 * (inner-inner.min()) / (inner.max()-inner.min()+epsilon) - 1
    offset1, offset2, idx = 7.5e-3, 6e-3, 0
    for univ in stat:
        plt.scatter(inner[idx], total[idx], s=unique[idx]*20, c=next(color_cycle), alpha=.6)
        plt.annotate(univ, (inner[idx], total[idx]), (inner[idx]-offset1*len(univ), total[idx]+offset2*len(univ)))
        idx += 1
    plt.show()

def show():
    con = load_data('connections.json')
    cnt = load_data('counts.json')
    t_avg = compute_total_connection(con)
    stat = compute_inner_connection(cnt, t_avg)
    plot_field(stat)

if __name__=="__main__":
    show()