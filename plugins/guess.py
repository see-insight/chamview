from grammar import Predictor
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
        imwidth = stack.img_current.size[0]
        imheight = stack.img_current.size[1]
        result = zeros([stack.point_kinds,3])
        for i in range(0,stack.point_kinds):
            #Choose a random coordinate in the image
            result[i,0] = random.randrange(0,imwidth)
            result[i,1] = random.randrange(0,imheight)
            result[i,2] = 0.0
        return result

