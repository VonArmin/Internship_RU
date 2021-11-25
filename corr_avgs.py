import pickle as pkl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import os.path

'''this fetches all correlation of correlation files and
plots them into averages per condition and per condition split between rgs and veh'''

rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}
order_i = pkl.load(open('order_by_timeperiod.pkl', 'rb'))
order_ii = pkl.load(open('order_by_realtime.pkl', 'rb'))


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
    vehavgper = avg_of_matrices(dataveh, 'Vehicle', order_i)
    rgsavgper = avg_of_matrices(datargs, 'RGS14', order_i)
    vehavgrt = avg_of_matrices(dataveh, 'Vehicle', order_ii)
    rgsavgrt = avg_of_matrices(datargs, 'RGS14', order_ii)

    # combine the condition matrices
    vehcomper = combine_avg_matrices(vehavgper, 'Vehicle', order_i, 'per')
    rgscomper = combine_avg_matrices(rgsavgper, 'RGS14', order_i, 'per')
    vehcomrt = combine_avg_matrices(vehavgrt, 'Vehicle', order_ii, 'rt')
    rgscomrt = combine_avg_matrices(rgsavgrt, 'RGS14', order_ii, 'rt')

    # compare dataset with HC
    compare_by_hc(vehavgper, 'Vehicle', 'per')
    compare_by_hc(rgsavgper, 'RGS', 'per')
    compare_by_hc(vehavgrt, 'Vehicle', 'rt')
    compare_by_hc(rgsavgrt, 'RGS', 'rt')

    # #substract veh data from rgs data
    # substr_combined_matrices(vehcomper, rgscomper)
    # substr_con_matrices(vehavgper, rgsavgper)

    # #devide rgs data by veh data
    divide_combined_matrices(vehcomper, rgscomper, 'per')
    divide_con_matrices(vehavgper, rgsavgper, 'per')
    divide_combined_matrices(vehcomrt, rgscomrt, 'rt')
    divide_con_matrices(vehavgrt, rgsavgrt, 'rt')


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
                with open(f'{path}/corr_of_corr_{name}_5min_I.pkl', 'rb') as file:
                    pkldata = pkl.load(file)
                    data[condition].append(pkldata)
            except FileNotFoundError:
                pass
    return data


def avg_of_matrices(dataset, name, order):
    """compute average per condtion for veh and rgs rats and creates heatmap
    :param dataset: raw data
    :param name: rgs or veh
    :return: avg dataset
    """
    print(f'Generating matrices of conditions for {name}')

    dataset_avg = {}
    for con, arr in dataset.items():
        averages = pd.concat([each.stack() for each in arr], axis=1) \
            .apply(lambda x: x.mean(), axis=1) \
            .unstack()
        averages = averages.reindex(order)
        averages = averages[order]
        dataset_avg[con] = averages
    return dataset_avg


def combine_avg_matrices(avgdata, name, order, time):
    """compute avg for veh and rgs rats and creates heatmap
    :param avgdata: averaged data per condition
    :param name: rgs or veh
    :return: avg from avgdata
    """
    print(f'generate average matrix for {name}, {time}')
    averages = pd.concat([each.stack() for each in avgdata.values()], axis=1) \
        .apply(lambda x: x.mean(), axis=1) \
        .unstack()
    averages = averages.reindex(order)
    averages = averages[order]
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'average of condition corr of corr matrices for: {name}')
    plot = sn.heatmap(averages, square=True, vmax=1, vmin=0, cmap='Greys')
    if time == 'per':
        plot.hlines(5, *plot.get_xlim(), colors='green', )
        plot.vlines(5, *plot.get_xlim(), colors='green', )
    plt.savefig(f'CoC_combined_con_{name}_{time}.png')
    plt.close()
    return averages


