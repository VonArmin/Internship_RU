import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from scipy import spatial

"""this script creates matrixes of correlation between neurons in one rat and the correlation of those neurons between timebins"""

path = ''


def main():
    # folders = create_folders(path)
    # run_calculations(folders)
    single_set()


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
    for path in folders:
        try:
            print('-' * 40)
            name = f'{path.split(" / ")[5]}'
            if not os.path.exists(f'{path}/corr_dataset_{name}.pkl'):
                print(f'loading data for {name}...')
                data = pkl.load(open(f'{path}/actmat_dict.pkl', 'rb'))
                data = load_data(data, name)
                save_data(data, name, path)
            else:
                data = pkl.load(open(f'{path}/corr_dataset_{name}.pkl', 'rb'))
            if not os.path.exists(f'{path}/Graph/PT5_part4_corr_graph_{name}.png'):
                plot_data(data, name, path)
            if not os.path.exists(f'{path}/Graph/corr_of_corr_{name}.png'):
                corr_corr(data, name, path)
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
    dataset = {}
    for key, val in data.items():
        key = key.replace('-', '_').lower()
        dataset[key] = {}
        for i, arr in enumerate(val):
            # if max(arr) != 0:
            dataset[key][i] = list(arr)
        dataset[key] = pd.DataFrame(dataset[key])
    key = list(dataset.keys())[9]
    for i in range(4):
        dataset[f'PT5_part{i + 1}'] = dataset[key].iloc[i * 108000: (i + 1) * 108000]
    dataset.pop(key)

    return process_data(dataset)


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


def corr_corr(data, name, path=''):
    """calculates and plots the correlation of correlation matrixes
    :param data: dict of correlation values of spike matrix
    :param name: which rat
    :param path: path to save
    :return: none
    """
    print('generating correlation of correlation matrix')
    # try:
    list = ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
            'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
    corrset = {}
    for key, val in data.items():
        # corrset[key] = np.array(data[key]).flatten()
        corrset[key] = spatial.distance.squareform(data[key], checks=False)
    df = pd.DataFrame(corrset).fillna(0)
    df.columns = list
    df = df[list]
    # df = df[list]
    corrM = df.corr()
    pkl.dump(corrM, open(f'{path}/corr_of_corr_{name}.pkl', 'wb'))
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'corr of corr {name}')
    sn.heatmap(corrM, square=True, linewidth=0.1, annot=True, vmax=0.7, vmin=0)
    plt.savefig(f'{path}/Graphs/corr_of_corr_{name}.png')
    print('Done and saved')
    plt.close()
    # except KeyError:
    #     print('data is malformed, skipping')
    # plt.show()


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
        plt.savefig(f'{path}/Graphs/{key}_corr_graph_{name}.png')
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
