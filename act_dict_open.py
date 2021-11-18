import pickle as pkl
import matplotlib.pyplot as plt
import scipy.io as sci

file = open('assembly_act_dict.pkl', 'rb')
file = pkl.load(file)


# print(file['Post-Trial2'][0])
# print(file)




# for i, j in file.items():
#
#     for jj in j:
#         print(i, len(jj))
#         plt.plot(jj,label=i)
# plt.figure()
# # [trial-period][assembly]
# plt.plot(file['Post_Trial2'][0])
# plt.legend()
# plt.show()

matfile = sci.loadmat('ripple_timestamps_Rat_OS_Ephys_RGS14_Rat3_357152_SD1_OD_10-11_10_2019.mat')
print(len(matfile['ripple_timestamps'][0]))
for line in matfile['ripple_timestamps'][0]:
    try:
        print(f'{line}')
    except IndexError:
        pass
