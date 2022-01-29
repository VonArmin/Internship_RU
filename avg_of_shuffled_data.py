import pickle as pkl
import numpy
import numpy as np
import pandas
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import seaborn as sn
import os.path
from operator import itemgetter
from scipy import spatial, stats

"""this script find the average of the shuffled datasets
it finds all the folders in the path, loads the graph_values_{iterations}_{foldername}.pkl file 
and find the average of veh and rgs rats separately"""

iterations = 500
path = '/media/genzel/data/Rat_OS_EPhys_RGS14_Cell_Assembly'
rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}


def main():
    subfolders = get_folders_loc(path)
    rgsdata, vehdata = load_data(subfolders)
    print('rgs data')
    rgs_avgs = find_avgs(rgsdata)
    print('veh data')
    veh_avgs = find_avgs(vehdata)
    plot_heatmap(rgs_avgs, 'RGS14')
    plot_heatmap(veh_avgs, 'Vehicle')
    # plot_bars(rgs_avgs, veh_avgs)
    # plot_hist(rgs_avgs, veh_avgs)


def get_folders_loc(abspath):
    """get subfolder in supplied path
    :param abspath: path to folders
    :return: array of strings to paths
    """
    files = [f.path for f in os.scandir(abspath) if f.is_dir()]
    return files


def load_data(folders):
    """data is stored in a nested dictionary: {rgs/vehicle: {study-day:2d-array of distances}}
    :param folders:
    :return:
    """
    rgsdata = {}
    vehdata = {}
    for folder in folders:
        try:
            name = folder.split('/')[-1]
            data = pkl.load(open(f'{folder}/data_corr_of_corr_shuffled_{iterations}{name}.pkl', 'rb'))
            ratnr = int(name.split('_')[0][3:4])
            data = pd.DataFrame(data).fillna(0)

            if ratnr in rats['vehicle']:
                vehdata[name.strip('.pkl')] = data
            if ratnr in rats['rgs']:
                rgsdata[name.strip('.pkl')] = data
        except FileNotFoundError:
            pass
    return rgsdata, vehdata


def find_avgs(data):
    # for sd, df in data.items():
    #     # this will calculate the average of all the trials into a df of the values per sd
    #     trial_averages = pd.concat([each.stack() for each in df.values()], axis=1) \
    #         .apply(lambda x: x.mean(), axis=1) \
    #         .unstack()
    #     data_avgs[sd] = trial_averages

    sd_averages = pd.concat([each.stack() for each in data.values()], axis=1) \
        .apply(lambda x: x.mean(), axis=1) \
        .unstack()
    return sd_averages
    # print(sd_averages)
    # for key, df in data_avgs.items():
    #     print(f'{key}\n{df}\n')


def plot_heatmap(data, name):
    avg = data.stack().mean()
    plt.figure(figsize=[20, 20])
    plt.title(f'avg of distances per neuron for: {name}, Mean: {avg}')
    sn.heatmap(data, square=True, vmax=0.2, vmin=-0.2,cmap='coolwarm')
    plt.xlabel('time period')
    plt.ylabel('time period')
    plt.savefig(f'{path}/corr_of_corr_{name}_shuffled.png')
    plt.show()
    # pass


def plot_bars(rgs, veh):
    rgs_sq = spatial.distance.squareform(rgs, checks=False, force='tovector')
    veh_sq = spatial.distance.squareform(veh, checks=False, force='tovector')
    rgs_data = rgs_sq
    veh_data = veh_sq
    plt.figure(figsize=[15, 15])
    plt.title('Averages of Vehicle and RGS distance correlations')
    plt.bar(['Vehicle', 'RGS14'],
            [veh_data.mean(), rgs_data.mean()],
            yerr=[scipy.stats.sem(veh_data, ddof=1, nan_policy='omit'),
                  scipy.stats.sem(rgs_data, ddof=1, nan_policy='omit')],
            capsize=5)
    plt.xlabel('Animals')
    plt.ylabel('Average')
    plt.show()


def plot_hist(rgs, veh):
    points = 20
    rgs = spatial.distance.squareform(rgs, checks=False, force='tovector')
    veh = spatial.distance.squareform(veh, checks=False, force='tovector')
    hist_rgs = {}
    hist_veh = {}
    hist_range = np.arange(min(min(rgs), min(veh)), max(max(rgs), max(veh)),
                           ((abs(min(min(rgs), min(veh))) + max(max(rgs), max(veh))) / points))

    print(hist_range)

    for i in range(0, points - 1, 1):
        hist_rgs[f'{round(hist_range[i], 2)} : {round(hist_range[i + 1], 2)}'] = 0
        hist_veh[f'{round(hist_range[i], 2)} : {round(hist_range[i + 1], 2)}'] = 0

        for ii in rgs:
            if hist_range[i] <= ii <= hist_range[i + 1]:
                hist_rgs[f'{round(hist_range[i], 2)} : {round(hist_range[i + 1], 2)}'] += 1

        for ii in veh:
            if hist_range[i] <= ii <= hist_range[i + 1]:
                hist_veh[f'{round(hist_range[i], 2)} : {round(hist_range[i + 1], 2)}'] += 1

    print(hist_rgs.values())
    # plt.figure(figsize=[15, 15])
    # plt.title('Distribution of values of RGS and Vehicle')
    # plt.bar(height=hist_rgs.values(), x=hist_rgs.keys(), alpha=0.3, label='RGS', color='red')
    # plt.bar(height=hist_veh.values(), x=hist_rgs.keys(), alpha=0.3, label='Vehicle', color='blue')
    # plt.xticks(rotation=30, ha='right')
    # plt.legend()
    # plt.ylabel('amount of values')
    # plt.xlabel('range')
    # plt.show()
    # print(hist_range)
    print('Krusal p-value:                      ', scipy.stats.kruskal(list(hist_rgs.values()), list(hist_veh.values())))
    print('two-sample Kolmogorov-Smirnov p-value:',
          scipy.stats.ks_2samp(list(hist_rgs.values()), list(hist_veh.values())))


main()
