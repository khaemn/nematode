'''
This script trains a predictor for a M next points on the
trajectory using previous N points as input. Trained on
elliptical generated routes
'''
import os.path
import numpy as np
from predictors import Predictor
import datasetGenerator as CRG
import random
from helpermath import *
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, Flatten, TimeDistributed, AveragePooling1D
from keras.models import load_model
from keras.optimizers import Adam


np.set_printoptions(precision=2, suppress=True)

random.seed(777)

_inputPoints = 3
_predictedPoints = 3

class DenseMixedPredictor(Predictor):
    TRAIN_ME = True
    TRAIN_ME = False
    model_filename = 'models/dense_mixed_predictor.h5'

    def __init__(self, inputs=_inputPoints, outputs=_predictedPoints):
        super().__init__(inputs, outputs)
        # define model
        # If there is a file, load model from the file
        if os.path.isfile(self.model_filename):
            self.model = load_model(self.model_filename)
        else:
            _layerFactor = 32
            self.model = Sequential()
            self.model.add(Dense(self.inputPoints * _layerFactor,
                                 input_shape=(self.inputPoints, 2),
                                 activation = 'linear'))
            self.model.add(Dense(self.inputPoints * _layerFactor,
                                 activation='relu'))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(self.outputPoints * _layerFactor, activation='relu'))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(self.outputPoints * 4, activation='relu'))
            self.model.add(Dropout(0.2))
            self.model.add(Dense(output_shape=(self.outputPoints, 2), activation='linear'))

            self.model.compile(loss='mse',
                               metrics=['accuracy'],
                               optimizer=Adam(clipnorm=1.))
            # fit model
        if self.TRAIN_ME:
            _datasetSize = 5000
            _iterations = 100
            #X, Y = CRG.getCircularTrainingData(_datasetSize, self.inputPoints, self.outputPoints, simulate_acceleration=True)
            X, Y = CRG.getLinearTrainingData(_datasetSize*2, self.inputPoints, self.outputPoints, simulate_acceleration=True)
            #Xl, Yl = CRG.getLinearTrainingData(_datasetSize*2, self.inputPoints, self.outputPoints, simulate_acceleration=True)
            #print("INTIAL LL:\n", Xl, "\n\n", Yl)
            #X = np.append(X, Xl, axis=0)
            #Y = np.append(Y, Yl, axis=0)

            for i in range (0, _iterations):
                batchSize = 1
                print("Iteration ", i, " of ", _iterations, " batch size: ", batchSize)
                self.model.fit(X,
                               Y,
                               epochs=10,
                               verbose=2,
                               shuffle=True,
                               batch_size=batchSize,
                               validation_split=0.05)
                # save model to single file
                self.model.save(self.model_filename)
                self.model.save(self.model_filename + '_bak_' + str(int(i / 100)))
                self.test()


    def predict(self, input):
        Predictor.validateInput(input)
        input = self.adapt(input)
        return self.model.predict(input, verbose=0)


    def test(self):
        testInput = nextNPointsOnCircle(Circle(0.5, 0.5, 0.5),
                                        startingAngle=0,
                                        angleStep=0.2618,  # 15 degr
                                        count=_inputPoints + _predictedPoints,
                                        accelerationRatio=1.0)
        #print("Test input: ", testInput)
        testData = np.array(testInput)
        testX, testY = testData[:_inputPoints], testData[_inputPoints:]
        testX = testX.reshape((1, _inputPoints, 2))
        testY = testY.reshape((1, _predictedPoints * 2))
        pred = self.predict(testX)
        err = (testY - pred)
        maxErr = abs(max(err.min(), err.max(), key=abs))
        print("Expected circular:\n", testY, "\nPredicted circular:\n", pred, "\nError:\n", (testY - pred), " max Err ", maxErr, "\n\n")

        textX, testY = CRG.getLinearTrainingData(1, self.inputPoints, self.outputPoints)
        pred = self.predict(textX)
        err = (testY - pred)
        maxErr = abs(max(err.min(), err.max(), key=abs))
        print("Expected linear:\n", testY, "\nPredicted linear:\n", pred,"\nError:\n", (testY - pred), " max Err ", maxErr, "\n\n")

if __name__ == '__main__':
    pred = DenseMixedPredictor()
    pred.test()



