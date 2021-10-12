import os.path

rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}
pathsv = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
pathsr = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
abspath = "Rat_OS_EPhys_RGS14_Cell_Assembly"
filename = '/mean_filter_df.csv'


def main(abspath):
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    write_data(bin_rats(subfolders))


def bin_rats(folders):
    for i, folder in enumerate(folders):
        type = folder.split('/')[1].split('_')
        if int(type[0].split('t')[1]) in rats['vehicle']:
            pathsv[type[2]].append(folder)
        if int(type[0].split('t')[1]) in rats['rgs']:
            pathsr[type[2]].append(folder)
    return get_data([pathsv, pathsr])


def get_data(indata):
    data = [[
        "Rat,Condition,SD,Neuron,Pre-sleep,Trial1,Post-Trial1,Trial2,Post-Trial2,Trial3,Post-Trial3,Trial4,Post-Trial4,Trial5,PT5_part1,PT5_part2,PT5_part3,PT5_part4\n"],
        [
            "Rat,Condition,SD,Neuron,Pre-sleep,Trial1,Post-Trial1,Trial2,Post-Trial2,Trial3,Post-Trial3,Trial4,Post-Trial4,Trial5,PT5_part1,PT5_part2,PT5_part3,PT5_part4\n"]]
    for i, dataset in enumerate(indata):
        for path in dataset:
            for file in dataset[path]:
                try:
                    with open(file + filename, 'r') as infilev:
                        for line in infilev:
                            if not line.startswith(','):
                                head = file.split('_')
                                outline = '{},{},{},{}'.format(head[5].split('t')[1], head[6], head[7], line)
                                data[i].append(outline)
                except FileNotFoundError:
                    pass
    return data


def write_data(datasets):
    vehicfile, rgsfile = 'vehicle_combined.csv', 'RGS14_combined.csv'
    for i, dataset in enumerate(datasets):
        if i == 0:
            with open(vehicfile, 'w') as outfile:
                for line in datasets[0]:
                    outfile.write(line)
        if i == 1:
            with open(rgsfile, 'w') as outfile:
                for line in datasets[1]:
                    outfile.write(line)


main(abspath)