def compare_by_hc(data, name, time):
    """compare data by deviding all but HC by HC matrix
    :param data: dataset
    :param name: name of analysis
    :return: none
    """
    print(f'generating figures for contions/HC for {name}, {time}')
    hc = data['HC']
    averages = dict((key, data[key]) for key in ['CON', 'OD', 'OR'])
    for con in averages:
        data = averages[con].div(hc)
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'divided matrices for corr of corr {name} ({con} / HC)')
        plot = sn.heatmap(data, square=True, vmax=2, vmin=0, cmap='coolwarm')
        if time == 'per':
            plot.hlines(5, *plot.get_xlim(), colors='green', )
            plot.vlines(5, *plot.get_xlim(), colors='green', )
        plt.savefig(f'divided_matrix_{name}_{con}_by_HC_{time}.png')

        save_data(data, f'data_matrix_{name}_{con}_by_HC')
    plt.close()
    allcon = pd.concat([each.stack() for each in averages.values()], axis=1) \
        .apply(lambda x: x.mean(), axis=1) \
        .unstack()
    data = allcon.div(hc)
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'divided matrices for corr of corr {name} (avg / HC)')
    plot = sn.heatmap(data, square=True, vmax=2, vmin=0, cmap='coolwarm')
    if time == 'per':
        plot.hlines(5, *plot.get_xlim(), colors='green', )
        plot.vlines(5, *plot.get_xlim(), colors='green', )
    plt.savefig(f'divided_matrix_{name}_all_by_HC_{time}.png')
    save_data(data, f'divided_matrix_{name}_all_by_HC')
    plt.close()


def divide_combined_matrices(vehdata, rgsdata, time):
    """divide rgs data by veh data and creates heatmap
    :param vehdata: veh data
    :param rgsdata: rgs data
    :return: none
    """
    print(f'combining rgs and veh data still conditions/HC for {time}')
    data = rgsdata.div(vehdata)
    plt.figure(figsize=(18, 15), tight_layout=True)
    plt.title(f'divided matrices for corr of corr (rgs / veh) all con')
    plot = sn.heatmap(data, square=True, vmax=2, vmin=0, cmap='coolwarm')
    if time == 'per':
        plot.hlines(5, *plot.get_xlim(), colors='green', )
        plot.vlines(5, *plot.get_xlim(), colors='green', )
    plt.savefig(f'divided_matrix_all_con_{time}.png')
    plt.close()


def divide_con_matrices(vehdata, rgsdata, time):
    """divide rgs data by veh data per con and creates heatmap
    :param vehdata: veh data
    :param rgsdata: rgs data
    :return: none
    """
    print(f'generating figures with RGS/veh for individual conditions for {time}')
    for con in vehdata:
        data = rgsdata[con].div(vehdata[con])
        plt.figure(figsize=(18, 15), tight_layout=True)
        plt.title(f'divided matrices for condition: {con}, (rgs / veh)')
        plot = sn.heatmap(data, square=True, vmax=2, vmin=0, cmap='coolwarm')
        if time == 'per':
            plot.hlines(5, *plot.get_xlim(), colors='green', )
            plot.vlines(5, *plot.get_xlim(), colors='green', )
        plt.savefig(f'divided_matrix_{con}_{time}.png')
        plt.close()


def save_data(data: pd.DataFrame, name):
    data.to_csv(path_or_buf=f'{name}.csv', sep=',')
    data.to_pickle(f'{name}.pkl')


# def substr_combined_matrices(vehdata, rgsdata):
#     """subtracts veh data from rgs data and creates heatmap
#     :param vehdata: veh data
#     :param rgsdata: rgs data
#     :return: none
#     """
#     data = rgsdata.subtract(vehdata)
#     plt.figure(figsize=(18, 15), tight_layout=True)
#     plt.title(f'substracted matrices for corr of corr (rgs - veh) all con')
#     sn.heatmap(data, square=True, vmax=0.3, vmin=-0.3, cmap='Greys')
#     plt.savefig(f'subtracted_matrix_all_con.png')
#     plt.close()
#
#
# def substr_con_matrices(vehdata, rgsdata):
#     """subtracts veh data from rgs and creates heatmap per con
#     :param vehdata: veh data
#     :param rgsdata: rgs data
#     :return: none
#     """
#     for con in vehdata:
#         data = rgsdata[con].subtract(vehdata[con])
#         plt.figure(figsize=(18, 15), tight_layout=True)
#         plt.title(f'subtracted matrices for condition: {con}, (rgs - veh)')
#         sn.heatmap(data, square=True, vmax=0.3, vmin=-0.3, cmap='Greys')
#         plt.savefig(f'subtracted_matrix_{con}.png')
#         plt.close()
main()
