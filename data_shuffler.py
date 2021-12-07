import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from scipy import spatial, stats

"""this script loads an actmat_dict.pkl file and randomizes the order of the spikes for each neuron, 
fetches the std and mean for each randomized neuron and compares it with the original file"""

iterations = 500
keys = []
file = pkl.load(open('actmat_dict.pkl', 'rb'))
path = '/media/irene/Data/Rat_OS_EPhys_RGS14_Cell_Assembly'


def main():
    folders = get_folders(path)
    for folder in folders:
        file = pkl.load(open(f'{folder}/actmat_dict.pkl', 'rb'))
        rat = folder.split('/')[-1]
        run_task(rat, file, folder)
    # dataset = load_data(file)
    # plot_existing(pkl.load(open('graph_values_5.pkl', 'rb')))
    # dataset = load_data(file)
    # stds = pkl.load(open(f'stds_{iterations}.pkl', 'rb'))
    # means = pkl.load(open(f'means_{iterations}.pkl', 'rb'))
    # compare_with_org(stds, means, get_corr(dataset))


def get_folders(abspath):
    """get subfolder in supplied path
    :param abspath: path to folders
    :return: array of strings to paths
    """
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    return subfolders


def run_task(name, file, path):
    """run a single rat with the supplied filen name and path to save to
    :param name: which rat
    :param file: actmat
    :param path: path to save to
    :return: none
    """
    dataset = load_data(file)
    randomized_data = randomize_timebins(dataset)
    stds, means = find_distribution(randomized_data)
    values = compare_with_org(stds, means, get_corr(dataset), path)
    save_data(stds, means, values, name, path)


def load_data(data):
    """creates dataframes of the spike matrixes using pandas
    :param data: dict of the data(opened with pickle in run_calculations)
    :param name: which rat
    :return: matrix of correlation values of data
    """
    global keys
    print('loading data...')
    dataset = {}
    for key, val in data.items():
        key = key.replace('-', '_').lower()
        dataset[key] = {}
        for i, arr in enumerate(val):
            # if max(arr) != 0:
            dataset[key][i] = list(arr)
        dataset[key] = pd.DataFrame(dataset[key])
    key = 'post_trial5'
    for i in range(4):
        dataset[f'PT5_part{i + 1}'] = dataset[key].iloc[i * 108000: (i + 1) * 108000].reset_index(drop=True)
    dataset.pop(key)
    keys = dataset.keys()
    return dataset


def randomize_timebins(data):
    """randomizes the order of the rows
    :param data: data to shuffle
    :return: shuffled data
    """
    randomized_matrices = {}
    for i in range(iterations):
        print('run:', i + 1)
        for key, df in data.items():
            for col in df.columns:
                df[col] = df[col].sample(frac=1).reset_index(drop=True)
            randomized_matrices[f'{key} {i}'] = spatial.distance.squareform(df.corr(method='pearson'), checks=False,
                                                                            force='tovector')
    return randomized_matrices


def get_corr(data):
    """calculates the correlation of the amtrix
    :param data: data
    :return:
    """
    matrices = {}
    for key, arr in data.items():
        matrices[key] = spatial.distance.squareform(arr.corr(method='pearson'), checks=False, force='tovector')
    return matrices


def find_distribution(data):
    """iterates through data and fetches std and means
    :param data:
    :return:
    """
    stds = {}
    means = {}
    len_of_arr = len(data['trial1 0'])
    for key in keys:
        values_stds = []  # storage of stds for a matrix
        values_means = []  # storage of means for a matrix
        for neuron in range(len_of_arr):
            neuron_vals = []  # storage for means of a neuron
            for iteration in range(iterations):
                neuron_vals.append(data[f'{key} {iteration}'][neuron])
            std, mean = get_std_mean(neuron_vals)
            values_stds.append(std)
            values_means.append(mean)
        stds[key] = values_stds
        means[key] = values_means
    return stds, means


def get_std_mean(data: list):
    return np.std(data), np.mean(data)


def compare_with_org(stds, means, original, name, path):
    """calculates the distance of the randomized data to the original data according to:
        (original value - shuffled mean) / shuffled standard deviation
    :param stds: df of shuffled stds
    :param means: df of shuffled means
    :param original: original corr values
    :param name: which rat
    :param path: path to save to
    :return: dict of actual distances between shuffled and original
    """
    values = {}
    print('calculating...')
    for key in keys:
        values[key] = []
        for neuron in range(len(stds[key])):
            value = (original[key][neuron] - means[key][neuron]) / stds[key][neuron]
            values[key].append(value)
    print('plotting')
    for key in keys:
        values[key] = spatial.distance.squareform(values[key], checks=False, force='tomatrix')
        plt.figure(figsize=(18, 15))
        sn.heatmap(values[key], square=True, cmap='coolwarm', center=0)
        plt.title(f'correlation data: (original-shuffled mean) / shuffled std, {key}, {iterations} iterations, {name}')
        plt.xlabel('Neuron #')
        plt.ylabel('Neuron #')
        plt.savefig(f'{path}/shuffled_{key}_{iterations}_{name}.png')

    plt.show()
    return values
    # save_data(stds, means, values)


def plot_existing(data):
    """plot an existing pkl file
    :param data:
    :return:
    """
    print('plotting')
    for key in keys:
        plt.figure(figsize=(18, 15))
        sn.heatmap(data[key], square=True, cmap='coolwarm', center=0)
        plt.title(f'correlation data: (original-shuffled mean) / shuffled std, {key}, {iterations} iterations')
        plt.xlabel('Neuron #')
        plt.ylabel('Neuron #')
        plt.savefig(f'shuffled_{key}_{iterations}.png')
    plt.show()


def save_data(stds, means, vals, name, path):
    """dave all data
    :param stds: std values
    :param means: mean values
    :param vals: original values
    :param name: which rat
    :param path: path to save to
    :return:
    """
    pkl.dump(stds, open(f'{path}/stds_{iterations}_{name}.pkl', 'wb'))
    pkl.dump(means, open(f'{path}/means_{iterations}_{name}.pkl', 'wb'))
    pkl.dump(vals, open(f'{path}/graph_values_{iterations}_{name}.pkl', 'wb'))


main()
