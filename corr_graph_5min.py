import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from scipy import spatial
from operator import itemgetter
from collections import deque

"""this ia a variant of corr_avgs.py which subdevides each period in 5min bins"""

path = '/media/irene/Data/Rat_OS_EPhys_RGS14_Cell_Assembly'
order_i = []
order_ii = []
order_iii = []


def main():
    folders = create_folders(path)
    run_calculations(folders)
    # single_set()


def single_set():
    rat = 'Rat2_SD2_OR'
    path = 'C:/Users/Armin/PycharmProjects/Internship_RU'
    data = load_data(pkl.load(open(f'actmat_dict.pkl', 'rb')), rat)
    save_data(data, rat, path)
    data = pkl.load(open(f'{path}/corr_dataset_{rat}.pkl', 'rb'))
    # plot_data(data, rat, path)
    corr_corr(data, rat, path)


def create_folders(abspath):
    """fetches all folders in the folder the script is run in and creates the Graph folder used later on
    :param abspath: -
    :return: array of strings
    """
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    for i, path in enumerate(subfolders):
        try:
            os.mkdir(f'{path}/Graph')
        except FileExistsError:
            pass
    return subfolders


def run_calculations(folders):
    """manages the folders and wether files are created or skipped
    :param folders: array of strings of paths
    :return: none
    """
    for rat_folder in folders:
        try:
            print('-' * 40)
            print(rat_folder)
            name = f'{rat_folder.split("/")[5]}_5min'
            # if not os.path.exists(f'{path}/corr_dataset_{name}.pkl'):
            print(f'loading data for {name}...')
            data = pkl.load(open(f'{rat_folder}/actmat_dict.pkl', 'rb'))
            data = load_data(data, name)
            save_data(data, name, rat_folder)
            # else:
            # data = pkl.load(open(f'{path}/corr_dataset_{name}.pkl', 'rb'))

            # plot_data(data, name, path)
            # if not os.path.exists(f'{path}/Graph/corr_of_corr_{name}.png'):

            # dataset, name of plot, dividing lines between sleep/nosleep, which order, path to rat folder, additional path
            corr_corr(data, f'{name}_I', order_i, True, rat_folder, path)
            corr_corr(data, f'{name}_II', order_ii, False, rat_folder, path)

        except FileNotFoundError:
            print('No actmat found, skipping...')
        except pkl.UnpicklingError:
            print('something wrong when unpacking pickle file, skipping...')


def load_data(data, name):
    """creates dataframes of the spike matrixes using pandas
    :param data: dict of the data(opened with pickle in run_calculations)
    :param name: which rat
    :return: matrix of correlation values of data
    """
    global order_i
    global order_ii
    order_i = []
    data_tuples = []
    dataset = {}
    outdata = {}

    timebins = {'trial': ['trial1', 'trial2', 'trial3', 'trial4', 'trial5'],
                'posttrial': ['post_trial1', 'post_trial2', 'post_trial3', 'post_trial4']}
    binsnames = ['(0-5)', '(5-10)', '(10-15)', '(15-20)', '(20-25)', '(25-30)', '(30-35)', '(35-40)', '(40-45)']

    for key, val in data.items():
        key = key.replace('-', '_').lower()
        dataset[key] = {}
        for i, arr in enumerate(val):
            # if max(arr) != 0:
            dataset[key][i] = list(arr)
        dataset[key] = pd.DataFrame(dataset[key])

    for key in dataset.keys():
        if key in timebins['trial']:
            # use as is
            outdata[key] = dataset[key]

            data_tuples.append((f'{key}', int(key[-1]), 0))
        if key in timebins['posttrial']:
            # take 9 bins of 5 mins (12000)
            for bin in range(9):
                strname = f'{key}_{binsnames[bin]}'
                data_tuples.append((f'{strname}', int(key[10:11]), bin + 1))
                outdata[strname] = dataset[key].iloc[bin * 12000: (bin + 1) * 12000]

        if key == 'post_trial5':
            # split into 36 bins of 5 min (12000)
            nameitt = 0  # this is increased when bin % 9 is 0 (thats 4 times, its to keep track of the parts of pt5)
            for bin in range(36):
                if bin % 9 == 0:
                    nameitt += 1
                strname = f'PT5_{nameitt}_{binsnames[bin % 9]}'
                data_tuples.append((f'{strname}', int(key[10:11]), bin + 1))
                outdata[strname] = dataset[key].iloc[bin * 12000: (bin + 1) * 12000]

    order_i = order_list(data_tuples, 2, 1)
    order_ii = order_list(data_tuples, 1, 2)
    pkl.dump(order_i, open('order_by_timeperiod.pkl', 'wb'))
    pkl.dump(order_ii, open('order_by_realtime.pkl', 'wb'))
    return process_data(outdata)


def process_data(dataset):
    """calculates the correlation values for each time bins neurons
    :param dataset: dictionary of dataframes of spikes
    :return: dictionary of correlation values
    """
    print('processing data...')
    corrset = {}
    for key, val in dataset.items():
        corrM = val.corr()
        corrset[key] = corrM
    return corrset


def corr_corr(data, name, order, line, rat_folder='', path='/media/irene/Data/Rat_OS_EPhys_RGS14_Cell_Assembly'):
    """calculates and plots the correlation of correlation matrices
    :param data: dict of correlation values of spike matrix
    :param name: which rat
    :param rat_folder: path to save
    :return: none
    """
    print('generating correlation of correlation matrix')
    corrset = {}
    for key, val in data.items():
        corrset[key] = spatial.distance.squareform(data[key], checks=False)
    df = pd.DataFrame(corrset).fillna(0)
    df.reindex(order)
    df = df[order]
    corrM = df.corr(method='pearson')
    pkl.dump(corrM, open(f'{rat_folder}/corr_of_corr_{name}.pkl', 'wb'))
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'corr of corr {name}')
    plot = sn.heatmap(corrM, square=True, vmax=1, vmin=0)
    if line:
        plot.hlines(5, *plot.get_xlim(), colors='green', )
        plot.vlines(5, *plot.get_xlim(), colors='green', )
    plt.savefig(f'{rat_folder}/Graph/corr_of_corr_{name}.png')
    plt.savefig(f'{path}/corr_of_corr_{name}.png')
    print('Done and saved')
    plt.close()


def order_list(tuples, order1, order2):
    ordered = []
    arr = sorted(tuples, key=itemgetter(order1, order2))
    for i in arr:
        ordered.append(i[0])
    return ordered


def plot_data(dataset, name, path=''):
    """creates heatmap of each timebin's neurons based on correlation matrix
    :param dataset: dict of correlations
    :param name: which rat
    :param path: path to save
    :return: none
    """
    print('generating per period heatmaps')
    for key, val in dataset.items():
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'{key} of {name}')
        sn.heatmap(val, square=True)
        plt.savefig(f'{path}/Graph/{key}_corr_graph_{name}.png')
        plt.close()
    print('Done and saved')
    # plt.show()


def save_data(dataset, name, path=''):
    """saves corr matrxi for future use using pkl
    :param dataset: corr matrix
    :param name: which rat
    :param path: path to save
    :return: none
    """
    pkl.dump(dataset, open(f'{path}/corr_dataset_{name}.pkl', 'wb'))
    print('saved correlation matrix data')


main()
