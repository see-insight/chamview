from base import Chooser
import os
from pylab import *

class Accuracy(Chooser):

    def setup(self):
        self.x = []
        self.y = []
        self.name = []

    def teardown(self):
        #Go through each predictor
        for i in range(0,len(self.name)):
            #Save data to file
            fo = open('accuracy_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j])+','+str(self.y[i][j])+'\n')
            fo.close()
            #Plot the error vs frame graph
            figure()
            xlabel('Frames')
            ylabel('Error (pixels)')
            title(self.name[i])
            plot(self.x[i],self.y[i])
        show()

    def choose(self,stack,predicted,predictor_name):
        print 'Frame '+str(stack.current_frame)+'/'+str(stack.total_frames)
        #Have we yet to create numpy arrays to hold test results?
        if len(self.name) != len(predictor_name):
            for name in predictor_name:
                self.name.append(name)
            for i in range(0,len(self.name)):
                self.x.append(arange(0,stack.total_frames,1))
                self.y.append(zeros(stack.total_frames))
            return
        #Get the accuracy of each predictor
        for i in range(0,len(self.name)):
            #Get distance between predicted and ground truth for pointkind 0
            dx = predicted[i,0,0] - stack.point[stack.current_frame,0,0]
            dy = predicted[i,0,1] - stack.point[stack.current_frame,0,1]
            dist = (dx**2 + dy**2)**0.5
            self.y[i][stack.current_frame] = dist
        #Advance the frame (imagestack is 0-based, so if we hit total_frames
        #that means that we're out of images)
        stack.next()
        if stack.current_frame == stack.total_frames: stack.exit = True

