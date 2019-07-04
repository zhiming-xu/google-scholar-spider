import numpy as np
import matplotlib.pyplot as plt
import json, re
from collections import defaultdict
from itertools import cycle
import util
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import argparse

parser = argparse.ArgumentParser(description="analyze the collected data, generate statistics and provide visualization")
parser.add_argument('--connection', type=str, default='../result/connections.json', help= \
                    'path to load the the connections file collected by this program')
parser.add_argument('--count', type=str, default='../result/counts.json', help= \
                    'path to load the the counts file collected by this program, if set None, recompute the counts')
parser.add_argument('--top_k', type=int, default=10, help='if recompute counts, take how many researchers a faculty \
                    member connects to into account')
parser.add_argument('--min_occur', type=int, default=1, help='if recompute counts, take only institution show up more \
                    than min_occur times into account')
'''
parser.add_argument('--plot_type', type=int, default=2, help='choose visualization for data, 2 for 2d plots, 3 for 3d ones')
parser.add_argument('--field', type=str, default='inner_connection_ratio avg_per_member_w_connection', help='choose \
                    which fields in statistics to generate plot, the order is "data_x_dim data_y_dim" for 2d plots and \
                    "data_x_dim data_y_dim data_z_dim" for 3d ones')
'''
args = parser.parse_args()

color_cycle = cycle('bgrcmky')

def compute_frequency(connections, top_k, min_occur):
    '''
    this function counts the connections, each institute's each occurrance counts for once
    params:
        connections: returned by find_connections
        defaultdict of defaultdict, key: university name, value: defaultdict, 
                                    secondary key: faculty member's name, secondary value: list of cooperating institutions 
        top_k: int, count the first top_k connections of a faculty member
        min_occur: take only institution show up [i.e., colloborate with] more than min_occur times into account
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
        # delete the institution that occurs too rarely
        del_key = []
        for institute in count:
            if count[institute] < min_occur:
                del_key.append(institute)
        for key in del_key:
            del count[key]
        # sort institutions from occurring most frequently to most rarely
        counts[univ] = dict(sorted(count.items(), key=lambda x: x[1], reverse=True))
    with open('../result/counts.json', 'w') as cnt:
        json.dump(dict(counts), cnt)
    return counts

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

def compute_connection_stats(counts, stat):
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
        stat[univ]['total_connections'] = 0
        stat[univ]['inner_connection_ratio'] = 0
        for ins in counts[univ]:    # ins: {institution_name: #connection}
            if re.sub('[^a-zA-Z -]', '', ins).lower() == re.sub('[^a-zA-Z -]', '', univ).lower():
                stat[univ]['inner_connection_ratio'] += counts[univ][ins]
            stat[univ]['total_connections'] += counts[univ][ins]
        stat[univ]['inner_connection_ratio'] /= stat[univ]['total_connections']
        stat[univ]['unique_connections'] = len(counts[univ])
        stat[univ]['avg_connection_per_member'] = stat[univ]['unique_connections'] / stat[univ]['#total_member']
        stat[univ]['avg_per_member_w_connection'] = stat[univ]['unique_connections'] / stat[univ]['#member_w_connection']
        stat[univ]['avg_collaborator_per_member'] = stat[univ]['total_connections'] / stat[univ]['#member_w_connection']
    return stat

def plot_field_3d(stat):
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
    ax.set_xlabel('outreaching')
    ax.set_ylabel('connecting')
    ax.set_zlabel('collaborating')
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
    # print(x_axis, y_axis, z_axis)
    plt.savefig('../result/demo.png')

def compute_stat():
    con = util.load_data('../result/connections.json')
    if args.count != 'None':
        cnt = util.load_data(args.count)
    else:
        cnt = compute_frequency(con, args.top_k, args.min_occur)
    stat = defaultdict(defaultdict)
    stat = compute_member_w_connection(con, stat)
    stat = compute_connection_stats(cnt, stat)
    return stat

if __name__=="__main__":
    stat = compute_stat()
    df_stat = pd.DataFrame.from_dict(stat, 'index')
    df_stat.to_csv('../result/stat.csv')
    plot_field_3d(stat)
