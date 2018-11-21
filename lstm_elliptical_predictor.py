'''
This script trains a predictor for a M next points on the
trajectory using previous N points as input. Trained on
elliptical generated routes
'''
import os.path
import math
import random
import numpy as np
from predictors import Predictor
from generators import circularRouteGenerator as CRG

np.set_printoptions(precision=2, suppress=True)

random.seed(777)


from keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten, TimeDistributed, AveragePooling1D
from keras.models import load_model

lstmInputPoints = 5
lstmPredictedPoints = 3

class LstmEllipticalPredictor(Predictor):
    TRAIN_ME = True
    #TRAIN_ME = False
    model_filename = 'models/lstm_elliptical_predictor.h5'
    inputs=lstmInputPoints
    outputs=lstmPredictedPoints

    def __init__(self, inputs=lstmInputPoints, outputs=lstmPredictedPoints):
        super().__init__()
        # define model
        self.model = Sequential()
        self.inputs = inputs
        self.outputs = outputs
        # If there is a file, load model from the file
        if os.path.isfile(self.model_filename):
            self.model = load_model(self.model_filename)
        else:
            # https: // machinelearningmastery.com / stacked - long - short - term - memory - networks /
            self.model.add(LSTM(self.inputs * 2, return_sequences = True, input_shape=(self.inputs, 2)))
            self.model.add(LSTM(self.inputs * 2))
            self.model.add(Dense(self.outputs * 2, activation='linear'))
            self.model.add(Dense(self.outputs * 2, activation='linear'))
            self.model.compile(loss='mse', optimizer='adam')
            # fit model
        if self.TRAIN_ME:
            _datasetSize = 10000
            _iterations = 100
            for i in range (0, _iterations):
                X, Y = CRG.getTrainingData(_datasetSize, self.inputs, self.outputs, simulate_acceleration=True)
                self.model.fit(X, Y, epochs=10, verbose=2, shuffle=True, batch_size=_iterations-i)
                # save model to single file
                self.model.save(self.model_filename)
                self.model.save(self.model_filename + 'bak')


    def predict(self, input):
        Predictor.validateInput(input)
        points = len(input[0])
        if (points < self.inputs):
            adapted = np.zeros((1, self.inputs, 2))
            for i in range(0, points):
                adapted[0,i] = input[0,i]
            input = adapted
        if (points > self.inputs):
            adapted = input[0][points - self.inputs:]
            adapted = adapted.reshape(1,self.inputs,2)
            input = adapted
        return self.model.predict(input, verbose=0)

    def runTest(self):
        testX, testY = CRG.getTrainingData(1, self.inputs, self.outputs)

        # make predictions:
        predictions = self.predict(testX[3].reshape(1,lstmInputPoints,2))

        # print results:
        normalizing_coef = 800
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
#pred = LstmEllipticalPredictor()
#pred.runTest()
#'''



