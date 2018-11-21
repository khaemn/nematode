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
    TRAIN_ME = False
    model_filename = 'models/lstm_elliptical_predictor.h5'
    def __init__(self):
        super().__init__()
        # define model
        self.model = Sequential()
        # If there is a file, load model from the file
        if os.path.isfile(self.model_filename):
            self.model = load_model(self.model_filename)
        else:
            # Building the model (https://github.com/keras-team/keras/issues/6351)
            self.model.add(LSTM(20, input_shape=(lstmInputPoints, 2)))
            self.model.add(Dense(lstmPredictedPoints * 2, activation='linear'))
            # compile model
            self.model.compile(loss='mse', optimizer='adam')
            # fit model
        if self.TRAIN_ME:
            _datasetSize = 1000
            for i in range (0, 10):
                X, Y = CRG.getTrainingData(_datasetSize, lstmInputPoints, lstmPredictedPoints)
                self.model.fit(X, Y, epochs=10, verbose=2, shuffle=True, batch_size=int(_datasetSize / 100))
                # save model to single file
                self.model.save(self.model_filename)
                self.model.save(self.model_filename + 'bak')


    def predict(self, input):
        Predictor.validateInput(input)
        points = len(input[0])
        if (points < lstmInputPoints):
            adapted = np.zeros((1, lstmInputPoints, 2))
            for i in range(0, points):
                adapted[0,i] = input[0,i]
            input = adapted
        if (points > lstmInputPoints):
            adapted = input[0][points - lstmInputPoints:]
            adapted = adapted.reshape(1,lstmInputPoints,2)
            input = adapted
        return self.model.predict(input, verbose=0)

    def runTest(self):
        testX, testY = CRG.getTrainingData(1, lstmInputPoints, lstmPredictedPoints)

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
pred = LstmEllipticalPredictor()
#pred.runTest()
#'''



