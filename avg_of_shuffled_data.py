import pickle as pkl
import corr_of_corr_multi
import numpy
import numpy as np
import pandas
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from operator import itemgetter
from scipy import spatial, stats

"""this script find the average of the shuffled datasets
it finds all the folders in the path, loads the graph_values_{iterations}_{foldername}.pkl file 
and find the average of veh and rgs rats separately"""

iterations = 500
path = 'D:\\OS Data'
rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}


def main():
    subfolders = get_folders(path)
    rgsdata, vehdata = load_data(subfolders)
    print('rgs data')
    rgs_avgs =corr_of_corr_multi.corr_corr(rgsdata,'rgs')
    print('veh data')
    veh_avgs = find_avgs(vehdata)
    plot_data(rgs_avgs, 'RGS14')
    plot_data(veh_avgs, 'Vehicle')


def get_folders(abspath):
    """get subfolder in supplied path
    :param abspath: path to folders
    :return: array of strings to paths
    """
    files = [f.path for f in os.scandir(abspath) if f.is_file()]
    return files


def load_data(folders):
    """data is stored in a nested dictionary: {rgs/vehicle: {study-day:2d-array of distances}}
    :param folders:
    :return:
    """
    rgsdata = {}
    vehdata = {}
    for folder in folders:
        name = folder.split('_500_')[-1]
        data = pkl.load(open(f"{path}\\graph_values_{iterations}_{name}", 'rb'))
        ratnr = int(name.split('_')[0][3:4])
        entry = {}
        # print(data)
        for key, val in data.items():
            val = pd.DataFrame(val).fillna(value=0)
            entry[key] = val

        if ratnr in rats['vehicle']:
            vehdata[name.strip('.pkl')] = entry
        if ratnr in rats['rgs']:
            rgsdata[name.strip('.pkl')] = entry
    return rgsdata, vehdata


def find_avgs(data):
    data_avgs = {}
    for sd, df in data.items():
        # this will caluclate the average of all the trials into a df of the values per sd
        trial_averages = pd.concat([each.stack() for each in df.values()], axis=1) \
            .apply(lambda x: x.mean(), axis=1) \
            .unstack()
        data_avgs[sd] = trial_averages

    sd_averages = pd.concat([each.stack() for each in data_avgs.values()], axis=1) \
        .apply(lambda x: x.mean(), axis=1) \
        .unstack()
    return sd_averages
    # print(sd_averages)
    # for key, df in data_avgs.items():
    #     print(f'{key}\n{df}\n')


def plot_data(data, name):
    avg = data.stack().mean()
    plt.figure(figsize=[15, 10])
    plt.title(f'avg of distances per neuron for: {name}, Mean: {avg}')
    sn.heatmap(data, square=True, vmax=0.2, vmin=-0.2)
    plt.xlabel('Neuron #')
    plt.ylabel('Neuron #')
    plt.show()
    # pass


main()
