from itertools import cycle
from mpl_toolkits.mplot3d import Axes3D
import argparse, re
import matplotlib.pyplot as plt
import argparse
import util
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description='provide visualization for statistics saved in the csv file')

parser.add_argument('--stat', type=str, default='result/stat.csv', help='path to the csv file saved by feature.py')
parser.add_argument('--plot_type', type=int, default=2, help='choose visualization for data, 2 for 2d plots, 3 for 3d ones')
parser.add_argument('--fields', type=str, default='inner_connection_ratio avg_connection_per_member', help='choose \
                    which fields in statistics to generate plot, the order is "data_x_dim data_y_dim" for 2d plots and \
                    "data_x_dim data_y_dim data_z_dim" for 3d ones')
parser.add_argument('--area', type=str, default='#member_w_connection', help='choose the meaning of each dot')

args = parser.parse_args()

stat = args.stat
plot_type = args.plot_type
fields = re.split('[ ]+', args.fields)
area = args.area

color_cycle = cycle('bgrcmky')

def plot_field_2d(stat, fields, area):
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
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot()
    ax.set_xlabel(fields[0])
    ax.set_ylabel(fields[1])
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    x_axis, y_axis, area = stat[fields[0]], stat[fields[1]], stat[area]
    x_axis, y_axis, area = np.array(x_axis), np.array(y_axis), np.array(area)
    x_axis = util.normal_to_m1p1(x_axis)
    y_axis = util.normal_to_m1p1(y_axis)
    area = util.normal_to_01(area) + 1
    offset1, offset2, idx = 9e-3, 1.6e-1, 0
    for row in stat.iterrows():
        ax.scatter(x_axis[idx], y_axis[idx], s=area[idx]*1600, c=next(color_cycle), marker='o', alpha=.6)
        ax.annotate(row[1][0], (x_axis[idx], y_axis[idx]), (x_axis[idx]-offset1*len(row[1][0]), y_axis[idx]+offset2))
        idx += 1
    plt.savefig('result/demo-2d.png')

def plot_field_3d(stat, fields, area):
    '''
    this function will visualize the data we collect, with x-axis being outer connection ratio,
    and y-axis being number of unique_connections connections, size of plot being total_connections connections
    params:
        stat: dataframe, fields other than institutions' names are listed as follows
        #total_member: number of total faculty members crawled from official websites
        #member_w_connection: number of total faculty members that have connection on google scholar
        total_connections: number of collaborated institutions' occurrences (w/ duplicates) shown on google scholar
        inner_connection_ratio: ratio of colloborations from the same institution
        unique_connections: number of different collaborated institutions
        avg_coauthors_per_member: total_connections / #total_member
        avg_coauthors_per_w_con: total_connections / #member_w_connection
        avg_connection_per_member: unique_connection / #member_w_connection
    return value:
        none
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel(fields[0])
    ax.set_ylabel(fields[1])
    ax.set_zlabel(fields[2])
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_zlim(-1.2, 1.2)
    x_axis, y_axis, z_axis, area = stat[fields[0]], stat[fields[1]], stat[fields[2]], stat[area]
    x_axis, y_axis, z_axis, area = np.array(x_axis), np.array(y_axis), np.array(z_axis), np.array(area)
    x_axis = util.normal_to_m1p1(x_axis)
    y_axis = util.normal_to_m1p1(y_axis)
    z_axis = util.normal_to_m1p1(z_axis)
    area = util.normal_to_01(area) + 1
    idx = 0
    for _ in stat.iterrows():
        ax.scatter(x_axis[idx], y_axis[idx], z_axis[idx], s=area[idx]*2000, c=next(color_cycle), marker='o', alpha=.6)
        idx += 1
    plt.savefig('result/demo-3d.png')

if __name__ == '__main__':
    try:
        stat = pd.read_csv(stat)
    except:
       print('can not find statistics file {}'.format(stat))
       exit(-1)
    if plot_type == 2:
        #try:
        plot_field_2d(stat, fields, area)
        #except:
        #    print('can not plot 2d with field setting: "{}"'.format(args.fields))
    elif plot_type == 3:
        try:
            plot_field_2d(stat, fields, area)
        except:
            print('can not plot 3d with field setting: "{}"'.format(args.fields))
    else:
        print('plot_type = {} is not a valid setting'.format(plot_type))