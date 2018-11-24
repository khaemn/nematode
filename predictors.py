import numpy as np
import random
from helpermath import *

# Prediction points naming convention:
# "Next" point mean a predicted point right next after the last of given points.
# "Future" point is the one after "Next", e.g. two steps later after the last of given points.

class Predictor:
    inputPoints=1
    outputPoints=1

    def __init__(self, inputPoints, outputPoints):
        self.inputPoints = inputPoints
        self.outputPoints = outputPoints


    # Takes a 2D trajectory vector with Carthesian points
    # Returns a 2D array of predicted Carthesian points
    # note: points are expected to be normalized to 0..1 range
    def predict(self, input=np.zeros((2,2))):
        Predictor.validateInput(input)
        # Should return at least 1 point (could me more)
        return np.ones((2,2))

    @staticmethod
    def validateInput(input=np.zeros((1,2,2)), minSize = 2):
        valid = len(input.shape) == 3 and input.size > minSize and len(input[0][0]) == 2
        if not valid: raise "Invalid input for Predictor! Expected 3D numpy array of shape (<n>, <m>, 2)"

    def adapt(self, input):
        totalPoints = len(input[0])
        if (totalPoints < self.inputPoints):
            adapted = np.zeros((1, self.inputPoints, 2))
            for i in range(0, totalPoints):
                adapted[0,i] = input[0,i]
            input = adapted
        if (totalPoints > self.inputPoints):
            adapted = input[0][totalPoints - self.inputPoints:]
            adapted = adapted.reshape(1, self.inputPoints, 2)
            input = adapted
        return input


class PrimitiveLinearPredictor(Predictor):
    noiseRatio = 0.02
    def predict(self, input=np.zeros((1,2,2))):
        Predictor.validateInput(input)

        prevX, prevY = input[0][-2][0], input[0][-2][1]
        currX, currY = input[0][-1][0], input[0][-1][1]

        nextX = currX + (currX - prevX) + self.noiseRatio * (0.5 - random.random())
        nextY = currY + (currY - prevY) + self.noiseRatio * (0.5 - random.random())

        futureX = nextX + (nextX - currX)
        futureY = nextY + (nextY - currY)

        postFutureX = futureX + (futureX - nextX)
        postFutureY = futureY + (futureY - nextY)

        #return np.array([[nextX, nextY], [futureX, futureY], [postFutureX, postFutureY]])
        return np.array([[nextX, nextY]])

import matplotlib.pyplot as plt
class PrimitiveCircularPredictor(Predictor):
    __debugPlot = False
    def predict(self, input=np.zeros((1,2,2))):
        Predictor.validateInput(input, 3)

        if(len(input[0]) < self.inputPoints):
            return np.array([[0, 0], [1, 1]])

        input = self.adapt(input)

        (p1, p2, p3) = (Point(input[0][0][0],
                              input[0][0][1]),
                        Point(input[0][1][0],
                              input[0][1][1]),
                        Point(input[0][2][0],
                              input[0][2][1])
                        )

        circle = circleFrom3Pts(p1, p2, p3)
        center = Point(circle.x, circle.y)
        print("Circle from 3 points:", circle)
        firstAngleDelta = angleDelta(p1, p2, center)
        secondAngleDelta = angleDelta(p2, p3, center)
        angleStep = inclination(center, p3) - inclination(center, p2)
        accelerationRate = secondAngleDelta / firstAngleDelta

        plt.plot([p1.x], [p1.y], 'ro')
        plt.plot([p2.x], [p2.y], 'go')
        plt.plot([p3.x], [p3.y], 'bo')

        prediction = nextNPointsOnCircle( circle,
                                          inclination(center, p3),
                                          angleStep,
                                          self.outputPoints,
                                          accelerationRate)
        predsAsNp = np.array(prediction)

        if self.__debugPlot: # debug plot should be closed before next step!
            xpred, ypred = predsAsNp[:,0], predsAsNp[:,1]
            plt.plot(xpred, ypred, 'yo')
            plt.title('Circular primitive prediction')
            plt.gca().invert_yaxis()
            plt.axes().set_aspect('equal', 'datalim')
            plt.show()
        return predsAsNp

