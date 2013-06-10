from Grammar import Chooser
import os
from pylab import *
import matplotlib.pyplot as plt
import math

class Accuracy(Chooser):
    """Can be used to find the difference between each Predictor and ground-truth
    points. Outputs the difference (in pixels) to file and displays a graph. Only
    uses the first pointkind on file.
    Usage: ./chamview.py -c Accuracy -d <image directory> -p <ground truth file>
    """

    def setup(self):     
        
        self.x = [] #Frame number
        self.y = [] #Error from ground-truth
        self.name = [] #Name of predictor
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        
        #Variable used to match with chamview.py requirements
        self.editedPointKinds = False

    def teardown(self):
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Save data to file
            fo = open('accuracy_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(self.y[i][j])+'\n')
            fo.close()
            
            #Plot the accuracy for current predictor
            plt.plot(self.x[i],self.y[i])
        
        #Declare other features for graph
        title('Accuracy on Prediction')
        xlabel('Frame')
        ylabel('Accuracy')
        plt.legend(self.name)
        plt.show()
        
    def choose(self,stack,predicted,predictor_name):
        
        #print 'Current Frame:'+str(stack.current_frame).zfill(4)+'/'+str(stack.total_frames).zfill(4)
        
        #Have we yet to take in Predictor info?
        if self.filledLists == False:
            
            self.filledLists = True
            
            for name in predictor_name:
                self.name.append(name)
                          
            for i in range(0,len(self.name)):
                self.x.append(arange(0,stack.total_frames,1))
                self.y.append(ones(stack.total_frames))
               
        #Get the accuracy of each predictor
        for pred in range(0,len(self.name)):
            
            #Add the accuracy given for pointkind 0
            #Get distance between predicted and ground truth
            dx = predicted[pred,0,0] - stack.point[stack.current_frame,0,0]
            dy = predicted[pred,0,1] - stack.point[stack.current_frame,0,1]
            
            dist = (dx**2 + dy**2)**0.5
            self.y[pred][stack.current_frame] = dist
   
        #Advance the frame (imagestack is 0-based, so if we hit total_frames
        #that means that we're out of images)
        stack.next()
        self.numImagesTested += 1
        
        if self.numImagesTested == stack.total_frames: stack.exit = True