import pickle as pkl
import pandas as pd
import matplotlib as plt
import seaborn as sn
import os.path

'''this fetches all correlation of correlation files and
plots them into averages per condition and per condition split between rgs and veh'''

rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}


def main():
    abspath = os.getcwd()
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    vehic, rgs = bin_rats(subfolders)
    dataveh = load_data(vehic)
    datargs = load_data(rgs)
    avg_of_matrixes(dataveh, datargs)


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


def load_data(paths):
    '''loads corr_of_corr_{rat} data into a disctionary split in conditions
    :param paths: paths of folders
    :return: dict of data split into conditions
    '''

    data = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for con, paths in paths.items():
        for path in paths:
            name = path.split('/')[5]
            print(name)
            condition = name.split('_')[2]
            print(condition)
            try:
                with open(f'{path}/corr_of_corr_{name}.pkl', 'rb') as file:
                    pkldata = pkl.load(file)
                    data[condition].append(pkldata)
            except FileNotFoundError:
                pass
    return data


def avg_of_matrixes(dataveh, datargs):
    print(dataveh)
    print(datargs)


main()
