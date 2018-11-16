import math

def angle_between_points( p0, p1, p2 ):
    a = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
    b = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    c = (p2[0]-p0[0])**2 + (p2[1]-p0[1])**2
    return math.acos( (a+b-c) / math.sqrt(4*a*b) ) * 180 / math.pi

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def inclination(p1, p2):
    h = p2[1] - p1[1]
    w = p2[0] - p1[0]
    angle = 0
    if abs(w) > 0 :
        angle = math.atan(h / w) #* 180 / math.pi
    return 90 * angle