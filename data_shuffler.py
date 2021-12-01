import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from scipy import spatial, stats

"""this script loads an actmat_dict.pkl file and randomizes the order of the spikes for each neuron, 
fetches the std and mean for each randomized neuron and compares it with the original file"""

iterations = 5
keys = []
file = pkl.load(open('actmat_dict.pkl', 'rb'))


def main():
    # new_run()
    dataset = load_data(file)
    plot_existing(pkl.load(open('graph_values_5.pkl', 'rb')))
    # dataset = load_data(file)
    # stds = pkl.load(open(f'stds_{iterations}.pkl', 'rb'))
    # means = pkl.load(open(f'means_{iterations}.pkl', 'rb'))
    # compare_with_org(stds, means, get_corr(dataset))


def new_run():
    dataset = load_data(file)
    randomized_data = randomize_timebins(dataset)
    stds, means = find_distribution(randomized_data)
    compare_with_org(stds, means, get_corr(dataset))


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
    matrices = {}
    for key, arr in data.items():
        matrices[key] = spatial.distance.squareform(arr.corr(method='pearson'), checks=False, force='tovector')
    return matrices


def find_distribution(data):
    stds = {}
    means = {}
    len_of_arr = len(data['trial1 0'])
    for key in keys:
        values_stds = []
        values_means = []
        for neuron in range(len_of_arr):
            neuron_vals = []
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


def compare_with_org(stds, means, original):
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
        plt.title(f'correlation data: (original-shuffled mean) / shuffled std, {key}, {iterations} iterations')
        plt.xlabel('Neuron #')
        plt.ylabel('Neuron #')
        plt.savefig(f'shuffled_{key}_{iterations}.png')

    plt.show()
    save_data(stds, means, values)


def plot_existing(data):
    print('plotting')
    for key in keys:
        plt.figure(figsize=(18, 15))
        sn.heatmap(data[key], square=True, cmap='coolwarm', center=0)
        plt.title(f'correlation data: (original-shuffled mean) / shuffled std, {key}, {iterations} iterations')
        plt.xlabel('Neuron #')
        plt.ylabel('Neuron #')
        plt.savefig(f'shuffled_{key}_{iterations}.png')
    plt.show()


def save_data(stds, means, vals):
    pkl.dump(stds, open(f'stds_{iterations}.pkl', 'wb'))
    pkl.dump(means, open(f'means_{iterations}.pkl', 'wb'))
    pkl.dump(vals, open(f'graph_values_{iterations}.pkl', 'wb'))


main()
