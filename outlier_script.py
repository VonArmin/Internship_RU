import matplotlib.pyplot as plt


def main():
    file = open('RGS14_combined.csv', 'r')
    file.readline()
    plot_data(file)


def plot_data(file):
    plt.figure(figsize=(20, 15))
    for line in file:
        line = line.strip('\n').split(',')
        for i in range(4, len(line)):
            line[i] = float(line[i])
        plt.plot(
            ['pre_sleep', 'trial1', 'post_trial1', 'trial2', 'post_trial2', 'trial3', 'post_trial3', 'trial4',
             'post_trial4', 'trial5', 'PT5_part1', 'PT5_part2', 'PT5_part3', 'PT5_part4'], line[4:],
            label=f'Rat{line[0]}-{line[1]}-{line[2]}')
    plt.legend()
    plt.title('Plot for all conditions, rats and SDs')
    plt.ylabel('Rat')
    plt.xlabel('Time Bin')
    plt.show()


main()
