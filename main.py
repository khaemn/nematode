from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlListProperty, QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtCore import QObject, QTimer, pyqtProperty, pyqtSignal, pyqtSlot

from spaceships import *
from helpermath import *
from predictors import *

#from lstm_bilinear_predictor import *

import numpy as np


class UiPoint(QObject):
    _x=0
    _y=0

    def __init__(self, x=0, y=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._x = x
        self._y = y

    @pyqtProperty('int')
    def x(self):
        return self._x

    @pyqtProperty('int')
    def y(self):
        return self._y


class GameEngine(QObject):
    def __init__(self):
        QObject.__init__(self)

    # обязательно даём название аргументу через arguments=['sum']
    # иначе нельзя будет его забрать в QML
    # Signals:
    initLaunchBay = pyqtSignal(int, int, int, float, arguments=['topLefX', 'topLeftY', 'bottomRightX', 'bottomRightY'])
    initLandingZone = pyqtSignal(int, int, int, float,
                                 arguments=['topLefX', 'topLeftY', 'bottomRightX', 'bottomRightY'])
    initShip = pyqtSignal(str, int, int, arguments=['imgWhenAlive', 'imgSize', 'hitRadius'])

    updateShip = pyqtSignal(int, int, int, float, arguments=['newX', 'newY', 'newRotation', 'newHealth'])
    stopPlay = pyqtSignal()

    # TODO: rework to Properties.
    showNextPointAt = pyqtSignal(int, int, arguments=['newX', 'newY'])
    showFuturePointAt = pyqtSignal(int, int, arguments=['newX', 'newY'])
    showBlastAt = pyqtSignal(int, int, int, arguments=['newX', 'newY', 'newRadius'])
    predictionPointsChanged = pyqtSignal()

    #_predictionPoints = [[0,0],[100,100],[200,200],[300,300],[400,400],[500,500]]
    #_predictionPoints = [0, 100, 200, 300, 400, 500, 600, 700]
    _predictionPoints = [UiPoint(0, 0), UiPoint(100, 100), UiPoint(200, 200)]

    isRouteBeingEdited = False
    route = []
    routeIndex = 0

    areaWidth = 800
    areaHeight = 800

    ship = SimpleShip()

    # TODO: move to Cannon
    #predictor = LstmLinearPredictor()
    predictor = PrimitiveLinearPredictor()
    prevPosition = [0.0, 0.0]
    currPosition = [0.0, 0.0]
    lastNext = currPosition
    lastFuture = currPosition
    cannonBlastRadius = 5

    @pyqtSlot(str)
    def log(self, message):
        print(message)

    # QT slot without args
    @pyqtSlot()
    def tick(self):
        if self.ship.isLanded or not self.ship.isAlive:
            self.stopPlay.emit()
            return

        # The ship performs its movement
        self.ship.fly()

        # Cannon's bullet hits the predicted target's position
        # TODO: cannon.observeHit()
        self.showBlastAt.emit(self.lastNext[0], self.lastNext[1], self.cannonBlastRadius)
        hitAccuracy = distance(self.lastNext, self.ship.position)
        if hitAccuracy < self.cannonBlastRadius:
            self.ship.takeDamage(10)  # TODO::!!!

        # Cannon observes real target's position and predicts the next and future ones
        # TODO: rework to Cannon predictor
        # TODO: cannon.decideFiring()
        self.currPosition = self.ship.position
        _input = np.array([[self.prevPosition, self.currPosition]])
        _input = _input / self.areaWidth  # normalization

        prediction = self.predictor.predict(_input) * self.areaWidth  # denormalization
        print("Predicted trajectory:", prediction)

        self._predictionPoints.clear()
        for npPoint in prediction:
            self._predictionPoints.append(UiPoint(npPoint[0], npPoint[1]))
        self.predictionPointsChanged.emit()

        if len(prediction) > 1:
            self.showFuturePointAt.emit(prediction[1][0], prediction[1][1])
            self.lastFuture = [prediction[1][0], prediction[1][1]]

        self.showNextPointAt.emit(prediction[0][0], prediction[0][1])

        self.lastNext = [prediction[0][0], prediction[0][1]]
        self.prevPosition = self.ship.position

        self.updateShipUi(self.ship)

    @pyqtSlot()
    def initFlight(self):
        # TODO: impl. Zone reading from the file (?)
        self.ship.initFlight([[0, 0], [100, 100]],
                             [[500, 500], [100, 100]],
                             self.route)

    @pyqtSlot()
    def routeEditingCompleted(self):
        self.isRouteBeingEdited = False
        print("Route editing completed.")
        print(self.route)

    @pyqtSlot(int, int)
    def addRoutePoint(self, x, y):
        if not self.isRouteBeingEdited:
            self.isRouteBeingEdited = True
            self.route = []
        print("New route point:", x, y)
        self.route.append([x, y])
        # TODO: impl!

    @pyqtSlot(float, float)
    def areaSizeChanged(self, w, h):
        self.areaWidth = w
        self.areaHeight = h

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
                             _ship.health / _ship.initialHealth)


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

    gameEngine.initLaunchBay.emit(0, 0, 100, 100)
    gameEngine.initLandingZone.emit(0, 0, 100, 100)
    gameEngine.initShip.emit("ship", 40, 10)

    engine.quit.connect(app.quit)
    sys.exit(app.exec_())
