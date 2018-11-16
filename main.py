from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from spaceships import *
from helpermath import *


class GameEngine(QObject):
    def __init__(self):
        QObject.__init__(self)

    # обязательно даём название аргументу через arguments=['sum']
    # иначе нельзя будет его забрать в QML
    # Signals:
    moveShipTo = pyqtSignal(int, int, int, arguments=['newX', 'newY', 'newRotation'])
    showPredictedShipAt = pyqtSignal(int, int, arguments=['newX', 'newY'])
    showBlastAt = pyqtSignal(int, int, arguments=['newX', 'newY'])

    stopPlay = pyqtSignal()

    isRouteBeingEdited = False
    route = []
    routeIndex = 0

    areaWidth = 0
    areaHeight = 0

    ship = SimpleShip()

    @pyqtSlot(str)
    def log(self, message):
        print(message)

    # QT slot without args
    @pyqtSlot()
    def tick(self):
        # dummy: re-emit another signal.
        #self.moveShipTo.emit(100, 100, 45)
        if self.routeIndex >= len(self.route):
            self.stopPlay.emit()
            self.routeIndex = 0
            return

        self.ship.fly()

        newX = self.ship.position[0]  # self.route[self.routeIndex][0]
        newY = self.ship.position[1]  # self.route[self.routeIndex][1]
        angle = self.ship.course

        print("Sending move request to: ", newX, newY, angle)
        self.moveShipTo.emit(newX,
                             newY,
                             angle)
        self.routeIndex += 1

    @pyqtSlot()
    def routeEditingCompleted(self):
        self.isRouteBeingEdited = False
        print("Route editing completed.")
        print(self.route)
        self.ship.initFlight([0, 0, 100, 100],
                             [0, 0, 100, 100],
                             self.route)
        # TODO: impl!

    @pyqtSlot(int, int)
    def addRoutePoint(self, x, y):
        if not self.isRouteBeingEdited:
            self.isRouteBeingEdited = True
            self.route = []
        print("New route point:", x, y)
        self.route.append([x , y])
        # TODO: impl!

    @pyqtSlot(float, float)
    def areaSizeChanged(self, w, h):
        self.areaWidth = w
        self.areaHeight = h

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

    engine.quit.connect(app.quit)
    sys.exit(app.exec_())