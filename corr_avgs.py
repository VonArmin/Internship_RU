import pickle as pkl

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path

'''this fetches all correlation of correlation files and
plots them into averages per condition and per condition split between rgs and veh'''

rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}


def main():
    abspath = os.getcwd()
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    vehic, rgs = bin_rats(subfolders)
    vehfilter = filter_SD(vehic)
    rgsfilter = filter_SD(rgs)
    dataveh = load_data(vehfilter)
    datargs = load_data(rgsfilter)
    avg_of_matrixes(dataveh, 'Vehicle')
    avg_of_matrixes(datargs, 'RGS14')


def bin_rats(folders):
    """finds the number of the rats and add it to a dict
    :param folders: array of all subfolders
    :return: dict of binned rats (pathsv contains paths to veh and pathsr to rgs)
    """
    pathsv = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    pathsr = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for i, folder in enumerate(folders):
        type = folder.split('/')[5].split('_')
        if int(type[0].split('t')[1]) in rats['vehicle']:
            pathsv[type[2]].append(folder)
        if int(type[0].split('t')[1]) in rats['rgs']:
            pathsr[type[2]].append(folder)

    return pathsv, pathsr


def filter_SD(dataset):
    '''filters out the rats which have more than one SD for a condition and only keeps the earliest study day
    :param dataset: dataset of paths to corr_of_corr files
    :return: filtered dataset
    '''
    outpaths = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    present_rats = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for con, paths in dataset.items():
        for path in paths:
            name = path.split('/')[5].split('_')
            if name[0] not in present_rats[con]:
                present_rats[con].append(name[0])
                outpaths[con].append(path)
    return outpaths


def load_data(paths):
    '''loads corr_of_corr_{rat} data into a dictionary split in conditions
    :param paths: paths of folders
    :return: dict of data split into conditions
    '''

    data = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for con, paths in paths.items():
        for path in paths:
            name = path.split('/')[5]
            condition = name.split('_')[2]
            try:
                with open(f'{path}/corr_of_corr_{name}.pkl', 'rb') as file:
                    pkldata = pkl.load(file)
                    data[condition].append(pkldata)
            except FileNotFoundError:
                pass
    return data


def avg_of_matrixes(dataset, name):
    for con, arr in dataset.items():
        plt.figure(figsize=(18, 15), tight_layout=True)
        averages = pd.concat([each.stack() for each in arr], axis=1) \
            .apply(lambda x: x.mean(), axis=1) \
            .unstack()
        plt.title(f'average of corr of corr matrixes for condition: {con} in {name} Rats')
        sn.heatmap(averages, square=True, linewidth=0.1, annot=True, vmax=1, vmin=0)
        plt.savefig(f'avg_corr_of_corr_{con}_{name}.png')


main()
