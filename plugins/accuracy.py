from base import Chooser
import os

class Accuracy(Chooser):

    def setup(self):
        self.fileList = None

    def teardown(self):
        for fo in self.fileList:
            fo.close()

    def choose(self,stack,predicted,predictor_name):
        if self.fileList == None:
            self.fileList = []
            #Initialize an output file for each predictor
            for name in predictor_name:
                fo = open('accuracy_'+name+'.txt','w')
                self.fileList.append(fo)
        else:
            #Get the accuracy of each predictor and write to file
            for i in range(0,len(predicted)):
                #Get the distance between predicted and ground truth
                dx = predicted[i,0,0] - stack.point[stack.current_frame,0,0]
                dy = predicted[i,0,1] - stack.point[stack.current_frame,0,1]
                d = (dx**2 + dy**2)**0.5
                #Write this to file
                self.fileList[i].write(str(d)+'\n')
            #Advance the frame (imagestack is 0-based, so if we hit total_frames
            #that means that we're out of images)
            stack.next()
            if stack.current_frame == stack.total_frames: stack.exit = True

