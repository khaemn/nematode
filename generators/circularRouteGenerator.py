# http://www.ambrsoft.com/trigocalc/circle3d.htm
from math import sqrt, atan2, sin, cos
import math
from collections import namedtuple
import numpy as np
import random
import matplotlib.pyplot as plt

#random.seed(777)

Point = namedtuple('Point', 'x, y')
Circle = namedtuple('Circle', 'x, y, r')

# Distances of a random segment that allows processing
minEligibleDistance = 0.01
maxEligibleDistance = 1.0
minEligibleRadiusRatio = 1.0
maxEligibleRadiusRatio = 10.0

__debugPrint = False
__debugPlotRawGeneration = False
__debugPlotDataset = False

# Math helpers: distance, inclination, angleDelta
def distance(p1, p2):
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


def inclination(p1=Point(0, 0), p2=Point(1, 1)):
    return atan2(p2.y - p1.y, p2.x - p1.x)


def angleDelta(p1=Point(1, 0), p2=Point(0, 1), center=Point(0, 0)):
    firstAngle = inclination(center, p1)
    secondAngle = inclination(center, p2)
    return secondAngle - firstAngle


def arcAngle(dist, radius):
    return 2 * math.asin(dist / (radius * 2))

# Linear generation

def randomSegment():
    p1 = Point(random.random(), random.random())
    p2 = Point(random.random(), random.random())

    while (distance(p1, p2) < minEligibleDistance
           or distance(p1, p2) > maxEligibleDistance):
        p2 = Point(random.random(), random.random())
    return p1, p2

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


def circleFrom3Pts(p1=Point(0, 0), p2=Point(0, 0), p3=Point(0, 0)):
    _x12y12 = (p1.x ** 2 + p1.y ** 2)
    _x22y22 = (p2.x ** 2 + p2.y ** 2)
    _x32y32 = (p3.x ** 2 + p3.y ** 2)

    A = p1.x * (p2.y - p3.y) - p1.y * (p2.x - p3.x) + p2.x * p3.y - p3.x * p2.y
    B = _x12y12 * (p3.y - p2.y) + _x22y22 * (p1.y - p3.y) + _x32y32 * (p2.y - p1.y)
    C = _x12y12 * (p2.x - p3.x) + _x22y22 * (p3.x - p1.x) + _x32y32 * (p1.x - p2.x)
    D = _x12y12 * (p3.x * p2.y - p2.x * p3.y) + _x22y22 * (p1.x * p3.y - p3.x * p1.y) + _x32y32 * (
    p1.y * p2.x - p1.x * p2.y)

    _x = (-1) * (B / (2 * A))
    _y = (-1) * (C / (2 * A))
    _r = sqrt(((B ** 2) + (C ** 2) - (4 * A * D)) / (4 * (A ** 2)))
    return Circle(_x, _y, _r)


def nextNPointsOnCircle(circle=Circle(0, 0, 1), startingAngle=0, angleStep=0, count=1, accelerationRatio=1.0):
    points = []
    delta = 0
    for i in range(0, count):
        delta += angleStep * (accelerationRatio ** i)
        next = Point(circle.x + circle.r * cos(startingAngle + delta),
                  circle.y + circle.r * sin(startingAngle + delta))
        points.append(next)

    return points

# _m here corresponds to LSTM input batch size, and _m - to prediction length.
# returns an array with many pairs of vectors each with of _m+_n points, that are situated on a circle.
def manyNplusMPointsOnTwoRandomComplementaryArcs(_n, _m, simulate_acceleration=False):
    _many = 5
    _accelerationRatio = 1.0 if not simulate_acceleration else (random.random() * 2)
    p1, p2 = randomSegment()
    length = distance(p1, p2)
    if __debugPrint: print("Segment: ", p1, p2, " length: ", distance(p1, p2))
    # after randomSegment(), two points are never coincident, so next call should never raise exception.
    points = []
    startingRadius = length
    for ratio in range(1, _many):
        radius = startingRadius * (ratio * 2)
        cir1, cir2 = twoComplementaryCirclesFrom2Points(p1, p2, radius)
        if __debugPrint: print("Complementary circles: ", cir1, cir2)
        pointsOnCir1 = [p1, p2]  # because they are random and on the circle anyway
        pointsOnCir2 = [p1, p2]  # because they are random and on the circle anyway
        pointsOnCir1 += (nextNPointsOnCircle(circle=cir1,
                                                startingAngle=inclination(p2),
                                                angleStep=angleDelta(p1, p2, Point(cir1.x, cir1.y)),
                                                count=(_n - 2 + _m), # because 2 points p1 and p2 are alreay in the array
                                                accelerationRatio=_accelerationRatio)
                            )
        if __debugPrint: print(_n+_m, " points on circle 1: ", pointsOnCir1)
        pointsOnCir2 += (nextNPointsOnCircle(circle=cir2,
                                                startingAngle=inclination(p2),
                                                angleStep = angleDelta(p1, p2, Point(cir2.x, cir2.y)),
                                                count=(_n - 2 + _m),
                                                # because 2 points p1 and p2 are alreay in the array
                                                accelerationRatio=_accelerationRatio)
                            )
        if __debugPrint: print(_n+_m, " points on circle 2: ", pointsOnCir2)
        points.append(pointsOnCir1)
        points.append(pointsOnCir2)
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
    _normalizationThreshold = 1.0
    for i in range (0, datasetSize):
        data += manyNplusMPointsOnTwoRandomComplementaryArcs(inputCount, outputCount, simulate_acceleration)
    dataset = np.array(data)
    # Normalization
    if normalize:
        normalizedData = []
        for record in dataset:
            # Get the (abs) maximum x and y coord in this line:
            maxXinThisLine, maxYinThisLine = max(abs(record[:,0])), max(abs(record[:,1]))
            if __debugPrint: print("Abs Maxim coords are: ", maxXinThisLine, maxYinThisLine)
            if maxXinThisLine > _normalizationThreshold or maxYinThisLine > _normalizationThreshold:
                newLine = np.zeros((len(record), 2))
                if __debugPrint: print("line\n", record)
                for i in range(0, len(record)): # shift all (!) points in the sequence closer to
                    newpX, newpY = record[i,0] / maxXinThisLine, record[i,1] / maxYinThisLine
                    newLine[i] = [newpX, newpY]
                if __debugPrint: print("newline\n", newLine)
                normalizedData.append(newLine)
        dataset = np.array(normalizedData)
            # normalizedPointsOnCir1 = [Point(pt.x - absMax, pt.y - absMax) for pt in pointsOnCir1]
            #
            # maxX, maxY = abs(max(pointsOnCir2).x), abs(max(pointsOnCir2).y)
            # absMax = max(maxX, maxY)
            # normalizedPointsOnCir2 = [Point(pt.x - absMax, pt.y - absMax) for pt in pointsOnCir2]
            # points.append(normalizedPointsOnCir1)
            # points.append(normalizedPointsOnCir2)
    if __debugPlotDataset:
        if __debugPrint: print("Dataset:\n")
        for line in dataset:
            if __debugPrint: print("Line:", line)
            plt.plot(line[2:,0], line[2:,1], '--')
        plt.title('Generated data')
        plt.show()
    Xr, Yr = dataset[:, :inputCount], dataset[:, inputCount:]
    Xr = Xr.reshape((len(Xr), inputCount, 2))
    Yr = Yr.reshape((len(Yr), outputCount*2))
    return Xr, Yr


#print (getTrainingData(2, 5, 3))