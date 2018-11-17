import numpy as np

# Prediction points naming convention:
# "Next" point mean a predicted point right next after the last of given points.
# "Future" point is the one after "Next", e.g. two steps later after the last of given points.

class Predictor:
    # Takes a 2D trajectory vector with Carthesian points
    # Returns a 2D array of predicted Carthesian points
    # note: points are expected to be normalized to 0..1 range
    def predict(self, input=np.zeros((2,2))):
        Predictor.validateInput(input)
        # Should return at least 1 point (could me more)
        return np.ones((2,2))

    @staticmethod
    def validateInput(input=np.zeros((1,2,2))):
        valid = len(input.shape) == 3 and input.size > 0 and len(input[0][0]) == 2
        if not valid: raise "Invalid input for Predictor! Expected 3D numpy array of shape (<n>, <m>, 2)"



class PrimitiveLinearPredictor(Predictor):
    def predict(self, input=np.zeros((1,2,2))):
        Predictor.validateInput(input)

        prevX, prevY = input[0][0][0], input[0][0][1]
        currX, currY = input[0][1][0], input[0][1][1]

        nextX = currX + (currX - prevX)
        nextY = currY + (currY - prevY)

        futureX = nextX + (nextX - currX)
        futureY = nextY + (nextY - currY)

        return np.array([[nextX, nextY], [futureX, futureY]])
