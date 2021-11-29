import matplotlib.pyplot as plt
import numpy as np
"""this script generates plots with the data from combine_data_per_condition"""

vehic_file = 'vehicle_combined.csv'
rgs_file = 'RGS14_combined.csv'


def main():

    rgs_data = create_data_dict(rgs_file)
    rgs_sems = get_sems(rgs_data)
    rgs_processed = process_data(rgs_data)
    # single_fig(rgs_processed, rgs_sems, 'RGS14 Rats')
    # plot_data(rgs_processed, rgs_sems, 'RGS14 Rats')

    vehic_data = create_data_dict(vehic_file)
    vehic_processed = process_data(vehic_data)
    vehic_sems = get_sems(vehic_data)
    # single_fig(vehic_processed, vehic_sems, 'Vehicle Rats')
    # plot_data(vehic_processed, vehic_sems, 'Vehicle Rats')

    average_per_bin(rgs_processed, vehic_processed)
    trial_cols = [1, 3, 5, 7, 9]
    pt_cols = [2, 4, 6, 8]
    pt5_cols = [10, 11, 12, 13]

    custom_batch(rgs_processed, rgs_sems, vehic_processed, vehic_sems, trial_cols, 'trials')
    custom_batch(rgs_processed, rgs_sems, vehic_processed, vehic_sems, pt_cols, 'post-trials')
    custom_batch(rgs_processed, rgs_sems, vehic_processed, vehic_sems, pt5_cols, 'post-trial 5')
    # custom_batch(rgs_processed, rgs_sems, vehic_processed, vehic_sems, range(14), 'all_trials')

    # dump_data(rgs_processed, 'rgs_processed_data.csv')
    # dump_data(vehic_processed,'vehic_processed_data.csv')


def dump_data(data, file):
    with open(file, 'w') as file:
        file.write(
            "Condition,Pre-sleep,Trial1,Post-Trial1,Trial2,Post-Trial2,Trial3,Post-Trial3,Trial4,Post-Trial4,Trial5,PT5_part1,PT5_part2,PT5_part3,PT5_part4\n")
        for key in data.keys():
            line = '{},' * 15
            line = line.format(key, data[key][0], data[key][1], data[key][2], data[key][3], data[key][4], data[key][5],
                               data[key][6], data[key][7], data[key][8], data[key][9], data[key][10], data[key][11],
                               data[key][12], data[key][13], data[key][4])
            line.strip(',')
            line += '\n'
            file.write(line)


def create_data_dict(infile):
    """reads data from file and stores it in a dict
    :param infile: file to read
    :return: dict of data
    """
    dataset = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    with open(infile, 'r') as file:
        for line in file:
            if not line.startswith('Rat'):
                line = line.strip('\n')
                line = line.split(',')
                data = line[4:]
                if line[2] == 'OD':
                    dataset['OD'].append(data)
                if line[2] == 'OR':
                    dataset['OR'].append(data)
                if line[2] == 'HC':
                    dataset['HC'].append(data)
                if line[2] == 'CON':
                    dataset['CON'].append(data)
    return dataset

def process_data(data):
    """reads data and calculates average for each column in each condition
    :param data: dict of data
    :return: dict of all avg data
    """
    data_dict = {}
    for key in data.keys():
        temp_arr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        val = len(data[key])
        for arr in data[key]:
            for i in range(14):
                temp_arr[i] += float(arr[i])
        for i, sum in enumerate(temp_arr):
            try:
                temp_arr[i] /= val
            except ZeroDivisionError:
                pass
        data_dict[key] = temp_arr
    return data_dict

def get_sems(data):
    """generate SEm (standard error of mean) data
    :param data: dict of all data
    :return: dict with SEm for each point
    """
    sems = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for key in data.keys():
        for i in range(14):
            list = []
            for ii in range(len(data[key])):
                list.append(float(data[key][ii][i]))
            sems[key].append(get_sem(list))
    # sem = np.std(data, ddof=1) / np.sqrt(np.size(data))
    return sems


def get_sem(list):
    """calculate SEm(standard error of mean) of the list
    :param list: array of data
    :return: SEm
    """
    return np.std(list, ddof=1) / np.sqrt(np.size(list))





