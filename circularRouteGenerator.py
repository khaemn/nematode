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
def manyNplusMPointsOnTwoRandomComplementaryArcs(_n, _m, simulate_acceleration=False):
    _many = 1
    _accelerationRatio = 1.0 if not simulate_acceleration else (1 + ((random.random() +0.5) / 10))
    p1, p2 = randomSegment()
    length = distance(p1, p2)
    if __debugPrint: print("Segment: ", p1, p2, " length: ", distance(p1, p2))
    # after randomSegment(), two points are never coincident, so next call should never raise exception.
    points = []
    startingRadius = length
    for ratio in range(0, _many):
        radius = startingRadius * ((ratio+1) * 2)
        cir1, cir2 = twoComplementaryCirclesFrom2Points(p1, p2, radius)
        cir1center, cir2center = Point(cir1.x, cir1.y), Point(cir2.x, cir2.y)
        if __debugPrint: print("Complementary circles: ", cir1, cir2)
        pointsOnCir1 = [p1, p2]  # because they are random and on the circle anyway
        pointsOnCir2 = [p1, p2]  # because they are random and on the circle anyway
        pointsOnCir1 += (nextNPointsOnCircle(circle=cir1,
                                             startingAngle=inclination(cir1center, p2),
                                             angleStep=angleDelta(p1, p2, Point(cir1.x, cir1.y)),
                                             count=(_n - 2 + _m), # because 2 points p1 and p2 are alreay in the array
                                             accelerationRatio=_accelerationRatio)
                            )
        if __debugPrint: print(_n+_m, " points on circle 1: ", pointsOnCir1)
        # pointsOnCir2 += (nextNPointsOnCircle(circle=cir2,
        #                                         startingAngle=inclination(p2),
        #                                         angleStep = angleDelta(p1, p2, Point(cir2.x, cir2.y)),
        #                                         count=(_n - 2 + _m),
        #                                         # because 2 points p1 and p2 are alreay in the array
        #                                         accelerationRatio=_accelerationRatio)
        #                     )
        # if __debugPrint: print(_n+_m, " points on circle 2: ", pointsOnCir2)
        points.append(pointsOnCir1)
        # points.append(pointsOnCir2)
    if __debugPlotRawGeneration:
        for vector in points:
            if __debugPrint: print(vector)
            for pt in vector:
                plt.plot(pt.x, pt.y, 'bo')
        plt.title('Generated data')
        plt.show()
    return points

# _m here corresponds to LSTM input batch size, and _m - to prediction length.
# returns an array with many pairs of vectors each with of _m+_n points, that are situated on a circle.
def manyNplusMPointsOnCircles(_n, _m, simulate_acceleration=False):
    if _m+_n < 3: raise ValueError("No less than 3 pts could be generated!")
    _many = 1
    _accelerationRatio = 1.0 if not simulate_acceleration else (1 + ((random.random() +0.5) / 10))

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

def getTrainingData(datasetSize, inputCount, outputCount, simulate_acceleration=False, normalize=True):
    data = []
    _normalizationThreshold = 2.0
    for i in range (0, datasetSize):
        #data += manyNplusMPointsOnTwoRandomComplementaryArcs(inputCount, outputCount, simulate_acceleration)
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


a = getTrainingData(100, 5, 5)