from base import Chooser
import os

class Accuracy(Chooser):

    def setup(self):
        self.fileList = []

    def teardown(self):
        for fo in self.fileList:
            fo.close()

    def choose(self,stack,predicted,predictor_name):
        if stack.current_frame == 0:
            #Initialize an output file for each predictor, but don't get
            #accuracy because the predictors first need a ground truth point
            for name in predictor_name:
                fo = open('..'+os.path.sep+name+'_accuracy.txt','w')
                self.fileList.append(fo)
        else:
            #Get the accuracy of each predictor and write to file
            for i in range(0,len(predicted)):
                #Get the distance between predicted and ground truth
                dx = predicted[i,0,0] - stack.point[stack.current_frame,0,0]
                dy = predicted[i,0,1] - stack.point[stack.current_frame,0,1]
                d = (dx**2 + dy**2)**0.5 #square root of squares
                #Write this to file
                self.fileList[j].write(d)
            #Advance the frame (imagestack is 0-based, so if we hit total_frames
            #that means that we're out of images)
            stack.next()
            if stack.current_frame == stack.total_frames: stack.exit = True

