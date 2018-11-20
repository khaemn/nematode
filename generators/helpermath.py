import math


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def inclination(p1, p2):
    h = p2[1] - p1[1]
    w = p2[0] - p1[0]
    angle = math.atan2(h, w)
    return math.degrees(angle)