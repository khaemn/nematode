'''
This script trains a predictor for a next point on the line
using previous two points as input.
'''
import os.path
import math
import random
import numpy as np
from predictors import Predictor
from datasetGenerator import *

np.set_printoptions(precision=2, suppress=True)

random.seed(777)


from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import load_model

bilinInputs = 3
bilinOuputs = 3

class LstmLinearPredictor(Predictor):
    TRAIN_ME = True
    TRAIN_ME = False
    model_filename = 'models/lstm_bilinear_predictor.h5'

    def __init__(self, inputs=bilinInputs, outputs=bilinOuputs):
        super().__init__(inputs, outputs)
        # define model
        self.model = Sequential()
        # If there is a file, load model from the file
        if os.path.isfile(self.model_filename) and not self.TRAIN_ME:
            self.model = load_model(self.model_filename)
            return
        self.model.add(LSTM(10, input_shape=(self.inputPoints, 2)))
        self.model.add(Dense(self.outputPoints * 2, activation='linear'))
        # compile model
        self.model.compile(loss='mse', optimizer='adam')
        # fit model
        _iterations = 100
        for i in range(0, _iterations):
            batchSize = max(1, _iterations - int(i / 10) * 10)
            print("Iteration ", i, " of ", _iterations, " batch size: ", batchSize)
            X, y = getLinearTrainingData(20000, self.inputPoints, self.outputPoints, simulate_acceleration=True)
            self.model.fit(X, y, epochs=10, verbose=2, shuffle=True, batch_size=batchSize)
            # save model to single file
            self.model.save(self.model_filename)
            self.model.save(self.model_filename + 'bak')
            self.test()

    def predict(self, input):
        Predictor.validateInput(input)
        input = self.adapt(input)
        return self.model.predict(input, verbose=0)

    def test(self):
        textX, textY = getLinearTrainingData(1, self.inputPoints, self.outputPoints)
        pred = self.predict(textX)
        print("Expected:\n", textY, "\nPredicted:\n", pred)

#'''
#pred = LstmLinearPredictor()
#pred.test()
#'''



