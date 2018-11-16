from helpermath import *

def inZone(point, zone):
    if len(point) < 2 or len(zone) < 2 or len(zone[0]) < 2:
        return False
    return (point[0] > zone[0,0] and point[0] < zone[1,0] and
            point[1] > zone[0,1] and point[1] < zone[1,1])

# Base class for space ships, defines interface
class BaseShip:
    def __init__(self):
        route = []
        self.speed = 0.0
        self.overload = 0.0
        self.course = 0.0
        self.position = [0.0, 0.0]
        self.launchBay = [[0.0, 0.0], [0.0, 0.0]]
        self.landingZone = [[0.0, 0.0], [0.0, 0.0]]
        self.timestep = 0
        self.health = 100
        self.isAlive = True
        self.isOnRoute = False
        self.isLanded = True

    def fly(self):
        return

    def initFlight(self, _launchBay, _landingZone, _route):
        self.launchBay = _launchBay
        self.landingZone = _landingZone
        self.route = _route
        self.timestep = 0
        return


class SimpleShip(BaseShip):
    def __init__(self):
        super().__init__()

    def fly(self):
        print("Ship time is", self.timestep)
        print("Remaining route", len(self.route) - self.timestep - 1)
        if self.timestep >= len(self.route):
            return
        currPosition = self.route[self.timestep]
        #self.isLanded = inZone(currPosition, self.landingZone)
        prevPosition = self.route[max(0, self.timestep - 1)]

        self.position = currPosition
        print("Ship position is", self.position, "(was ", prevPosition, ")")

        self.speed = distance(currPosition, prevPosition)
        print("Ship speed is", self.speed)

        self.course = inclination(prevPosition, currPosition)
        print("Ship course is", self.course)

        self.timestep += 1



