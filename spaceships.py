from helpermath import *
import math

def inZone(point, zone):
    if len(point) < 2 or len(zone) < 4:
        return False
    zoneX, zoneY, zoneW, zoneH = zone[0],zone[1],zone[2],zone[3]
    pointX, pointY = point[0], point[1]
    xInsideZone = pointX > zoneX and pointX < zoneX+zoneW
    yInsideZone = pointY > zoneY and pointY < zoneY+zoneH
    return xInsideZone and yInsideZone

# Base class for space ships, defines interface
class BaseShip:
    # Ship-specific constant characteristics:
    armor = 1.0
    mapSpeed = 600.0
    maxOverload = 10.0
    initialHealth = 100.0
    initialFuel = 100.0
    hitRadius = 10.0

    # Game map parameters
    route = []
    launchBay = [[0.0, 0.0], [0.0, 0.0]]
    landingZone = [[0.0, 0.0], [0.0, 0.0]]

    # Current status
    acceleration = 0.0
    course = 0.0
    speed = 0.0

    # previous speed and course are used to calculate overload and fuel consumption
    prevCourse = 0.0
    prevSpeed = speed

    prevPosition = [0.0, 0.0]
    position = [0.0, 0.0]
    time = 0
    health = initialHealth
    fuel = initialFuel

    isAlive = True
    isOnRoute = False
    isStopped = False
    isLanded = False
    isLaunching = False

    def fly(self):
        maxTime = len(self.route) - 1
        print("ShipModel time is", self.time)
        print("ShipModel remaining route", maxTime - self.time)

        nextPosition = [0, 0]
        if (self.fuel > 0) :
            self.prevPosition = self.route[max(0, self.time - 1)]
            self.position = self.route[min(self.time, maxTime)]
            nextPosition = self.route[min(self.time + 1, maxTime)]
        else:
            # Without fuel - move with constant speed and course until death.
            self.speed = self.speed * 0.9
            xOffset = self.speed * math.cos(math.radians(self.course))
            yOffset = self.speed * math.sin(math.radians(self.course))
            self.position = [self.prevPosition[0] + xOffset,
                             self.prevPosition[1] + yOffset]
            nextPosition = [self.prevPosition[0] + xOffset*2,
                            self.prevPosition[1] + yOffset*2]

        self.isLaunching = inZone(self.position, self.launchBay) and self.fuel > 0
        self.isStopped = (nextPosition == self.prevPosition)
        self.isOnRoute = not inZone(self.position, self.landingZone)\
                         and not inZone(self.position, self.launchBay)
        self.isLanded = inZone(self.position, self.landingZone) and self.fuel > 0\
                        and (self.isStopped or self.speed < 0.1)

        print("ShipModel position is", self.position, "(was ", self.prevPosition, ")", "(will be", nextPosition ,")")

        if self.fuel > 0: # No change to course/speed possible without fuel
            self.speed = distance(Point(self.position[0], self.position[1]),
                                  Point(self.prevPosition[0], self.prevPosition[1]))
            self.course = inclination(Point(self.position[0], self.position[1]),
                                      Point(nextPosition[0], nextPosition[1]))
            self.acceleration = abs(self.speed - self.prevSpeed) + abs(self.course - self.prevCourse)
            print("ShipModel overload is", self.acceleration)
            self.fuel = max(0, self.fuel - self.acceleration / 10)  # TODO: investigate if ok
            self.prevSpeed = self.speed
            self.prevCourse = self.course

        print("ShipModel speed is", self.speed)
        print("ShipModel course is", self.course)

        self.prevPosition = self.position
        self.time += 1

    def initFlight(self, _launchBay, _landingZone, _route):
        self.launchBay = _launchBay
        self.landingZone = _landingZone
        self.route = _route
        self.time = 0
        self.health = self.initialHealth
        self.fuel = self.initialFuel
        self.prevSpeed = self.speed = 0
        self.prevCourse = self.course = 0
        self.isAlive = True
        self.isOnRoute = False
        self.isLanded = False
        self.isLaunching = True
        self.isStopped = False
        return

    def takeDamage(self, dmg):
        self.health = max(0, self.health - (dmg / self.armor))
        self.isAlive = self.health > 0


class SimpleShip(BaseShip):
    def __init__(self):
        super().__init__()


class DebugShip(BaseShip): # Increased fuel and health
    def __init__(self):
        super().__init__()
        self.initialFuel = 1000
        self.initialHealth = 1000



