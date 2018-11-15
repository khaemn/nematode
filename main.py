from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

import math


def angle_between_points( p0, p1, p2 ):
    a = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
    b = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    c = (p2[0]-p0[0])**2 + (p2[1]-p0[1])**2
    return math.acos( (a+b-c) / math.sqrt(4*a*b) ) * 180 / math.pi


def inclination(p1, p2):
    h = p2[1] - p1[1]
    w = p2[0] - p1[0]
    angle = 0
    if abs(w) > 0 :
        angle = math.atan(h / w) #* 180 / math.pi
    return 90 * angle



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
        newX = self.route[self.routeIndex][0]
        newY = self.route[self.routeIndex][1]

        angle = inclination(
            self.route[max([self.routeIndex - 1, 0])],
            self.route[self.routeIndex]
        )
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