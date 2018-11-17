from helpermath import *

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
    overload = 0.0
    course = 0.0
    speed = 0.0

    # previous speed and course are used to calculate overload and fuel consumption
    prevCourse = 0.0
    prevSpeed = speed

    prevPosition = [0.0, 0.0]
    position = [0.0, 0.0]
    timestep = 0
    health = initialHealth
    fuel = initialFuel
    isAlive = True
    isOnRoute = False
    isLanded = False
    isLaunching = False

    def fly(self):
        maxTime = len(self.route) - 1
        print("ShipModel time is", self.timestep)
        print("ShipModel remaining route", maxTime - self.timestep)

        nextPosition = [0, 0]
        if (self.fuel > 0) :
            self.prevPosition = self.route[max(0, self.timestep - 1)]
            self.position = self.route[min(self.timestep, maxTime)]
            nextPosition = self.route[min(self.timestep + 1, maxTime)]
        else:
            # Without fuel - move with constant speed and course until death.
            self.speed = self.speed * 0.9
            xOffset = self.speed * math.cos(math.radians(self.course))
            yOffset = self.speed * math.sin(math.radians(self.course))
            self.position = [self.prevPosition[0] + xOffset,
                             self.prevPosition[1] + yOffset]
            nextPosition = [self.prevPosition[0] + xOffset*2,
                            self.prevPosition[1] + yOffset*2]

        self.isLanded = inZone(self.position, self.landingZone) and self.fuel > 0
        self.isLaunching = inZone(self.position, self.launchBay) and self.fuel > 0
        self.isOnRoute = not self.isLanded and not self.isLaunching

        print("ShipModel position is", self.position, "(was ", self.prevPosition, ")", "(will be", nextPosition ,")")

        if self.fuel > 0: # No change to course/speed possible without fuel
            self.speed = distance(self.position, self.prevPosition)
            self.course = inclination(self.prevPosition, self.position)
            self.overload = math.sqrt((self.speed - self.prevSpeed) ** 2 + (self.course - self.prevCourse) ** 2)
            print("ShipModel overload is", self.overload)
            self.fuel = max(0, self.fuel - self.overload / 10)  # TODO: investigate if ok
            self.prevSpeed = self.speed
            self.prevCourse = self.course

        print("ShipModel speed is", self.speed)
        print("ShipModel course is", self.course)

        self.prevPosition = self.position
        self.timestep += 1

    def initFlight(self, _launchBay, _landingZone, _route):
        self.launchBay = _launchBay
        self.landingZone = _landingZone
        self.route = _route
        self.timestep = 0
        self.health = self.initialHealth
        self.fuel = self.initialFuel
        self.prevSpeed = self.speed = 0
        self.prevCourse = self.course = 0
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





