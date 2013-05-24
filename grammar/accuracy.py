from Grammar import Chooser
import os
from pylab import *

class Accuracy(Chooser):
    """Can be used to find the difference between each Predictor and ground-truth
    points. Outputs the difference (in pixels) to file and displays a graph. Only
    uses the first pointkind on file.
    Usage: ./chamview.py -c Accuracy -d <image directory> -p <ground truth file>
    """

    def setup(self):
        
        #Debugging purposes
        print 'Running setup in Accuracy'
        
        self.x = [] #Frame number
        self.y = [] #Error from ground-truth
        self.name = [] #Name of predictor
        self.filledLists = False

    def teardown(self):
        
        #Debugging purposes
        print 'Running teardown in Accuracy'
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            #Save data to file
            fo = open('accuracy_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(self.y[i][j])+'\n')
            fo.close()
            #Plot the error vs frame graph
            figure()
            xlabel('Frames')
            ylabel('Error (pixels)')
            title(self.name[i])
            plot(self.x[i],self.y[i])
        show()

    def choose(self,stack,predicted,predictor_name):
        
        #Debugging purposes
        print 'Running choose in Accuracy'
        
        print 'Frame '+str(stack.current_frame).zfill(4)+'/'+str(stack.total_frames).zfill(4)
        #Have we yet to take in Predictor info?
        if self.filledLists == False:
            self.filledLists = True
            for name in predictor_name:
                self.name.append(name)
            for i in range(0,len(self.name)):
                self.x.append(arange(0,stack.total_frames,1))
                self.y.append(zeros(stack.total_frames))
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

