# http://www.ambrsoft.com/trigocalc/circle3d.htm
from math import sqrt, atan2, sin, cos
import math
import numpy as np
import random
import matplotlib.pyplot as plt
from helpermath import *

#random.seed(777)

# Distances of a random segment that allows processing
minEligibleDistance = 0.0001
maxEligibleDistance = 1.0
minEligibleRadiusRatio = 1.0
maxEligibleRadiusRatio = 10.0

__debugPrint = False
__debugPlotRawGeneration = False
__debugPlotDataset = False

# Linear generation

def randomSegment():
    p1 = Point(random.random(), random.random())
    p2 = Point(random.random(), random.random())

    while (distance(p1, p2) < minEligibleDistance
           or distance(p1, p2) > maxEligibleDistance):
        p2 = Point(random.random(), random.random())
    return p1, p2

def random3pointsNotOnALine():
    p1, p2 = randomSegment()
    p3 = Point(random.random(), random.random())
    # ensure all three points are in "normal" distances
    while (distance(p3, p2) < minEligibleDistance
           or distance(p3, p2) > maxEligibleDistance):
        p3 = Point(random.random(), random.random())
    # Ensure they are not on 1 line:
    if distance(p1,p2) + distance(p2,p3) == distance(p1,p3):
        p3 = Point(random.random(), random.random())
        while (distance(p3, p2) < minEligibleDistance
               or distance(p3, p2) > maxEligibleDistance):
            p3 = Point(random.random(), random.random())
    return p1, p2, p3

# Generates linear 3-points sequence.
# Assume that x1 = 0, x2 = 1, x3 = 2 on a Carthesian plane.
# Three Y coordinates are returned for a line on this plane.
def randomNpointsOnALine(n = 3, simulate_acceleration=True):
    k = random.random()
    b = random.random()
    acceleration = 1.0 if not simulate_acceleration else (1 + ((random.random() + 0.5) / 5))

    # using y = kx + b equation with acceleration of each next X
    p1, p2 = randomSegment()
    xDistance = p2.x - p1.x
    yDistance = p2.y - p1.y
    prevPoint = p2

    output = [p1, p2]
    for i in range (2, n):
        if __debugPrint:
            print("Accel: ",acceleration)
            print("xDistance, y: ", xDistance, yDistance)
        xDistance = xDistance * acceleration
        yDistance = yDistance * acceleration
        newPoint = Point(prevPoint.x + xDistance,
                         prevPoint.y + yDistance)
        output.append(newPoint)
        prevPoint = newPoint
    return output


def getLinearTrainingData(datasetSize, inputCount, outputCount, simulate_acceleration=False, normalize=True):
    data = []
    for i in range(0, datasetSize):
        data.append(randomNpointsOnALine(inputCount + outputCount, simulate_acceleration))

    data = np.array(data)
    if normalize:
        threshold = 1.0
        absMax = abs(max(data.min(), data.max(), key=abs))
        if __debugPrint:
            print("Absoulte, min, max:", absMax, data.min(), data.max(),)
            print("Dataset before normalizing:\n", data)
        if absMax > threshold:
            data = data / absMax
        if __debugPrint:
            print("Dataset after normalizing:\n", data)
    if __debugPlotRawGeneration:
        for vector in data:
            startingPointsCount = 2
            plt.plot(vector[:startingPointsCount,0], vector[:startingPointsCount,1], 'ro--')
            plt.plot(vector[startingPointsCount-1:, 0], vector[startingPointsCount-1:, 1], 'o--')
        plt.title('Generated data')
        plt.show()
    Xr, yr = data[:, :inputCount], data[:, inputCount:]
    Xr = Xr.reshape((datasetSize, inputCount, 2))
    yr = yr.reshape((len(yr), outputCount*2))
    return Xr, yr

# Circular generation functions

def twoComplementaryCirclesFrom2Points(p1, p2, r=1.0):
    'Following explanation at http://mathforum.org/library/drmath/view/53027.html'
    if r == 0.0:
        raise ValueError('radius of zero')
    (x1, y1), (x2, y2) = p1, p2
    if p1 == p2:
        raise ValueError('coincident points gives infinite number of Circles')
    # delta x, delta y between points
    dx, dy = x2 - x1, y2 - y1
    # dist between points
    q = sqrt(dx ** 2 + dy ** 2)
    if q > 2.0 * r:
        raise ValueError('separation of points > diameter')
    # halfway point
    x3, y3 = (x1 + x2) / 2, (y1 + y2) / 2
    # distance along the mirror line
    d = sqrt(r ** 2 - (q / 2) ** 2)
    # One answer
    c1 = Circle(x=x3 - d * dy / q,
             y=y3 + d * dx / q,
             r=abs(r))
    # The other answer
    c2 = Circle(x=x3 + d * dy / q,
             y=y3 - d * dx / q,
             r=abs(r))
    return c1, c2


