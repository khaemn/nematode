import numpy as np
import os
import io

def getAllData(routeFile):
    data = np.genfromtxt(routeFile, delimiter=',')
    # print(data)
    return data


# Splits a give array of Carthesian points to subsents
# with n input points and m (consecutive) output (e.g. learning)
def splitToLearningData(inputPointsCount, outPointsCount, _input):
    inputLen = len(_input)
    subsetLen = inputPointsCount + outPointsCount
    totalSubsets = inputLen - subsetLen
    # print(inputLen, totalSubsets)
    X,Y = [],[]
    for i in range (0, totalSubsets):
        _in = _input[i : (i + inputPointsCount)]
        _out = _input[(i + inputPointsCount):(i + subsetLen)]
        # print("\nX:", _in,"\nY:", _out)
        X.append(_in)
        Y.append(_out)
    X = np.array(X)
    #X = np.reshape(totalSubsets, inputPointsCount, 2)
    Y = np.array(Y)
    # Output layer will contain outPointsCount * 2 dense neurons.
    Y = Y.reshape(len(Y), outPointsCount * 2)
    return X,Y


def getTrainingData(filename, inputPointsCount, outPointsCount, normalizeDivider=800):
    data = getAllData(filename)
    X,Y = splitToLearningData(inputPointsCount, outPointsCount, data)
    X = X / normalizeDivider
    Y = Y / normalizeDivider
    return X,Y


'''
data = getAllData("routes/route_20181117_222622.csv")
X,Y = splitToLearningData(5, 2, data)
print("\nX:", X,"\n\nY:", Y)
'''