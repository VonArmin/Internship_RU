import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from operator import itemgetter
from scipy import spatial, stats

"""this script creates matrixes of correlation between neurons in one rat and the correlation of those neurons between timebins"""

path = '/media/genzel/data/Rat_OS_EPhys_RGS14_Cell_Assembly'
order_i = []
order_ii = []
order_iii = []
iterations = 500


def main():
    folders = get_folders(path)
    run_calculations(folders)


def get_folders(abspath):
    """get subfolder in supplied path
    :param abspath: path to folders
    :return: array of strings to paths
    """
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    return subfolders


def run_calculations(folders):
    """manages the folders and wether files are created or skipped
    :param folders: array of strings of paths
    :return: none
    """
    for path in folders:
        try:
            name = path.split('/')[-1]
            file = pkl.load(open(f'{path}/graph_values_{iterations}_{name}.pkl', 'rb'))

            print('-' * 40)
            data = process_data(file)
            # data = load_data(data, name)
            # save_data(data, name)

            # plot_data(data, name)
            # if not os.path.exists(f'{path}/Graph/corr_of_corr_{name}.png'):
            corr_data = corr_corr(data, name, f'{path}/Graph')
            save_data(corr_data, name, path)
            # corr_corr(data, name, '/media/irene/Data')
        except FileNotFoundError:
            print('No actmat found, skipping...')
        except pkl.UnpicklingError:
            print('something wrong when unpacking pickle file, skipping...')


def process_data(dataset):
    """calculates the correlation values for each time bins neurons
    :param dataset: dictionary of dataframes of spikes
    :return: dictionary of correlation values
    """
    print('processing data...')
    corrset = {}
    for key, val in dataset.items():
        val = pd.DataFrame(val)

        # zscore = stats.zscore(val, ddof=1)
        # std = zscore.std(ddof=1)
        # filter = std + std + std
        corrM = val.corr()

        corrset[key] = corrM
    return corrset


def corr_corr(data, name, path):
    """calculates and plots the correlation of correlation matrixes
    :param data: dict of correlation values of spike matrix
    :param name: which rat
    :param path: path to save
    :return: none
    """
    print('generating correlation of correlation matrix')
    try:
        list = ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
                'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
        corrset = {}

        for key, val in data.items():
            corrset[key] = spatial.distance.squareform(data[key], checks=False)
        df = pd.DataFrame(corrset).fillna(0)

        # df.columns = list
        # df = df[list]

        corrM = df.corr()

        # pkl.dump(corrM, open(f'{path}/corr_of_corr_{name}.pkl', 'wb'))
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'corr of corr {name}')
        sn.heatmap(corrM, square=True, linewidth=0.1, vmax=1, vmin=0)
        # plt.show()
        print(f'{path}/corr_of_corr_{name}_shuff_{iterations}.png')
        plt.savefig(f'{path}/corr_of_corr_{name}_shuff_{iterations}.png')
        print('Done and saved')
        plt.close()
        return corrM
    except KeyError:
        print('data is malformed, skipping')
    # plt.show()


def plot_data(dataset, name, path='D:/OS Data/Graphs'):
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
        plt.savefig(f'{path}/{name}/{key}_corr_graph_{name}.png')
        plt.close()
    print('Done and saved')
    # plt.show()


def save_data(dataset, name, path):
    """saves corr matrix for future use using pkl
    :param dataset: corr matrix
    :param name: which rat
    :param path: path to save
    :return: none
    """
    pkl.dump(dataset, open(f'{path}/data_corr_of_corr_shuffled_{iterations}{name}.pkl', 'wb'))
    print('saved correlation matrix data')


main()