# _m here corresponds to LSTM input batch size, and _m - to prediction length.
# returns an array with many pairs of vectors each with of _m+_n points, that are situated on a circle.
def manyNplusMPointsOnCircles(_n, _m, simulate_acceleration=False):
    if _m+_n < 3: raise ValueError("No less than 3 pts could be generated!")
    _many = 1
    _accelerationRatio = 1.0 if not simulate_acceleration else (1 + ((random.random() +0.5) / 5))

    points = []

    for i in range(0, _many):
        p1, p2, p3 = random3pointsNotOnALine()
        _angleStep = math.pi * random.random()
        cir = circleFrom3Pts(p1, p2, p3)
        cirCenter = Point(cir.x, cir.y)
        pointsOnCir = (nextNPointsOnCircle(circle=cir,
                                             startingAngle=inclination(cirCenter, p3),
                                             angleStep=_angleStep,
                                             count=(_n + _m), # because 2 points p1 and p2 are alreay in the array
                                             accelerationRatio=_accelerationRatio)
                            )
        points.append(pointsOnCir)
        # opposite direction
        pointsOnCir = (nextNPointsOnCircle(circle=cir,
                                            startingAngle=inclination(cirCenter, p1),
                                            angleStep=-_angleStep,
                                            count=(_n + _m),  # because 2 points p1 and p2 are alreay in the array
                                            accelerationRatio=_accelerationRatio)
                                        )
        points.append(pointsOnCir)
    if __debugPlotRawGeneration:
        for vector in points:
            if __debugPrint: print(vector)
            for pt in vector:
                plt.plot(pt.x, pt.y, 'bo')
        plt.title('Generated data')
        plt.show()
    return points

def getCircularTrainingData(datasetSize, inputCount, outputCount, simulate_acceleration=False, normalize=True):
    data = []
    _normalizationThreshold = 2.0
    for i in range (0, datasetSize):
        data += manyNplusMPointsOnCircles(inputCount, outputCount, simulate_acceleration)
    dataset = np.array(data)
    # Normalization
    if normalize:
        normalizedData = []
        for record in dataset:
            # Get the (abs) maximum x and y coord in this line:
            maxXinThisLine, maxYinThisLine = max(abs(record[:,0])), max(abs(record[:,1]))
            absMax = max(maxXinThisLine, maxYinThisLine)
            if __debugPrint: print("Abs Maxim coords are: ", maxXinThisLine, maxYinThisLine, " denominator is ", absMax)
            if absMax > _normalizationThreshold:
                newLine = np.zeros((len(record), 2))
                if __debugPrint: print("line\n", record)
                for i in range(0, len(record)): # shift all (!) points in the sequence closer to
                    newpX, newpY = (float(record[i,0]) / absMax), (float(record[i,1]) / absMax)
                    newLine[i] = [newpX, newpY]
                if __debugPrint: print("newline\n", newLine)
                normalizedData.append(newLine)
            else:
                normalizedData.append(record)
        dataset = np.array(normalizedData)
    if __debugPlotDataset:
        if __debugPrint: print("Dataset:\n")
        for line in dataset:
            if __debugPrint: print("Line:", line)
            plt.plot(line[3:inputCount, 0], line[3:inputCount, 1], 'go') # then there are generated, but still "input" points
            plt.plot(line[:3,0], line[:3,1], 'bo') # 2 are the starting points
            plt.plot(line[inputCount:, 0], line[inputCount:, 1], 'ro') # these are output points
        plt.gca().invert_yaxis()
        plt.axes().set_aspect('equal', 'datalim')
        plt.title('Generated data')
        plt.show()
    Xr, Yr = dataset[:, :inputCount], dataset[:, inputCount:]
    Xr = Xr.reshape((len(Xr), inputCount, 2))
    Yr = Yr.reshape((len(Yr), outputCount*2))
    return Xr, Yr


# Generates necessary training datasets

#a = getCircularTrainingData(100, 5, 5)
b = getLinearTrainingData(1, 3, 3, simulate_acceleration=True)