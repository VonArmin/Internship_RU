import pickle as pkl
import matplotlib.pyplot as plt
import scipy.io as sci

file = open('assembly_act_dict.pkl', 'rb')
file = pkl.load(file)

plt.figure()
# print(file['Post-Trial2'][0])
# print(file)

plt.plot(file['Post_Trial2'][2])

# for i, j in file.items():
#
#     for jj in j:
#         print(i, len(jj))
#         plt.plot(jj,label=i)
plt.legend()
plt.show()

matfile = sci.loadmat('ripple_timestamps_Rat_OS_Ephys_RGS14_Rat3_357152_SD1_OD_10-11_10_2019.mat')
print(matfile)
