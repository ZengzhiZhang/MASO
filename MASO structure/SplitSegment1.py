# step 2: split trajectory to segments
import os
from copy import copy, deepcopy

import numpy as np
import pickle
from GlobalConfig import global_file_path

os.chdir('/..')
filename = global_file_path + 'step1'  # from the first step
AllSegment = []

AllModes = []
minPoints = 50
AllsegmentPointsNumber = []
AllExtendSegmentArray = []
AllExtendSegmentArrayResult = []

with open(filename, 'rb') as f:
    trajectoryLabelAllUser = pickle.load(f)
# variable from step 1

for t in range(len(trajectoryLabelAllUser)):
    AllExtendSegment = []
    Data = trajectoryLabelAllUser[t]
    if len(Data) == 0:
        continue
    delta_time = []
    # 遍历一个人的轨迹
    for i in range(len(Data) - 1):
        delta_time.append((Data[i + 1, 2] - Data[i, 2]) * 24. * 3600)
        if delta_time[i] == 0:
            delta_time[i] = 0.1
        # 左点的经纬度
        A = (Data[i, 0], Data[i, 1])
        # 右点的经纬度
        B = (Data[i + 1, 0], Data[i + 1, 1])
    delta_time.append(3)

    min_trip_time = 20 * 60  # zheng et al., 2008
    tripPointsNumber = []
    dataOneUserTrip = []
    dataOneUserSegment = []
    dataOneUserExtendSegment = []
    counter = 0
    index = []

    i = 0

    # 将一个人的轨迹分成多trip
    while i <= (len(Data) - 1):

        if delta_time[i] <= min_trip_time:
            counter += 1
            index.append(i)
            i += 1
        else:
            # 如果这一个点的距离上个点的持续时间大于20min，表明一趟结束。
            _the_delta_time = delta_time[i]
            counter += 1
            index.append(i)
            i += 1
            #
            tripPointsNumber.append(counter)
            dataTrip = [Data[k, 0:4] for k in index]
            dataTrip = np.array(dataTrip, dtype=float)
            dataOneUserTrip.append(dataTrip)
            counter = 0
            index = []
            continue
    # 如果没有找到一趟的结束点
    if len(index) != 0:
        tripPointsNumber.append(counter)
        dataTrip = [Data[k, 0:4] for k in index]
        dataTrip = np.array(dataTrip, dtype=float)
        dataOneUserTrip.append(dataTrip)
    else:
        print("last trip ")

    i = 0

    for i in range(len(dataOneUserTrip)):
        # dataOneUserTrip[i] 一趟的数据
        dataTrip = dataOneUserTrip[i]
        modeType = dataTrip[0][3]
        index = []
        # 每一趟的简单轨迹段
        simpleOneTripSegments = []
        # 每一趟的扩展轨迹段
        extendOneTripSegments = []
        j = 0
        while j <= len(dataTrip) - 1:
            # 将这一趟的数据通过模式分成只包含一种交通模式的轨迹段
            if dataTrip[j][3] == modeType:
                index.append(j)
                j += 1
            else:
                _mode = dataTrip[j][3]
                dataSegment = [dataTrip[k, 0:4] for k in index]
                simpleOneTripSegments.append(deepcopy(dataSegment))
                dataOneUserSegment.append(dataSegment)
                index = []
                modeType = dataTrip[j][3]
                index.append(j)
                j += 1
                continue
        # 这一趟交通模式没有发生改变
        if len(index) != 0:
            dataSegment = [dataTrip[k, 0:4] for k in index]
            simpleOneTripSegments.append(deepcopy(dataSegment))
            dataOneUserSegment.append(dataSegment)

        if len(dataOneUserSegment) == len(AllExtendSegmentArray) + len(simpleOneTripSegments):
            print("12312313")
            if len(AllExtendSegmentArray) > 349:
                print("123123")
        simpleOneTripSegmentsSize = len(simpleOneTripSegments)
        simpleOneTripSegmentsTemp = deepcopy(simpleOneTripSegments)
        if simpleOneTripSegmentsSize == 2:
            lSeg = simpleOneTripSegments[0]
            rSeg = simpleOneTripSegments[1]
            lSegTemp = lSeg[len(lSeg) // 5 * 4:]
            rSegTemp = rSeg[:len(rSeg) // 5]
            lSeg.extend(rSegTemp)
            lSegTemp.extend(rSeg)
            AllExtendSegmentArray.append(lSeg)
            AllExtendSegmentArray.append(lSegTemp)
            # extendOneTripSegments.append(lSeg)
            # extendOneTripSegments.append(lSegTemp)
        elif simpleOneTripSegmentsSize > 2:
            for _i in range(simpleOneTripSegmentsSize):
                if _i == 0:
                    # 只拼接后面一段
                    lSeg = simpleOneTripSegments[0]
                    rSeg = simpleOneTripSegments[1]
                    rSegTemp = rSeg[:len(rSeg) // 5]
                    lSeg.extend(rSegTemp)
                    AllExtendSegmentArray.append(lSeg)
                    # extendOneTripSegments.append(lSeg)
                if _i == simpleOneTripSegmentsSize - 1:
                    lSeg = simpleOneTripSegments[_i]
                    rSeg = simpleOneTripSegments[_i - 1]
                    lSegTemp = lSeg[len(lSeg) // 5 * 4:]
                    lSegTemp.extend(rSeg)
                    AllExtendSegmentArray.append(lSegTemp)
                    # extendOneTripSegments.append(lSegTemp)
                if _i != simpleOneTripSegmentsSize - 1 and _i != 0:
                    lSeg = simpleOneTripSegmentsTemp[_i - 1]
                    mSeg = simpleOneTripSegmentsTemp[_i]
                    rSeg = simpleOneTripSegmentsTemp[_i + 1]
                    lSegTemp = lSeg[len(lSeg) // 5 * 4:]
                    rSegTemp = rSeg[:len(rSeg) // 5]
                    lSegTemp.extend(mSeg)
                    lSegTemp.extend(rSegTemp)
                    AllExtendSegmentArray.append(lSegTemp)
                    # extendOneTripSegments.append(lSegTemp)
        else:
            # extendOneTripSegments.append(simpleOneTripSegments)
            AllExtendSegmentArray.append(simpleOneTripSegments[0])
        # dataOneUserExtendSegment.append(extendOneTripSegments)
    segmentPointsNumber = []
    # AllExtendSegment.append(dataOneUserExtendSegment)

    for i in range(len(dataOneUserSegment)):
        if len(dataOneUserSegment[i]) >= minPoints:
            segmentPointsNumber.append(len(dataOneUserSegment[i]))
            AllsegmentPointsNumber.append(len(dataOneUserSegment[i]))
            AllSegment.append(dataOneUserSegment[i])
            AllExtendSegmentArrayResult.append(AllExtendSegmentArray[i])
            AllModes.append(int(dataOneUserSegment[i][0][3]))
    if len(segmentPointsNumber) == 0:
        continue
# Output
with open(global_file_path + 'step2', 'wb') as f:
    pickle.dump([AllSegment,AllExtendSegmentArrayResult, AllModes], f)


def getAssociatedSegment(trip, index):
    # index是只包含一种交通模式的片段的轨迹点下标，获取其左右轨迹点的策略：
    # 1、获取其前后各一种模式的长度n，获取1/5··· * n 的轨迹长度，拼接在一起
    # 2、获取其前一段的轨迹，计算后半部分减速的轨迹段。获取其后一段的轨迹，计算前半部分加速的轨迹段。将三段按照顺序拼接在一起

    # 策略1 固定长度取值
    for _i, _item in trip:
        _i = 1