def custom_batch(rgs_data, rgs_sems, vehic_data, vehic_sems, cols, text):
    """generate a graph with specific columns (so for specific time bins)
    :param rgs_data: dict of rgs14 rats data
    :param rgs_sems: dict of SEm data from rgs rats
    :param vehic_data: dict of rgs14 rats data
    :param vehic_sems: dict of SEm data from vehic rats
    :param cols: array of columns to plot
    :param text: name of the columns
    :return: graph
    """
    x_labels = ['Pre-sleep', 'Trial1', 'Post-Trial1', 'Trial2', 'Post-Trial2', 'Trial3', 'Post-Trial3', 'Trial4',
                'Post-Trial4', 'Trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
    plt.figure(figsize=(18, 10))
    for key in rgs_data.keys():
        plt.errorbar(get_custom_data(x_labels, cols), get_custom_data(rgs_data[key], cols),
                     get_custom_data(rgs_sems[key], cols), ecolor='black', elinewidth=0.5, capsize=5,
                     label='RGS14 ' + key)
        plt.errorbar(get_custom_data(x_labels, cols), get_custom_data(vehic_data[key], cols),
                     get_custom_data(vehic_sems[key], cols), ecolor='black', elinewidth=0.5, capsize=5,
                     label='Vehicle ' + key, fmt='--')
    plt.ylabel('Strength')
    plt.xlabel('Time Bin')
    plt.ylim(0, 0.25)
    plt.legend()
    plt.title('all rats, all conditions, ' + text)
    plt.savefig('Graph\\Graph_all_rats_all_con_' + text)
    plt.show()
    pass

def get_custom_data(indata, cols):
    """returns the data from specific columns
    :param indata: any array of data
    :param cols: array of columns of data to return
    :return: columns of data
    """
    outdata = []
    for i in cols:
        outdata.append(indata[i])
    return outdata


def average_per_bin(rgs_data, vehic_data):
    print(rgs_data)
    print(vehic_data)
    cols = [[0], [1, 3, 5, 7, 9], [2, 4, 6, 8], [10, 11, 12, 13]]
    xlabels = ['pre-sleep', 'trial 1-4', 'post-trial 1-4', 'post-trial5']
    rgs_dataset = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    vehic_dataset = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    rgs_sems = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    vehic_sems = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for key in rgs_data.keys():
        for i in cols:
            rgs_dataset[key].append(average_bin_of(rgs_data[key], i))
            rgs_sems[key].append(get_sem(get_custom_data(rgs_data[key], i)))
            vehic_dataset[key].append(average_bin_of(vehic_data[key], i))
            vehic_sems[key].append(get_sem(get_custom_data(vehic_data[key], i)))
    print(vehic_sems)
    print(rgs_sems)
    plt.figure(figsize=(15, 6))
    for key in rgs_dataset.keys():
        plt.errorbar(xlabels, rgs_dataset[key], rgs_sems[key], label='RGS ' + key, ecolor='black', elinewidth=0.5,
                     capsize=5)
    for key in vehic_dataset.keys():
        plt.errorbar(xlabels, vehic_dataset[key], vehic_sems[key], label='Vehic ' + key, fmt='--', ecolor='black',
                     elinewidth=0.5, capsize=5)
    plt.ylabel('Strength')
    plt.xlabel('Time Bin')
    plt.title('Avg per ens per time bin for all rats')
    plt.ylim(0, 0.2)
    plt.legend()
    plt.savefig('Graph\\avgs_per_bin_per_ens_all_rats')
    plt.show()


def average_bin_of(data, cols):
    avg = 0
    for i in cols:
        avg += data[i]
    return avg / len(cols)


def per_con_graph(data, sems, rat_type):
    """plots the data in a graph
    :param data: dict of the data
    :param rat_type: which rats are plotted
    :return: null
    """
    x_labels = ['Pre-sleep', 'Trial1', 'Post-Trial1', 'Trial2', 'Post-Trial2', 'Trial3', 'Post-Trial3', 'Trial4',
                'Post-Trial4', 'Trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
    for key in data.keys():
        plt.figure(figsize=(15, 6))
        # plt.plot(x_labels, data[key])
        plt.plot(x_labels, data[key], data[key], 'ko')
        plt.errorbar(x_labels, data[key], sems[key], ecolor='black', elinewidth=1, capsize=5)
        plt.ylabel('Strength')
        plt.xlabel('Time Bin')
        plt.title('{}, Condition: {}'.format(rat_type, key))
        plt.savefig(fname='Graph\\graph_{}_Condition_{}.png'.format(rat_type, key))
        plt.show()
    # single_fig(data, rat_type)


def all_con_single_graph(data, sems, rat_type):
    """plots data of a single data set
    :param data: dict of dataset
    :param sems: dict of SEm info
    :param rat_type: info on wihc data is plotted
    :return: null
    """
    x_labels = ['Pre-sleep', 'Trial1', 'Post-Trial1', 'Trial2', 'Post-Trial2', 'Trial3', 'Post-Trial3', 'Trial4',
                'Post-Trial4', 'Trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4']
    plt.figure(figsize=(20, 10))
    plt.ylabel('Strength')
    plt.xlabel('Time Bin')
    plt.title('{}, all conditions'.format(rat_type))
    print(sems)
    for i, key in enumerate(data.keys()):
        plt.ylim(0, 0.25)
        plt.errorbar(x_labels, data[key], sems[key], ecolor='black', elinewidth=.5, capsize=5, label=key)
        # plt.plot(x_labels, data[key], label=key, color=colors[i])

        # plt.plot(data[key], 'ko')
    plt.legend()
    plt.savefig(fname='Graph\\graph_{}_all_conditions'.format(rat_type))
    plt.show()


main()
