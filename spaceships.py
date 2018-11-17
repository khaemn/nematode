from helpermath import *

def inZone(point, zone):
    if len(point) < 2 or len(zone) < 2 or len(zone[0]) < 2:
        return False
    xInsideZone = point[0] > zone[0][0] and point[0] < zone[1][0]
    yInsideZone = point[1] > zone[0][1] and point[1] < zone[1][1]
    return xInsideZone and yInsideZone

# Base class for space ships, defines interface
class BaseShip:
    # Ship-specific constant characteristics:
    armor = 1.0
    mapSpeed = 600.0
    maxOverload = 10.0
    initialHealth = 100.0
    hitRadius = 10.0

    # Game map parameters
    route = []
    launchBay = [[0.0, 0.0], [0.0, 0.0]]
    landingZone = [[0.0, 0.0], [0.0, 0.0]]

    # Current status
    overload = 0.0
    course = 0.0
    speed = 0.0
    position = [0.0, 0.0]
    timestep = 0
    health = initialHealth
    isAlive = True
    isOnRoute = False
    isLanded = False
    isLaunching = False

    def fly(self):
        return

    def initFlight(self, _launchBay, _landingZone, _route):
        self.launchBay = _launchBay
        self.landingZone = _landingZone
        self.route = _route
        self.timestep = 0
        self.health = self.initialHealth
        self.isAlive = True
        self.isOnRoute = False
        self.isLanded = False
        self.isLaunching = False
        return

    def takeDamage(self, dmg):
        self.health = max(0, self.health - (dmg / self.armor))
        self.isAlive = self.health > 0


class SimpleShip(BaseShip):
    def __init__(self):
        super().__init__()

    def fly(self):
        maxTime = len(self.route) - 1
        print("ShipModel time is", self.timestep)
        print("ShipModel remaining route", maxTime - self.timestep)

        prevPosition = self.route[max(0, self.timestep - 1)]
        currPosition = self.route[min(self.timestep, maxTime)]
        nextPosition = self.route[min(self.timestep + 1, maxTime)]

        self.isLanded = inZone(currPosition, self.landingZone) or nextPosition == prevPosition
        self.isLaunching = inZone(currPosition, self.launchBay)
        self.isOnRoute = not self.isLanded and not self.isLaunching

        self.position = currPosition
        print("ShipModel position is", self.position, "(was ", prevPosition, ")", "(will be", nextPosition ,")")

        self.speed = distance(currPosition, prevPosition)
        print("ShipModel speed is", self.speed)

        self.course = inclination(prevPosition, currPosition)
        print("ShipModel course is", self.course)

        self.timestep += 1



