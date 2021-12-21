import pickle as pkl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path
from operator import itemgetter
from scipy import spatial, stats

"""this script loads an actmat_dict.pkl file and randomizes the order of the spikes for each neuron, 
fetches the std and mean for each randomized neuron and compares it with the original file"""

iterations = 500
keys = []
path = '/media/irene/Data/Rat_OS_EPhys_RGS14_Cell_Assembly'
order_i = []
order_ii = []
order_iii = []


def main():
    run_multiple()
    #run_task('rat3_SD14_shuff', pkl.load(open('actmat_dict.pkl', 'rb')), path)


def run_multiple():
    folders = get_folders(path)
    for folder in folders:
        try:
            rat = folder.split('/')[-1]
            file = pkl.load(open(f'{folder}/actmat_dict.pkl', 'rb'))
            run_task(rat, file, folder)
        except FileNotFoundError:
            print('no actmat found for:', rat)

        except pkl.UnpicklingError:
            print('something wrong when unpacking pickle file, skipping...')

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
    """run a single rat with the supplied file name and path to save to
    :param name: which rat
    :param file: actmat
    :param path: path to save to
    :return: none
    """
    print('-' * 50)
    print(f'running: {name}')
    dataset = load_data(file, name)
    randomized_data = randomize_timebins(dataset)
    stds, means = find_distribution(randomized_data)
    values = compare_with_org(stds, means, get_corr(dataset), name, path)
    save_data(stds, means, values, name, path)


def load_data(data, name):
    """creates dataframes of the spike matrixes using pandas
    :param data: dict of the data(opened with pickle in run_calculations)
    :param name: which rat
    :return: matrix of correlation values of data
    """
    global order_i
    global order_ii
    global keys
    order_i = []
    data_tuples = []
    dataset = {}
    outdata = {}

    timebins = {'trial': ['trial1', 'trial2', 'trial3', 'trial4', 'trial5'],
                'posttrial': ['post_trial1', 'post_trial2', 'post_trial3', 'post_trial4']}
    binnames = ['(0-5)', '(5-10)', '(10-15)', '(15-20)', '(20-25)', '(25-30)', '(30-35)', '(35-40)', '(40-45)']

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
                strname = f'{key}_{binnames[bin]}'
                data_tuples.append((f'{strname}', int(key[10:11]), bin + 1))
                outdata[strname] = dataset[key].iloc[bin * 12000: (bin + 1) * 12000]

        if key == 'post_trial5':
            # split into 36 bins of 5 min (12000)
            nameitt = 0  # this is increased when bin % 9 is 0 (thats 4 times, its to keep track of the parts of pt5)
            for bin in range(36):
                if bin % 9 == 0:
                    nameitt += 1
                strname = f'PT5_{nameitt}_{binnames[bin % 9]}'
                data_tuples.append((f'{strname}', int(key[10:11]), bin + 1))
                outdata[strname] = dataset[key].iloc[bin * 12000: (bin + 1) * 12000]
    
    order_i = order_list(data_tuples, 2, 1)
    order_ii = order_list(data_tuples, 1, 2)
    keys = outdata.keys()
    pkl.dump(order_i, open('order_by_timeperiod.pkl', 'wb'))
    pkl.dump(order_ii, open('order_by_realtime.pkl', 'wb'))
    return outdata


def randomize_timebins(data):
    """randomizes the order of the rows
    :param data: data to shuffle
    :return: shuffled data
    """
    print('Randomizing: ')
    randomized_matrices = {}
    for i in range(iterations):
        if i % 25 == 0:
            print('run:', i)

        for key, df in data.items():
            for col in df.columns:
                df[col] = df[col].sample(frac=1).reset_index(drop=True)
            randomized_matrices[f'{key} {i}'] = spatial.distance.squareform(df.corr(method='pearson'), checks=False,
                                                                            force='tovector')
    print('Done!')
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
    global keys
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
    print('plotting...')
    for key in keys:
        values[key] = spatial.distance.squareform(values[key], checks=False, force='tomatrix')
        #plt.figure(figsize=(18, 15))
        #sn.heatmap(values[key], square=True, cmap='coolwarm', center=0)
        #plt.title(f'correlation data: (original-shuffled mean) / shuffled std, {key}, {iterations} iterations, {name}')
        #plt.xlabel('Neuron #')
        #plt.ylabel('Neuron #')
        #plt.savefig(f'{path}/shuffled_{key}_{iterations}_{name}.png')
        #plt.close()
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


def order_list(tuples, order1, order2):
    """order supplied tuples based on order 1 and 2
    :param tuples: (timebin, int1, int2)
    :param order1:int used to sort
    :param order2: int used to sort
    :return: ordered list
    """
    ordered = []
    arr = sorted(tuples, key=itemgetter(order1, order2))
    for i in arr:
        ordered.append(i[0])
    return ordered


def save_data(stds, means, vals, name, path=''):
    """dave all data
    :param stds: std values
    :param means: mean values
    :param vals: original values
    :param name: which rat
    :param path: path to save to
    :return:
    """
    print('Saving...')
    pkl.dump(stds, open(f'{path}/stds_{iterations}_{name}.pkl', 'wb'))
    pkl.dump(means, open(f'{path}/means_{iterations}_{name}.pkl', 'wb'))
    pkl.dump(vals, open(f'{path}/graph_values_{iterations}_{name}.pkl', 'wb'))
    print('Done!')


main()
