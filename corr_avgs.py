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
    print('Fetching Folders...')
    vehic, rgs = bin_rats(subfolders)
    print('Filtering SDs...')
    vehfilter = filter_SD(vehic)
    rgsfilter = filter_SD(rgs)
    print('Loading Data...')

    # load raw data
    dataveh = load_data(vehfilter)
    datargs = load_data(rgsfilter)

    # calculate avg of each condition matrix
    vehavg = avg_of_matrices(dataveh, 'Vehicle')
    rgsavg = avg_of_matrices(datargs, 'RGS14')

    # combine the condition matrices
    vehcom = combine_avg_matrices(vehavg, 'Vehicle')
    rgscom = combine_avg_matrices(rgsavg, 'RGS14')

    # compare dataset with HC
    compare_by_hc(vehavg, 'Vehicle')
    compare_by_hc(rgsavg, 'RGS')

    # #substract veh data from rgs data
    # substr_combined_matrices(vehcom, rgscom)
    # substr_con_matrices(vehavg, rgsavg)
    #
    # #devide rgs data by veh data
    # divide_combined_matrices(vehcom, rgscom)
    # divide_con_matrices(vehavg, rgsavg)


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


def avg_of_matrices(dataset, name):
    """compute average per condtion for veh and rgs rats and creates heatmap
    :param dataset: raw data
    :param name: rgs or veh
    :return: avg dataset
    """
    print(f'Generating matrices of conditions for {name}')
    order = ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
            'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
    dataset_avg = {}
    for con, arr in dataset.items():
        # plt.figure(figsize=(18, 15), tight_layout=True)
        averages = pd.concat([each.stack() for each in arr], axis=1) \
            .apply(lambda x: x.mean(), axis=1) \
            .unstack()
        averages = averages[order.reverse()]
        averages = averages.reindex(order)
        # plt.title(f'average of corr of corr matrixes for condition: {con} in {name} Rats')
        # sn.heatmap(averages, square=True, linewidth=0.1, annot=True, vmax=1, vmin=0, cmap='Greys')
        # plt.savefig(f'avg_corr_of_corr_{con}_{name}.png')
        dataset_avg[con] = averages
    return dataset_avg


def combine_avg_matrices(avgdata, name):
    """compute avg for veh and rgs rats and creates heatmap
    :param avgdata: averaged data per condition
    :param name: rgs or veh
    :return: avg from avgdata
    """
    order = ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
            'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
    averages = pd.concat([each.stack() for each in avgdata.values()], axis=1) \
        .apply(lambda x: x.mean(), axis=1) \
        .unstack()
    averages = averages[order.reverse()]
    averages = averages.reindex(order)
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'average of condition corr of corr matrices for: {name}')
    sn.heatmap(averages, square=True, linewidth=0.1, annot=True, vmax=1, vmin=0, cmap='Greys')
    plt.savefig(f'CoC_combined_con_{name}.png')
    return averages


def compare_by_hc(data, name):
    hc = data['HC']
    averages = dict((key, data[key]) for key in ['CON', 'OD', 'OR'])
    for con in averages:
        data = averages[con].div(hc)
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'divided matrices for corr of corr {name} ({con} / HC)')
        sn.heatmap(data, square=True, linewidth=0.1, annot=True, vmax=2, vmin=0, cmap='coolwarm')
        plt.savefig(f'divided_matrix_{name}_{con}_by_HC.png')
        save_data(data, f'data_matrix_{name}_{con}_by_HC')

    allcon = pd.concat([each.stack() for each in averages.values()], axis=1) \
        .apply(lambda x: x.mean(), axis=1) \
        .unstack()
    data = allcon.div(hc)
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'divided matrices for corr of corr {name} (avg / HC)')
    sn.heatmap(data, square=True, linewidth=0.1, annot=True, vmax=2, vmin=0, cmap='coolwarm')
    plt.savefig(f'divided_matrix_{name}_all_by_HC.png')
    save_data(data, f'divided_matrix_{name}_all_by_HC')
    plt.show()


def substr_combined_matrices(vehdata, rgsdata):
    """subtracts veh data from rgs data and creates heatmap
    :param vehdata: veh data
    :param rgsdata: rgs data
    :return: none
    """
    data = rgsdata.subtract(vehdata)
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'substracted matrices for corr of corr (rgs - veh) all con')
    sn.heatmap(data, square=True, linewidth=0.1, annot=True, vmax=0.3, vmin=-0.3, cmap='Greys')
    plt.savefig(f'subtracted_matrix_all_con.png')


def substr_con_matrices(vehdata, rgsdata):
    """subtracts veh data from rgs and creates heatmap per con
    :param vehdata: veh data
    :param rgsdata: rgs data
    :return: none
    """
    for con in vehdata:
        data = rgsdata[con].subtract(vehdata[con])
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'subtracted matrices for condition: {con}, (rgs - veh)')
        sn.heatmap(data, square=True, linewidth=0.1, annot=True, vmax=0.3, vmin=-0.3, cmap='Greys')
        plt.savefig(f'subtracted_matrix_{con}.png')


def divide_combined_matrices(vehdata, rgsdata):
    """divide rgs data by veh data and creates heatmap
    :param vehdata: veh data
    :param rgsdata: rgs data
    :return: none
    """
    data = rgsdata.div(vehdata)
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'divided matrices for corr of corr (rgs - veh) all con')
    sn.heatmap(data, square=True, linewidth=0.1, annot=True, vmax=2, vmin=0, cmap='coolwarm')
    plt.savefig(f'divided_matrix_all_con.png')


def divide_con_matrices(vehdata, rgsdata):
    """divide rgs data by veh data per con and creates heatmap
    :param vehdata: veh data
    :param rgsdata: rgs data
    :return: none
    """
    for con in vehdata:
        data = rgsdata[con].div(vehdata[con])
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'divided matrices for condition: {con}, (rgs - veh)')
        sn.heatmap(data, square=True, linewidth=0.1, annot=True, vmax=2, vmin=0, cmap='coolwarm')
        plt.savefig(f'divided_matrix_{con}.png')


def save_data(data: pd.DataFrame, name):
    data.to_csv(path_or_buf=f'{name}.csv', sep=',')
    data.to_pickle(f'{name}.pkl')


main()
