import math
from math import sqrt, atan2, sin, cos
from collections import namedtuple

Point = namedtuple('Point', 'x, y')
Circle = namedtuple('Circle', 'x, y, r')

# def distance(p1, p2):
#     return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
#     return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
#
#
# def inclination(p1, p2):
#     h = p2[1] - p1[1]
#     w = p2[0] - p1[0]
#     angle = math.atan2(h, w)
#     return math.degrees(angle)
# Math helpers: distance, inclination, angleDelta
def distance(p1, p2):
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


def inclination(p1=Point(0, 0), p2=Point(1, 1)):
    return atan2(p2.y - p1.y, p2.x - p1.x) * (180 / math.pi)


def angleDelta(p1=Point(1, 0), p2=Point(0, 1), center=Point(0, 0)):
    firstAngle = inclination(center, p1)
    secondAngle = inclination(center, p2)
    return secondAngle - firstAngle


def arcAngle(dist, radius):
    return 2 * math.asin(dist / (radius * 2))

def circleFrom3Pts(p1=Point(0, 0), p2=Point(0, 0), p3=Point(0, 0)):
    _x12y12 = (p1.x ** 2 + p1.y ** 2)
    _x22y22 = (p2.x ** 2 + p2.y ** 2)
    _x32y32 = (p3.x ** 2 + p3.y ** 2)

    A = p1.x * (p2.y - p3.y) - p1.y * (p2.x - p3.x) + p2.x * p3.y - p3.x * p2.y
    B = _x12y12 * (p3.y - p2.y) + _x22y22 * (p1.y - p3.y) + _x32y32 * (p2.y - p1.y)
    C = _x12y12 * (p2.x - p3.x) + _x22y22 * (p3.x - p1.x) + _x32y32 * (p1.x - p2.x)
    D = _x12y12 * (p3.x * p2.y - p2.x * p3.y) + _x22y22 * (p1.x * p3.y - p3.x * p1.y) + _x32y32 * (
    p1.y * p2.x - p1.x * p2.y)

    A = max(0.000001, A) # to prevent zero division if the points are on a line

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


    # So I was finally able to figure it out: The solution is to uncheck
    # the "PyQt compatible" option under Python Debugger in the Project
    # Settings of PyCharm. This option seems to cause the mentioned issues when using pyqt and debug mode.