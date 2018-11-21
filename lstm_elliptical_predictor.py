'''
This script trains a predictor for a M next points on the
trajectory using previous N points as input. Trained on
elliptical generated routes
'''
import os.path
import numpy as np
from predictors import Predictor
import circularRouteGenerator as CRG
from circularRouteGenerator import Circle, nextNPointsOnCircle
from helpermath import *
from keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten, TimeDistributed, AveragePooling1D
from keras.models import load_model


np.set_printoptions(precision=2, suppress=True)

#random.seed(777)



lstmInputPoints = 3
lstmPredictedPoints = 1

class LstmEllipticalPredictor(Predictor):
    #TRAIN_ME = True
    TRAIN_ME = False
    model_filename = 'models/lstm_elliptical_predictor.h5'
    inputPoints=lstmInputPoints
    outputPoints=lstmPredictedPoints

    def __init__(self, inputs=lstmInputPoints, outputs=lstmPredictedPoints):
        super().__init__(inputs, outputs)
        # define model
        self.model = Sequential()
        # If there is a file, load model from the file
        if os.path.isfile(self.model_filename):
            self.model = load_model(self.model_filename)
        else:
            # https: // machinelearningmastery.com / stacked - long - short - term - memory - networks /
            _lstmLayerFactor = 5
            self.model.add(LSTM(self.inputPoints * _lstmLayerFactor, return_sequences = True, input_shape=(self.inputPoints, 2)))
            self.model.add(LSTM(self.inputPoints * _lstmLayerFactor))
            self.model.add(Dense(self.inputPoints * _lstmLayerFactor, activation='relu'))
            self.model.add(Dense(self.outputPoints * 2, activation='linear'))
            self.model.compile(loss='mse', optimizer='adam')
            # fit model
        if self.TRAIN_ME:
            _datasetSize = 90
            _iterations = 5
            X, Y = CRG.getTrainingData(_datasetSize, self.inputPoints, self.outputPoints, simulate_acceleration=False)
            for i in range (0, _iterations):
                batchSize = max(1, _iterations - int(i / 100) * 100)
                print("Iteration ", i, " of ", _iterations, " batch size: ", batchSize)
                self.test()
                self.model.fit(X, Y, epochs=10, verbose=2, shuffle=True, batch_size=batchSize)
                # save model to single file
                self.model.save(self.model_filename)
                self.model.save(self.model_filename + '_bak_' + str(int(i / 100)))


    def predict(self, input):
        Predictor.validateInput(input)
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
        return self.model.predict(input, verbose=0)


    def test(self):
        testInput = nextNPointsOnCircle(Circle(0.5, 0.5, 0.5),
                                        startingAngle=0,
                                        angleStep=0.2618,  # 15 degr
                                        count=lstmInputPoints + lstmPredictedPoints,
                                        accelerationRatio=1.0)
        print("Test input: ", testInput)
        testData = np.array(testInput)
        testX, testY = testData[:lstmInputPoints], testData[lstmInputPoints:]
        testX = testX.reshape((1, lstmInputPoints, 2))
        testY = testY.reshape((1, lstmPredictedPoints * 2))
        prediction = self.predict(testX)
        print("Prediction:\n", prediction)
        print("Expected:\n", testY)

# '''
pred = LstmEllipticalPredictor()
pred.test()
# '''



