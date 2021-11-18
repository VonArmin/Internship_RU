import matplotlib.pyplot as plt


def main():
    file1 = open('RGS14_combined.csv', 'r')
    file2 = open('vehicle_combined.csv', 'r')
    file1.readline()
    file2.readline()
    plot_data(file1, 'RGS')
    plot_data(file2, 'veh')


def plot_data(file1, name):
    plt.figure(figsize=(15, 10))
    for line in file1:
        line = line.strip('\n').split(',')
        for i in range(4, len(line)):
            line[i] = float(line[i])
        # if line[2] == 'OD':
        #     plt.plot(
        #         ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
        #          'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4'], line[4:],
        #         label=f'Rat{line[0]}-{line[1]}-{line[2]}', linestyle='dotted')
        if line[2] == 'OR':
            plt.plot(
                ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
                 'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4'], line[4:],
                label=f'Rat{line[0]}-{line[1]}-{line[2]}-{line[3]}', linestyle='dashed')
        # if line[2] == 'HC':
        #     plt.plot(
        #         ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
        #          'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4'], line[4:],
        #         label=f'Rat{line[0]}-{line[1]}-{line[2]}', linestyle='dashdot')
        # if line[2] == 'CON':
        #     plt.plot(
        #         ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
        #          'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4'], line[4:],
        #         label=f'Rat{line[0]}-{line[1]}-{line[2]}')
    plt.legend()
    plt.title(f'Plot for all conditions and SDs {name}')
    plt.ylabel('Rat')
    plt.xlabel('Time Bin')
    plt.show()


main()
