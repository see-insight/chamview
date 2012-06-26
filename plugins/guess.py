from base import Predictor
from numpy import *
import random

class Guess(Predictor):

    def setup(self,stack):
        #Choose a random coordinate in the image
        row = random.randrange(0,stack.img_current.size[0])
        column = random.randrange(0,stack.img_current.size[1])
        confidence = 0.0
        return array([row,column,confidence])

    def teardown(self):
        pass

    def predict(self,stack):
        #Choose a random coordinate in the image
        row = random.randrange(0,stack.img_current.size[0])
        column = random.randrange(0,stack.img_current.size[1])
        confidence = 0.0
        return array([row,column,confidence])

