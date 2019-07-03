import numpy as np
import matplotlib.pyplot as plt
import json, re
from collections import defaultdict
from itertools import cycle
import util
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

color_cycle = cycle('bgrcmky')

def compute_member_w_connection(connections, stat):
    '''
    this function compute # of faculty members w/ connection provided by google scholar
    params:
        connections: dict of dict, saved by main.find_connections,
            key: institution name, value: dict, 
            secondary key: faculty member's name, secondary value: list of cooperating institutions
        stat:
            statistics
    return value:
        stat: key: institution name, value: dict
        secondary key: #member_w_connection, secondary value: cnt
    '''
    for univ in connections:
        member_cnt = 0
        for member in connections[univ]:
            if connections[univ][member]:
                member_cnt += 1
        stat[univ]['#member_w_connection'] = member_cnt
        stat[univ]['#total_member'] = len(connections[univ])
    return stat

def compute_total_connection(connections, stat):
    '''
    this function computes the average connection per faculty member of a given institution
    have. Note: since we set `top_k` for maximum number of google scholar coauthors, this
    value might have a certain upper bound, you can change this by passing a specific top_k
    to util.parse_scholar.
    params:
        connections: dict of dict, saved by main.find_connections,
            key: institution name, value: dict, 
            secondary key: faculty member's name, secondary value: list of cooperating institutions
    return value:
        dict:
            key: institution name, value: dict
            secondary key: 'total_connections': # of total_connections connections,
            '#members': # of all faculty members
    '''
    for univ in connections:
        cnt = 0
        for member in connections[univ]:
            cnt += len(connections[univ][member])
        stat[univ]['total_connections'] = cnt
    return stat

def compute_inner_connection(counts, stat):
    '''
    this function computes the ratio of inner_connection_ratio connections to total_connections connections
    params:
        counts: dict of dict, saved by main.compute_frequency
            key: institution name, value: dict,
            secondary key: institute's name, secondary key: number of occurrance
        stat: dict of dict, statistics computed
    return value:
        defaultdict:
            key: institution name, value: dict
            secondary key: 'total_connections', 'num_members', 'inner_connection_ratio', value: total_connections connections,
            num_members per member, ratio of inner_connection_ratio connections
    '''
    for univ in counts:
        stat[univ]['inner_connection_ratio'] = 0
        for ins in counts[univ]:    # ins: {institution_name: #connection}
            if re.sub('[^a-zA-Z -]', '', ins).lower() == re.sub('[^a-zA-Z -]', '', univ).lower():
                stat[univ]['inner_connection_ratio'] += counts[univ][ins]
        stat[univ]['inner_connection_ratio'] /= stat[univ]['total_connections']
        stat[univ]['unique_connections'] = len(counts[univ])
        stat[univ]['avg_connection_per_member'] = stat[univ]['unique_connections'] / stat[univ]['#total_member']
        stat[univ]['avg_per_member_w_connection'] = stat[univ]['unique_connections'] / stat[univ]['#member_w_connection']
        stat[univ]['avg_collaborator_per_member'] = stat[univ]['total_connections'] / stat[univ]['#member_w_connection']
    return stat

def plot_field(stat):
    '''
    this function will visualize the data we collect, with x-axis being outer connection ratio,
    and y-axis being number of unique_connections connections, size of plot being total_connections connections
    params:
        stat: dict of dict
            key: institution name, value: dict
            secondary key: 'total_connections', 'num_members', 'inner_connection_ratio', 'unique_connections'
    return value:
        none
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('outreached')
    ax.set_ylabel('connected')
    ax.set_zlabel('collaborated')
    ax.set_xlim(-.2, 1.2)
    ax.set_ylim(-.2, 1.2)
    ax.set_zlim(-.2, 1.2)
    x_axis, y_axis, z_axis, area = [], [], [], []
    for univ in stat:
        x_axis.append(1-stat[univ]['inner_connection_ratio'])
        y_axis.append(stat[univ]['avg_per_member_w_connection'])
        z_axis.append(stat[univ]['avg_collaborator_per_member'])
        area.append(stat[univ]['#total_member'])
    x_axis, y_axis, z_axis, area = np.array(x_axis), np.array(y_axis), np.array(z_axis), np.array(area)
    x_axis = util.normal_to_01(x_axis)
    y_axis = util.normal_to_01(y_axis)
    z_axis = util.normal_to_01(z_axis)
    area = util.normal_to_01(area) + 1
    offset1, offset2, idx = 7.5e-3, 1.5e-1, 0
    for univ in stat:
        ax.scatter(x_axis[idx], y_axis[idx], z_axis[idx], s=area[idx]*2000, c=next(color_cycle), marker='o', alpha=.6)
        # ax.annotate(univ, (x_axis[idx],y_axis[idx], z_axis[idx]), (x_axis[idx], y_axis[idx], z_axis[idx]))
        idx += 1
    plt.savefig('../result/demo.png')

def compute_stat():
    con = util.load_data('connections.json')
    cnt = util.load_data('counts.json')
    stat = defaultdict(defaultdict)
    stat = compute_member_w_connection(con, stat)
    stat = compute_total_connection(con, stat)
    stat = compute_inner_connection(cnt, stat)
    return stat

if __name__=="__main__":
    stat = compute_stat()
    df_stat = pd.DataFrame.from_dict(stat, 'index')
    df_stat.to_csv('stat.csv')
    plot_field(stat)
