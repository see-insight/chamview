from base import Chooser
from numpy import *

class Max(Chooser):

    def setup(self):
        pass

    def teardown(self):
        pass

    def choose(self,stack,predicted,predictor_name):
        #For every point kind
        for i in range(0,stack.point_kinds):
            max_confidence = -0.1
            row = 0;column = 0
            #For every predictor
            for j in range(0,len(predicted)):
                #If the predictor is more confident than the current max, then
                #set the current max to this predictor
                if predicted[j,i,2] > max_confidence:
                    max_confidence = predicted[j,i,2]
                    row = predicted[j,i,0]
                    column = predicted[j,i,1]
            #Store the most confident coordinate for this point kind
            stack.point[stack.current_frame,i,0] = row
            stack.point[stack.current_frame,i,1] = column
        #Advance the frame (imagestack is 0-based, so if we hit total_frames
        #that means that we're out of images)
        stack.next()
        if stack.current_frame == stack.total_frames: stack.exit = True

