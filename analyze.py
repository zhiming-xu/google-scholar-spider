import numpy as np
import matplotlib.pyplot as plt
import json, re
from collections import defaultdict
from itertools import cycle
import util

color_cycle = cycle('bgrcmk')

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
            if re.sub('[^a-zA-Z -]', '', ins).lower() == re.sub('[^a-zA-Z -]', '', univ).lower():
                t_avg_cons[univ]['inner'] += counts[univ][ins] / t_avg_cons[univ]['total']
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
    total, inner, unique, avg = [], [], [], []
    for univ in stat:
        total.append(stat[univ]['total'])
        inner.append(1-stat[univ]['inner'])
        unique.append(stat[univ]['unique'])
        avg.append(stat[univ]['avg'])
    total, inner, unique, avg = np.array(total), np.array(inner), np.array(unique), np.array(avg)
    epsilon = 2e-8  # avoid divided by 0
    avg = util.normal_to_m1p1(avg)
    inner = util.normal_to_m1p1(inner)
    unique = util.normal_to_01(unique) + 1
    offset1, offset2, idx = 7.5e-3, 6e-3, 0
    for univ in stat:
        plt.scatter(inner[idx], avg[idx], s=unique[idx]*200, c=next(color_cycle), alpha=.6)
        plt.annotate(univ, (inner[idx], avg[idx]), (inner[idx]-offset1*len(univ), avg[idx]+offset2*len(univ)))
        idx += 1
    plt.show()

def show():
    con = util.load_data('connections.json')
    cnt = util.load_data('counts.json')
    t_avg = compute_total_connection(con)
    stat = compute_inner_connection(cnt, t_avg)
    plot_field(stat)

if __name__=="__main__":
    show()