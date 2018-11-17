'''
This script trains a predictor for a next point on the line
using previous two points as input.
'''
import os.path
import math
import random
import numpy as np
from predictors import Predictor

np.set_printoptions(precision=2, suppress=True)

random.seed(777)

# Generates linear 3-points sequence.
# Assume that x1 = 0, x2 = 1, x3 = 2 on a Carthesian plane.
# Three Y coordinates are returned for a line on this plane.
def get_random_3_points_on_a_line():
    firstX = 1 - random.random()*2
    firstY = 1 - random.random()*2
    secondX = 1 - random.random()*2
    secondY = 1 - random.random()*2
    thirdX = secondX + (secondX - firstX)
    thirdY = secondY + (secondY - firstY)
    return [[firstX, firstY], [secondX, secondY], [thirdX, thirdY]]

# Generates a pack of random lines (each of 3 points)
def get_random_lines(quantity=10):
    result = list()
    for i in range(0, quantity):
        result.append(get_random_3_points_on_a_line())
    return result

# Generates necessary training datasets
def get_training_data():
    seq = get_random_lines(5000)
    seq = np.array(seq)
    Xr, yr = seq[:, :2], seq[:, 2:]
    Xr = Xr.reshape((len(Xr), 2, 2))
    yr = yr.reshape((len(yr), 2))
    return Xr, yr

#print(X, "\n\n\n\n", y)
#quit()

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import load_model


class LstmLinearPredictor(Predictor):
    TRAIN_ME = False
    model_filename = 'models/lstm_bilinear_predictor.h5'
    def __init__(self):
        super().__init__()
        # define model
        self.model = Sequential()
        # If there is a file, load model from the file
        if os.path.isfile(self.model_filename) and not self.TRAIN_ME:
            self.model = load_model(self.model_filename)
            return
        self.model.add(LSTM(10, input_shape=(2, 2)))
        self.model.add(Dense(2, activation='linear'))
        # compile model
        self.model.compile(loss='mse', optimizer='adam')
        # fit model
        for i in range (0, 100):
            X, y = get_training_data()
            self.model.fit(X, y, epochs=100, verbose=2, shuffle=False, batch_size=1)
            # save model to single file
            self.model.save(self.model_filename)
            self.model.save(self.model_filename + 'bak')

    def predict(self, input):
        Predictor.validateInput(input)
        return self.model.predict(input, verbose=0)

    def runTest(self):
        testX = np.array([
            # Input points            | expected prediction
            # RightTop <> LeftBottom movement:
            [[0.5, 0.5], [0.6, 0.6]],  # 0.7, 0.7
            [[0.6, 0.6], [0.8, 0.8]],  # 1.0, 1.0
            [[0.7, 0.7], [0.6, 0.6]],  # 0.5, 0.5
            [[1.0, 1.0], [0.9, 0.8]],  # 0.8, 0.6
            # Right <> Left movement:
            [[0.5, 0.5], [1.0, 0.5]],  # 1.5, 0.5
            [[0.1, 0.1], [0.2, 0.1]],  # 0.3, 0.1
            [[1.0, 1.0], [0.5, 1.0]],  # 0.0, 1.0
            [[0.2, 1.0], [-.5, 1.0]],  # -1.2, 1.0
            # Stall points (no movement at all)
            [[-.1, -.5], [-.1, -.5]],  # -.1, -.5
            [[-.0, -.0], [-.0, -.0]],  # -.0, -.0
            [[1.0, 1.0], [1.0, 1.0]],  # 1.0, 1.0
            [[0.5, 1.0], [0.5, 1.0]],  # 0.5, 1.0
            # Top<>Bottom movement:
            [[0.5, 0.5], [0.5, -.5]],  # .5, -1.5
            [[0.1, 0.1], [0.1, 0.5]],  # 0.1, 0.9
            [[1.0, 1.0], [1.0, 0.0]],  # 1.0, -1.
            [[0.1, 1.0], [0.1, -1.]],  # 0.1, -2.
            #[-0.01, 0.01], [-0.01, -0.01], [0.0, 0.0], [0.01, 0.01], [0.01, -0.01],
            # Descending lines:
            #[0.6, 0.5], [0.9, 0.4], [0.7, 0.2], [0.8, 0.79],
            # Out-of-bound too steep lines:
            #[0.0, 1.0], [1.0, 0.0], [-1.0, 0.0],
            #[-0.5, 0.5], [-0.9, 0.9], [-1.0, 1.0],
        ])
        testX = testX.reshape(len(testX), 2, 2)
        print(testX.shape)

        # make predictions:
        predictions = self.predict(testX)

        # print results:
        normalizing_coef = 10
        print("Test predictions:\n      first       second    -->    prediction    (     expected    error%)")
        for i in range(0, len(predictions)):
            firstX = testX[i, 0, 0] * normalizing_coef
            firstY = testX[i, 0, 1] * normalizing_coef
            secondX = testX[i, 1, 0] * normalizing_coef
            secondY = testX[i, 1, 1] * normalizing_coef
            predictedX = predictions[i, 0] * normalizing_coef
            predictedY = predictions[i, 1] * normalizing_coef
            expectedX = secondX + (secondX - firstX)
            expectedY = secondY + (secondY - firstY)
            errorX = (expectedX - predictedX) * 100 / (predictedX + 0.000001)  # to prevent division by zero
            errorY = (expectedY - predictedY) * 100 / (predictedY + 0.000001)  # to prevent division by zero
            error = math.sqrt(errorX**2 + errorY**2)
            print(
                "%6.1F;%5.1F, %6.1F;%5.1F  --> %7.2F;%6.2F;  (%6.1F;%6.1F;   %6.2F)"
                % (firstX, firstY, secondX, secondY, predictedX, predictedY, expectedX, expectedY, error)
            )

#'''
pred = LstmLinearPredictor()
pred.runTest()
#'''



