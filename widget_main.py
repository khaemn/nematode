import sys  # sys нужен для передачи argv в QApplication
import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import mainwindow  # Это наш конвертированный файл дизайна
#from lstm_bilinear_predictor import *

class MousePointer(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()  # calling base class constructor
        self.setupUi(self)  # Mandatory Qt call
        self.gw.mouseMoveEvent = self.mouseMoveEvent  # connecting mouse movement over GW to this class handler
        self.gw.setSceneRect(0, 0, self.gw.width(), self.gw.height())
        self.gw.setScene(QtWidgets.QGraphicsScene(self))
        #self.gw.setSceneRect(0, 0, self.gw.width(), self.gw.height())
        self.scene = self.gw.scene()
        #self.scene.setSceneRect(0, 0, self.gw.width(), self.gw.height())
        self.gw.setSceneRect(QtCore.QRectF(self.gw.viewport().rect()))

        self.prevX = 0
        self.prevY = 0

        self.mouseEventDivider = 0
        self.mouseEventThreshold = 2

        self.redPen = QtGui.QPen(QtGui.QColor("red"))
        self.bluePen = QtGui.QPen(QtGui.QColor("blue"), 2)

        #self.predictor = BilinearPredictor()


    def mouseMoveEvent(self, event):
        if self.mouseEventDivider < self.mouseEventThreshold:
            self.mouseEventDivider += 1
            return

        self.mouseEventDivider = 0
        x, y = event.x(), event.y()
        if self.prevX == 0 and self.prevY == 0:
            self.prevX, self.prevY = x, y
            return

        point = QtCore.QPointF(self.gw.mapToScene(x, y))
        prevPoint = QtCore.QPointF(self.gw.mapToScene(self.prevX, self.prevY))
        print("mouse moved: ", x, y, point, prevPoint)

        self.scene.addLine(prevPoint.x(), prevPoint.y(), point.x(), point.y(), self.bluePen)

        # used instead of bilinear predictor LSTM NN :))) Works 99% the same.
        predictedX = x + (x - self.prevX)
        predictedY = y + (y - self.prevY)

        #input = np.array([[self.prevX, self.prevY],[x,y]])
        #input = input.reshape(len(input), 2, 2)
        #predictedX, predictedY = self.predictor.predict(input)

        predictedNextPoint = self.gw.mapToScene(predictedX, predictedY)
        ellipseSize = 10
        self.scene.addEllipse(predictedNextPoint.x() - ellipseSize / 2,
                              predictedNextPoint.y() - ellipseSize / 2,
                              ellipseSize,
                              ellipseSize,
                              self.redPen)
        self.scene.addLine(point.x(), point.y(), predictedNextPoint.x(), predictedNextPoint.y(), self.redPen)

        self.prevX, self.prevY = x, y
        return





def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MousePointer()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()