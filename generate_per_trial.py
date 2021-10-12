import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import sem
"""this script generated a plot with the data from combine_data_per_condition but normalizes it first"""


vehic_file = 'vehicle_combined.csv'
rgs_file = 'RGS14_combined.csv'


def main():
    rgs_data = create_data(rgs_file)
    rgs_sems = get_sems(rgs_data)
    rgs_avg = average_data(rgs_data)
    rgs_norm = normalise_data_pp_dev(rgs_data)
    rgs_norm_m = normalise_data_pp_min(rgs_data)

    vehic_data = create_data(vehic_file)
    vehic_sems = get_sems(vehic_data)
    vehic_avg = average_data(vehic_data)
    vehic_norm = normalise_data_pp_dev(vehic_data)
    vehic_norm_m = normalise_data_pp_min(vehic_data)
    # print(rgs_data)

    post_trials = ['Post-Trial1', 'Post-Trial2', 'Post-Trial3', 'Post-Trial4', 'PT5_part1', 'PT5_part2', 'PT5_part3',
                   'PT5_part4']
    trial = ['Trial1', 'Trial2', 'Trial3', 'Trial4', 'Trial5']

    plot_data(data_for_plot(rgs_norm_m, post_trials), data_for_plot(rgs_sems, post_trials),
              data_for_plot(vehic_norm_m, post_trials),
              data_for_plot(vehic_sems, post_trials), 'Post-Trials', 'Minus')
    plot_data(data_for_plot(rgs_norm_m, trial), data_for_plot(rgs_sems, trial),
              data_for_plot(vehic_norm_m, trial),
              data_for_plot(vehic_sems, trial), 'Trials', 'Minus')


def create_data(path):
    dataset = {'Pre-sleep': [], 'Trial1': [], 'Post-Trial1': [], 'Trial2': [], 'Post-Trial2': [], 'Trial3': [],
               'Post-Trial3': [], 'Trial4': [],
               'Post-Trial4': [], 'Trial5': [], 'PT5_part1': [], 'PT5_part2': [], 'PT5_part3': [], 'PT5_part4': []}
    with open(path, 'r') as file:
        file.readline()
        for line in file:
            list = line.split(',')
            list = list[4:]
            for i, key in enumerate(dataset):
                dataset[key].append(float(list[i]))
    return dataset


def data_for_plot(data, cols):
    dataset = {}
    for col in cols:
        dataset[col] = data[col]
    return dataset


def plot_data(data_rgs, sems_rgs, data_vehic, sems_vehic, text,text2):
    print(data_rgs)
    print(data_vehic)
    plt.figure(figsize=(15, 6))
    plt.errorbar(data_rgs.keys(), data_rgs.values(), sems_rgs.values(), ecolor='black', elinewidth=0.5, capsize=5,
                 label='RGS14')
    plt.errorbar(data_vehic.keys(), data_vehic.values(), sems_vehic.values(), ecolor='black', elinewidth=0.5, capsize=5,
                 label='Vehicle')

    plt.ylabel('Strength')
    plt.xlabel('Time Bin')
    plt.title('normalized by PS {} {}'.format(text,text2))
    plt.axhline(y=0, color='r')
    # plt.ylim()
    plt.savefig('normalized_by_ps_{}_{}'.format(text,text2))
    plt.legend()
    plt.show()


def average_data(data):
    dataset = {}
    for key, value in data.items():
        dataset[key] = avg(value)
    return dataset


def avg(list):
    val = 0
    for i in list:
        val += i
    return val / len(list)


def normalise_data_avgs(data):
    dataset = {}
    print(data)
    for key, value in data.items():
        dataset[key] = avg(value[1:]) / value[0]
    return dataset


def normalise_data_pp_dev(data):
    dataset = {}
    sleep_val = data['Pre-sleep']
    dataset['Pre-sleep'] = data['Pre-sleep']
    for key, value in data.items():

        if key != 'Pre-sleep':
            dataset[key] = []
            for i, val in enumerate(value):
                dataset[key].append(val / sleep_val[i])
        dataset[key] = avg(dataset[key])
    print(dataset)

    return dataset


def normalise_data_pp_min(data):
    dataset = {}
    sleep_val = data['Pre-sleep']
    dataset['Pre-sleep'] = data['Pre-sleep']
    for key, value in data.items():

        if key != 'Pre-sleep':
            dataset[key] = []
            for i, val in enumerate(value):
                dataset[key].append(val - sleep_val[i])
        dataset[key] = avg(dataset[key])
    print(dataset)

    return dataset


def get_sems(data):
    dataset = {}
    for key, value in data.items():
        dataset[key] = get_sem(value)
    return dataset


def get_sem(list):
    """calculate SEm(standard error of mean) of the list
    :param list: array of data
    :return: SEm
    """
    return sem(list)


main()
