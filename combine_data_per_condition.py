import os.path
import pickle
'this fetches all the data in cell_assembly folder and compiles it to a single file'
rats = {'vehicle': [1, 2, 6, 9], 'rgs': [3, 4, 7, 8]}

path = "Cell_assembly"
filename = '\mean_filter_df.csv'


def main(abspath):
    subfolders = [f.path for f in os.scandir(abspath) if f.is_dir()]
    write_data(get_data(bin_rats(subfolders)))


def bin_rats(folders):
    """finds the number of the rats and add it to a dict
    :param folders: array of all subfolders
    :return: dict of
    """
    pathsv = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    pathsr = {'OD': [], 'OR': [], 'HC': [], 'CON': []}
    for i, folder in enumerate(folders):
        type = folder.split('\\')[1].split('_')
        if int(type[0].split('t')[1]) in rats['vehicle']:
            pathsv[type[2]].append(folder)
        if int(type[0].split('t')[1]) in rats['rgs']:
            pathsr[type[2]].append(folder)
    return ([pathsv, pathsr])



def get_data(indata):
    """obtains data from mean_filter_df.csv file and puts it in a new csv file
    :param indata: dict of 2 dicts
    :return:
    """
    data = [[
        "Rat,SD,Condition,Assembly,Pre-sleep,Trial1,Post-Trial1,Trial2,Post-Trial2,Trial3,Post-Trial3,Trial4,Post-Trial4,Trial5,PT5_part1,PT5_part2,PT5_part3,PT5_part4\n"],
        [
            "Rat,SD,Condition,Assembly,Pre-sleep,Trial1,Post-Trial1,Trial2,Post-Trial2,Trial3,Post-Trial3,Trial4,Post-Trial4,Trial5,PT5_part1,PT5_part2,PT5_part3,PT5_part4\n"]]
    for i, dataset in enumerate(indata):
        for path in dataset:
            for file in dataset[path]:
                try:
                    with open(file + filename, 'r') as infilev:
                        for line in infilev:
                            if not line.startswith(','):
                                head = file.split('_')
                                outline = '{},{},{},{}'.format(head[1].split('t')[1], head[3], head[2], line)
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


main(path)
