# step 1: match trajectory and label


import numpy as np
import os
from datetime import datetime
import pickle
from GlobalConfig import global_file_path, global_data_path

os.chdir('/..')
pathFile = global_data_path

allFolder = os.listdir(pathFile)
allFolder.sort()
print(allFolder)
trajectoryAllUser = []
labelAllUser = []
trajectoryLabelAllUser = []

mode = ['walk', 'bike', 'bus', 'car', 'taxi', 'subway', 'train', 'railway']  # travel modes in Geolife
modeIndex = {'walk': 0, 'bike': 1, 'bus': 2, 'car': 3, 'taxi': 3, 'subway': 4, 'train': 4, 'railway': 4}  # select modes


def dateConvert(time_str):
    date_format = "%Y/%m/%d %H:%M:%S"
    current = datetime.strptime(time_str, date_format)
    date_format = "%Y/%m/%d"
    bench = datetime.strptime('1899/12/30', date_format)
    no_days = current - bench
    delta_time_days = no_days.days + current.hour / 24.0 + current.minute / (24. * 60.) + current.second / (24. * 3600.)
    return delta_time_days


for folder in allFolder:
    # 遍历文件夹，找到有两个文件的，说明这个轨迹是带标签的
    if len(os.listdir(pathFile + folder)) == 2:
        trajectoryOneUser = []
        # trajectories
        trajectoriesPath = pathFile + folder + '/Trajectory/'
        # 一个人的所有的轨迹文件 ['20080116073613.plt', '20080117092422.plt']
        allPlt = os.listdir(trajectoriesPath)
        allPlt.sort()
        # 遍历这个人的所有轨迹文件
        for plt in allPlt:
            print("     *", allPlt.index(plt))
            # 打开一个plt文件
            with open(trajectoriesPath + plt, 'r', newline='', encoding="utf-8") as f:
                # 过滤掉非gps数据
                gpsPoint = filter(lambda x: len(x.split(',')) == 7, f)
                gpsPointSplit = map(lambda x: x.rstrip('\r\n').split(','), gpsPoint)
                for row in gpsPointSplit:
                    trajectoryOneUser.append([float(row[0]), float(row[1]), float(row[4])])
        # [39.9889166666667, 116.305066666667, 39463.3498263889]
        trajectoryOneUser = np.array(trajectoryOneUser)
        trajectoryAllUser.append(trajectoryOneUser)

        # label
        labelPath = pathFile + folder + '/labels.txt'
        with open(labelPath, 'r', encoding='utf-8') as f:
            labelOneUser = []
            label = list(map(lambda x: x.rstrip('\r\n').split('\t'), f))
            labelSplit = filter(lambda x: len(x) == 3 and x[2] in mode, label)
            for row in labelSplit:
                labelOneUser.append([dateConvert(row[0]), dateConvert(row[1]), modeIndex[row[2]]])
        labelOneUser = np.array(labelOneUser)
        # [3.95884021e+04 3.95884139e+04 2.00000000e+00]
        labelAllUser.append(labelOneUser)

        # 到这里，获取到了一个人如001的所有的轨迹列表和对应的时间范围标签为trajectoryOneUser和labelOneUser
        # 获取一个人所有的轨迹点的时间
        Dates = np.split(trajectoryOneUser, 3, axis=-1)[2]
        sec = 1 / (24.0 * 3600.0)
        indexNeed = []
        modeFinal = []
        # 遍历标签列表
        for index, row in enumerate(labelOneUser):
            index1 = np.where(Dates >= (float(row[0]) - sec))
            index2 = np.where(Dates <= (float(row[1]) + sec))
            index3 = list(set(index1[0]).intersection(index2[0]))
            temp = list(set(index1[0]).intersection(index2[0]))
            index3.sort()
            [modeFinal.append(row[2]) for i in index3]
            [indexNeed.append(i) for i in index3]

        trajectoryOneUser = [trajectoryOneUser[i, :] for i in indexNeed]
        trajectoryOneUser = np.array(trajectoryOneUser)
        modeFinal = np.array(modeFinal)

        trajectoryLabelOneUser = (np.vstack((trajectoryOneUser.T, modeFinal))).T
        trajectoryLabelAllUser.append(trajectoryLabelOneUser)
    else:
        continue

# Output
with open(global_file_path + 'step1', 'wb') as f:
    pickle.dump(trajectoryLabelAllUser, f)
# print("len", len(trajectoryLabelAllUser))
# Output trajectoryLabelAllUser
