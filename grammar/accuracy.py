from Grammar import Chooser
import os
from pylab import *
import matplotlib.pyplot as plt

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
        self.z = [] #Contains the accuracy(a number between 0 and 1)
        self.name = [] #Name of predictor
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        
        #Variable used to match with chamview.py requirements
        self.editedPointKinds = False

    def teardown(self):
        
        #Debugging purposes-------------------------------------------------------
        print 'Running teardown in Accuracy'
        
        '''plt.plot(x, x)
        plt.plot(x, 2 * x)
        plt.plot(x, 3 * x)
        plt.plot(x, 4 * x)
        plt.legend(['y = x', 'y = 2x', 'y = 3x', 'y = 4x'], loc='upper left')
        plt.show()'''
        
        #-------------------------------------------------------------------------
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Save data to file
            fo = open('accuracy_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(self.z[i][j])+'\n')
            fo.close()
            
            #Plot the error vs frame graph
            #figure()
            #xlabel('Frames')
            #ylabel('Error (pixels)')
            #title(self.name[i])
            plt.plot(self.x[i],self.z[i])
        plt.legend(self.name)
        plt.show()

    def choose(self,stack,predicted,predictor_name):
        
        #Debugging purposes--------------------------------------------------------
        print 'Running choose in Accuracy'
        #--------------------------------------------------------------------------
        
        print 'Frame '+str(stack.current_frame).zfill(4)+'/'+str(stack.total_frames).zfill(4)
        #Have we yet to take in Predictor info?
        if self.filledLists == False:
            
            self.filledLists = True
            
            for name in predictor_name:
                self.name.append(name)
                          
            for i in range(0,len(self.name)):
                self.x.append(arange(0,stack.total_frames,1))
                self.y.append(ones(stack.total_frames))
                self.z.append(zeros(stack.total_frames))
               
        #Get the accuracy of each predictor
        for pred in range(0,len(self.name)):
            
            #Add the accuracy given for each pointkind
            for pKind in range(0,stack.point_kinds):
                #Get distance between predicted and ground truth
                dx = predicted[pred,pKind,0] - stack.point[stack.current_frame,pKind,0]
                dy = predicted[pred,pKind,1] - stack.point[stack.current_frame,pKind,1]
            
                dist = (dx**2 + dy**2)**0.5
                self.y[pred][stack.current_frame] += dist
            
            #Compute the accuracy of predictor pred in current frame
            self.z[pred][stack.current_frame] = 1 / self.y[pred][stack.current_frame]
            
        #Advance the frame (imagestack is 0-based, so if we hit total_frames
        #that means that we're out of images)
        stack.next()
        self.numImagesTested += 1
        
        if self.numImagesTested == stack.total_frames: stack.exit = True
        
        #Print arrays for debugging purposes-------------------------
        print 'x: ', self.x
        print 'y: ', self.y    
        print 'z: ', self.z
        #---------------------------------------------------------------------

        #Print name for debugging purposes-------------------------------------
        print 'self.name: ', self.name
        print 'Current image: ', stack.current_frame
        print 'Predicted Points for current image\n', predicted
        print 'Ground truth data for current image\n', stack.point[stack.current_frame]
        #--------------------------------------------------------------------- 

