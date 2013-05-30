from Grammar import Chooser
import os
from pylab import *
import matplotlib.pyplot as plt

'''This file implements classes where the performance of predictors
is computed using different techniques.
Input: A stack of images, ground truth data, and a predictor
Output: A list and graphs that shows the performance of predictors
'''

class Error(Chooser):
    '''It is used to compute the error of predictions and ground-truth points. It
    outpus the difference (in pixels) to file and displays a graph.
    The error is according frames or according kind_point.
    Usage: ./chamview.py -c Error -d <image directory> -p <ground truth file>
    '''
    
    def setup(self):     
        
        #Debugging purposes-----------------------------------------------------
        print 'Running setup in Error'
        #-----------------------------------------------------------------------
        
        self.x = [] #Frame number
        self.y = [] #Error from ground-truth
        self.errorKindX = [] #Kind point number 
        self.errorKindY = [] #Error from ground-truth for each kind point
        self.name = [] #Name of predictor
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        self.className = 'Error' #The name of this class
        
        #Variable used to match with chamview.py requirements
        self.editedPointKinds = False

    def teardown(self):
        
        #Debugging purposes-------------------------------------------------------
        print 'Running teardown in Accuracy'
        #-------------------------------------------------------------------------
        
        #Define a initial figure
        plt.figure(1)
        
        #Define a subplot to graph error according to frames
        plt.subplot(211)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Save data to file
            fo = open(self.className+'_byFrame_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(self.y[i][j])+'\n')
            fo.close()
            
            #Plot the error in the subplot
            plt.plot(self.x[i],self.y[i])
            
        title(self.className + ' on Prediction')
        xlabel('Frame')
        ylabel(self.className)
        plt.legend(self.name)
        
        #Define a subplot to graph error according to kind points
        plt.subplot(212)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Save data to file
            fo = open(self.className+'_byPointKind_'+self.name[i]+'.txt','w')
            for j in range(0,self.errorKindX[i].shape[0]):
                fo.write(str(self.errorKindX[i][j]).zfill(4)+','+str(self.errorKindY[i][j])+'\n')
            fo.close()
        
            #Plot the error in the subplot
            plt.plot(self.errorKindX[i],self.errorKindY[i])
            
        title(self.className + ' on Prediction')
        xlabel('Point Kind')
        ylabel(self.className)
        plt.legend(self.name)
        
        plt.show()

    def choose(self,stack,predicted,predictor_name):
        
        #Debugging purposes--------------------------------------------------------
        print 'Running choose in Accuracy'
        #--------------------------------------------------------------------------
        
        #Print the frame number that we are working with
        print 'Frame '+str(stack.current_frame).zfill(4)+'/'+str(stack.total_frames).zfill(4)
        
        
        #Have we yet to take in Predictor info?
        if self.filledLists == False:
            
            self.filledLists = True
            
            for name in predictor_name:
                self.name.append(name)
                          
            for i in range(0,len(self.name)):
                self.x.append(arange(0,stack.total_frames,1))
                self.y.append(zeros(stack.total_frames))
                
                self.errorKindX.append(arange(0,stack.point_kinds,1))
                
            self.errorKindY = zeros((len(self.name), stack.point_kinds))

        #Get the accuracy of each predictor
        for pred in range(0,len(self.name)):
            
            #Add the accuracy given for each pointkind
            for pKind in range(0,stack.point_kinds):
                
                #Get distance between predicted and ground truth
                dx = predicted[pred, pKind, 0] - stack.point[stack.current_frame,pKind,0]
                dy = predicted[pred, pKind, 1] - stack.point[stack.current_frame,pKind,1]
            
                dist = (dx**2 + dy**2)**0.5
                
                #Add the distance error to the matrix y 
                self.y[pred][stack.current_frame] += dist
                
                #Add the distance error to the matrix errorKindY
                self.errorKindY[pred][pKind] += dist
            
        #Advance the frame (imagestack is 0-based, so if we hit total_frames
        #that means that we're out of images)
        stack.next()
        self.numImagesTested += 1
        
        if self.numImagesTested == stack.total_frames: stack.exit = True

        #Print informaction for debugging purposes------------------------------
        print 'self.name: ', self.name
        print 'Current image: ', stack.current_frame
        print 'Predicted Points for current image\n', predicted
        print 'Ground truth data for current image\n', stack.point[stack.current_frame]
    
        print 'x:\n', self.x
        print 'y:\n', self.y        
        #----------------------------------------------------------------------- 




class Performance(Chooser):
    
    """Can be used to find the difference between each Predictor and ground-truth
    points. Outputs the difference (in pixels) to file and displays a graph.
    Usage: ./chamview.py -c Performance -d <image directory> -p <ground truth file>
    
    """

    def setup(self):
        print 'Running_setup_method_in_Performance'
        '''
        self.x = [] #Frame number
        self.y = [] #Error from ground-truth
        self.name = [] #Name of predictor
        self.filledLists = False
        '''

    def teardown(self):
        print 'Running_teardown_method_in_Performance'
        '''
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
        '''

    def choose(self,stack,predicted,predictor_name):
        
        #Print something for debugging purposes
        print 'Running_choose_method_in_Performance'
        
        
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
        