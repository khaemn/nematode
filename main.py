from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlListProperty, QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtCore import QObject, QTimer, pyqtProperty, pyqtSignal, pyqtSlot

from spaceships import *
from helpermath import *
from predictors import *
from enum import Enum
#from lstm_bilinear_predictor import *
#from lstm_mouse_predictor import *
from lstm_elliptical_predictor import *

import numpy as np
import json
import io
import os
from time import gmtime, strftime

class UiPoint(QObject):
    _x=0
    _y=0

    def __init__(self, x=0, y=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._x = x
        self._y = y

    def __str__(self):
        return "%.0f:%.0f" % (self._x, self._y)

    @pyqtProperty('int')
    def x(self):
        return self._x

    @pyqtProperty('int')
    def y(self):
        return self._y


class GameStep(Enum):
    Predicting = 0
    Flying = 1
    Shooting = 2


class GameEngine(QObject):
    launchBay = [0, 0, 100, 100]
    landingZone = [700, 700, 100, 100]
    settingsFile = "settings.json"
    inputPointsForPredictor=3
    outputPointsForPredictor=1

    def __init__(self):
        QObject.__init__(self)
        # Write JSON file
        if not os.path.isfile(self.settingsFile):
            with io.open(self.settingsFile, 'w', encoding='utf8') as outfile:
                str_ = json.dumps({'launchBay' : self.launchBay, 'landingZone': self.landingZone},
                                  indent=4, sort_keys=False,
                                  separators=(',', ': '), ensure_ascii=True)
                outfile.write(str_)
        else:
            with io.open(self.settingsFile, 'r', encoding='utf8') as settingsFile:
                settings = json.load(settingsFile)
                self.landingZone = settings['landingZone']
                self.launchBay = settings['launchBay']
                print('landingZone', self.landingZone, 'launchBay', self.launchBay)


    # обязательно даём название аргументу через arguments=['sum']
    # иначе нельзя будет его забрать в QML
    # Signals:
    initLaunchBay = pyqtSignal(int, int, int, int, arguments=['_x', '_y', '_width', '_height'])
    initLandingZone = pyqtSignal(int, int, int, int, arguments=['_x', '_y', '_width', '_height'])
    initShip = pyqtSignal(str, int, int, arguments=['imgWhenAlive', 'imgSize', 'hitRadius'])

    updateShip = pyqtSignal(int, int, int, float, float,
                arguments=['posX', 'posY', 'course', 'health', 'fuel'])
    stopPlay = pyqtSignal(bool, arguments=['win'])

    # TODO: rework to Properties.
    showBlastAt = pyqtSignal(int, int, int, arguments=['newX', 'newY', 'newRadius'])
    predictionPointsChanged = pyqtSignal()

    _predictionPoints = [UiPoint(0, 0)]

    isRouteBeingEdited = False
    route = []
    routeIndex = 0

    areaWidth = 800
    areaHeight = 800

    #ship = SimpleShip()
    ship = DebugShip()

    # TODO: move to Cannon
    # predictor = LstmLinearPredictor()
    # predictor = PrimitiveLinearPredictor()
    # predictor = LstmMousePredictor()
    predictor = LstmEllipticalPredictor()
    #predictor = PrimitiveCircularPredictor(inputPointsForPredictor, 3)
    lastPositions = []

    prevPosition = [0.0, 0.0]
    currPosition = [0.0, 0.0]
    lastNext = currPosition
    lastFuture = currPosition
    cannonBlastRadius = 5

    step = GameStep.Predicting

    statistics = []
    statisticHeader = "time,x,y,course,speed,acceleration,health,fuel,nextX,nextY,hit"
    statisticFormat = "%d,%d,%d,%d,%.1f,%.1f,%.1f,%.1f,%d,%d,%d"

    wasHit = False

    @pyqtSlot(str)
    def log(self, message):
        print(message)

    # QT slot without args
    @pyqtSlot()
    def tick(self):
        if len(self.route) < 2 :
            self.stopPlay.emit(True)


        if self.ship.isLanded and self.ship.isAlive:
            self.stopPlay.emit(True)
            self.saveStats()
            print("Ship landed successfully! You win!")
            return

        if not self.ship.isAlive:
            self.stopPlay.emit(False)
            self.saveStats()
            print("Human killed. Robot wins.")
            return

        if self.ship.isStopped:
            self.stopPlay.emit(False)
            self.saveStats()
            print("Ship failed to achieve landing zone. Nobody cares it is alive, you lose anyway.")
            return


        if self.step == GameStep.Flying:
            # The ship performs its movement
            self.wasHit = False
            self.ship.fly()
            self.updateShipUi(self.ship) # to fly
            self.step = GameStep.Shooting
            return

        if self.step == GameStep.Shooting:
            self.step = GameStep.Predicting
            if not self.ship.isOnRoute:
                return
            # Cannon's bullet hits the predicted target's position
            # TODO: cannon.observeHit()
            self.showBlastAt.emit(self.lastNext[0], self.lastNext[1], self.cannonBlastRadius)
            hitAccuracy = distance(Point(self.lastNext[0], self.lastNext[1]),
                                   Point(self.ship.position[0], self.ship.position[1]))
            if hitAccuracy < (self.cannonBlastRadius + self.ship.hitRadius):
                self.wasHit = True
                self.ship.takeDamage(10)  # TODO::!!!
                self.updateShipUi(self.ship)  # to indicate damage
            return

        if self.step == GameStep.Predicting:
            # Cannon observes real target's position and predicts the next and future ones
            # TODO: rework to Cannon predictor
            # TODO: cannon.decideFiring()
            self.currPosition = self.ship.position

            self.lastPositions.append(self.ship.position)
            if(len(self.lastPositions) > 5) : #TODO: named constant!
                self.lastPositions.pop(0)

            _input = np.array(self.lastPositions)
            _input = _input / self.areaWidth  # normalization
            if(len(_input) < 2): # minimum 2 points needed to make a preditcion
                self.step = GameStep.Flying
                return
            _input = _input.reshape(1, len(_input), 2)
            prediction = self.predictor.predict(_input)
            prediction = prediction * self.areaWidth  # denormalization
            print("Predicted trajectory:\n", prediction)

            self._predictionPoints.clear()
            for npPoint in prediction:
                uiPoint = UiPoint(npPoint[0], npPoint[1])
                self._predictionPoints.append(uiPoint)
            print("Predicted UiPoints are about to be sent:\n", [str(pt) for pt in self._predictionPoints])
            self.predictionPointsChanged.emit()

            # "time,x,y,course,speed,acceleration,health,fuel,nextX,nextY,hit"
            self.statistics.append(
                self.statisticFormat % (self.ship.time,
                                        self.ship.position[0],
                                        self.ship.position[1],
                                        self.ship.course,
                                        self.ship.speed,
                                        self.ship.acceleration,
                                        self.ship.health,
                                        self.ship.fuel,
                                        prediction[0][0],
                                        prediction[0][1],
                                        self.wasHit
                                        )
            )

            self.lastNext = [prediction[0][0], prediction[0][1]]
            self.prevPosition = self.ship.position

            self.step = GameStep.Flying
            return

    @pyqtSlot()
    def initFlight(self):
        # TODO: impl. Zone reading from the file (?)
        self.ship.initFlight(self.launchBay,
                             self.landingZone,
                             self.route)

    @pyqtSlot()
    def routeEditingStarted(self):
        self.isRouteBeingEdited = True
        self.route = []

    @pyqtSlot()
    def routeEditingCompleted(self):
        self.isRouteBeingEdited = False
        print("Route editing completed.")
        if (len(self.route) < 2
            or not inZone(self.route[0], self.launchBay)
            or not inZone(self.route[-1], self.landingZone)):
            print("Invalid route: less than 2 points, or starts not from start, or ends not at the end.")
            self.route = []
        print(self.route)

    @pyqtSlot(int, int)
    def addRoutePoint(self, x, y):
        print("New route point:", x, y)
        self.route.append([x, y])

    @pyqtSlot()
    def saveRoute(self):
        filename = "route_" + strftime("%Y%m%d_%H%M%S", gmtime()) + ".csv"
        path = "routes/" + filename
        with io.open(path, 'w', encoding='utf8') as outfile:
            for point in self.route:
                outfile.write("%.0f,%.0f\n"%(point[0], point[1]))

    @pyqtProperty(QQmlListProperty, notify=predictionPointsChanged)
    def predictionPoints(self):
        return QQmlListProperty(UiPoint, self, self._predictionPoints)

    def updateShipUi(self, _ship=BaseShip()):
        newX = _ship.position[0]
        newY = _ship.position[1]
        angle = _ship.course

        print("Sending move request to: ", newX, newY, angle)
        self.updateShip.emit(newX,
                             newY,
                             angle,
                             _ship.health / _ship.initialHealth,
                             _ship.fuel / _ship.initialFuel)

    def saveStats(self):
        filename = "game_" + strftime("%Y%m%d_%H%M%S", gmtime()) + ".csv"
        path = "games/" + filename
        with io.open(path, 'w', encoding='utf8') as outfile:
            outfile.write(self.statisticHeader)
            outfile.write("\n")
            for record in self.statistics:
                outfile.write(record)
                outfile.write("\n")

if __name__ == "__main__":
    import sys

    # создаём экземпляр приложения
    app = QGuiApplication(sys.argv)
    # создаём QML движок
    engine = QQmlApplicationEngine()
    # создаём объект калькулятора
    gameEngine = GameEngine()
    # и регистрируем его в контексте QML
    engine.rootContext().setContextProperty("gameEngine", gameEngine)
    # загружаем файл qml в движок
    engine.load("catcher/main.qml")

    gameEngine.initLaunchBay.emit(gameEngine.launchBay[0],
                                  gameEngine.launchBay[1],
                                  gameEngine.launchBay[2],
                                  gameEngine.launchBay[3])
    gameEngine.initLandingZone.emit(gameEngine.landingZone[0],
                                    gameEngine.landingZone[1],
                                    gameEngine.landingZone[2],
                                    gameEngine.landingZone[3])
    gameEngine.initShip.emit("ship", 40, 10)

    engine.quit.connect(app.quit)
    sys.exit(app.exec_())
