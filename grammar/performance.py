# -*- coding: utf-8 -*-
from Grammar import Chooser
import os
from pylab import *
import matplotlib.pyplot as plt
#from mayavi.mlab import *

'''This file implements classes where the performance of predictors
is computed using different techniques.
Input: A stack of images, ground truth data, and a predictor
Output: A list and graphs that shows the performance of predictors
'''

class Performance(Chooser):
    '''It is used to compute the error of predictions and ground-truth points. It
    outpus the difference (in pixels) to file and displays a graph.
    The error is according frames or according kind_point.
    Usage: ./chamview.py -c Error -d <image directory> -p <ground truth file>
    '''
    
    def setup(self):     
        
        self.x = [] #Frame number
        self.errorKindX = [] #Kind point number
        self.y = [] #Error from ground-truth
        self.errorFrame = [] #Error compute by frame
        self.confidence = [] #Multidimensional array that saves the confidence
        
        self.name = [] #Name of predictor
        self.pointKList = [] #Name of the point kinds
        
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        self.className = 'Performance' #The name of this class
        self.upperB = 16 #Max number of pixels that we care about for error
        self.numPlots = 0 #Determine the number of plots showed
        
        #Variables used to match with chamview.py requirements
        self.editedPointKinds = False
        self.activePoint = -1
        self.selectedPredictions = []

    def teardown(self):
        
        #Print current informaction for debugging purposes----------------------
        print 'self.name: ', self.name
        print 'x:\n', self.x
        print 'y:\n', self.y     
        print 'errorKindX:\n', self.errorKindX   
        #----------------------------------------------------------------------- 

        #Compute the error by frame for each predictor to plot results in
        #different ways
        self.computeErrorByFrame()
        
        #Show results in text files and in graphs
        self.showErrorByFrame()
        self.showErrorByPointKind()
        self.showAccuracy()
        self.showAccuracyConfidence()
        self.showErrorEachPointK()
        
        

    def choose(self,stack,predicted,predictor_name):
    
        #Print the frame number that we are working with
        print 'Frame '+str(stack.current_frame).zfill(4)+'/'+str(stack.total_frames).zfill(4)
        
        #Have we yet to take in Predictor info?
        if self.filledLists == False:
            self.filledLists = True
                    
            self.name = predictor_name
            self.pointKList = stack.point_kind_list
            
            for i in range(0,len(self.name)):
                self.x.append(arange(0,stack.total_frames,1))
                self.errorKindX.append(arange(0,stack.point_kinds,1) + 1)

            #A 3-dimensional array for error
            #1.- predictor, 2.- frame, 3.- point kind
            self.y = zeros((len(self.name), stack.total_frames, stack.point_kinds))
            
            #A 3-dimensional array for confidence in predictions
            #1.- predictor, 2.- frame, 3.- point kind
            self.confidence = zeros((len(self.name), stack.total_frames, stack.point_kinds))

        #Get the accuracy of each predictor
        for pred in range(0,len(self.name)):
            
            #Add the accuracy given for each pointkind
            for pKind in range(0,stack.point_kinds):
                
                #Get distance between predicted and ground truth
                dx = predicted[pred, pKind, 0] - stack.point[stack.current_frame,pKind,0]
                dy = predicted[pred, pKind, 1] - stack.point[stack.current_frame,pKind,1]
            
                dist = (dx**2 + dy**2)**0.5
                
                #Add the distance error to the matrix y 
                self.y[pred][stack.current_frame][pKind] = dist
                #Add confidence of prediction
                self.confidence[pred][stack.current_frame][pKind] = predicted[pred, pKind, 2]
            
        #Advance the frame (imagestack is 0-based, so if we hit total_frames
        #that means that we're out of images)
        stack.next()
        self.numImagesTested += 1
        
        if self.numImagesTested == stack.total_frames: stack.exit = True
        
        #Printing information for debugging purposes----------------------------
        print 'Current image: ', stack.current_frame
        print 'Predicted Points for current image\n', predicted
        print 'Ground truth data for current image\n', stack.point[stack.current_frame]
        #-----------------------------------------------------------------------
            
    def showErrorByFrame(self):
        
        print 'Plot graph of errors in predictors by frames'
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Get the error by frame array at position i
            yPlot = zeros(len(self.errorFrame[i]))
            for j in range(0,len(yPlot)):            
                yPlot[j] = self.errorFrame[i][j]
            
            #Cut error by a given upper bound
            yPlot = self.cutArray(yPlot, self.upperB)
            
            #Save data to file
            fo = open('Error_byFrame_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()
            
            #Plot the error in the subplot
            plt.plot(self.x[i],yPlot)
            
        title('Error on Prediction')
        xlabel('Frame')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        plt.show()
        
    def showErrorByPointKind(self):

        print 'Plot graph of errors in predictors by point kinds'
        
        self.numPlots += 1
        
        #Define a new figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
        
            #An array that contains the averages of errors by point kind
            yPlot = zeros(len(self.y[i][0]))
            
            for pointK in range(0,len(yPlot)):
                for frame in range(0,len(self.y[i])):
                    yPlot[pointK] += sum(self.y[i][frame][pointK])
            #Divide over the number of frames
            yPlot = yPlot / len(self.y[i])  
        
        
            #Cut error by a given upper bound
            yPlot = self.cutArray(yPlot, self.upperB)    
                                      
            #Save data to file
            fo = open('Error_byPointKind_'+self.name[i]+'.txt','w')
            for j in range(0,self.errorKindX[i].shape[0]):
                fo.write(str(self.errorKindX[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()
        
            #Plot the error in the subplot
            plt.plot(self.errorKindX[i],yPlot)
            
        title('Error on Prediction')
        xlabel('Point Kind')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        
        plt.show()

    def showErrorEachPointK(self):
        
        print 'Plot graphs with error of predictors for each kind point'        
        
        #Go through each point kind
        for pointK in range(0, len(self.y[0][0])):
            
            self.numPlots += 1
            #Define a new figure
            plt.figure(self.numPlots)
            
            
            #Go through each predictor
            for i in range(0,len(self.name)):
        
                #Get the error by frame array at position i
                yPlot = zeros(len(self.y[i]))
                for frame in range(0,len(yPlot)):            
                    yPlot[frame] = self.y[i][frame][pointK]
            
                #Cut error by a given upper bound
                yPlot = self.cutArray(yPlot, self.upperB)
            
                '''#Save data to file
                fo = open('Error_byFrame_pointK_'+str(pointK+1)+'_'+self.name[i]+'.txt','w')
                for j in range(0,self.x[i].shape[0]):
                    fo.write(str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
                fo.close()'''
            
                #Plot the error in the subplot
                plt.plot(self.x[i],yPlot)
            
            title('Error on ' + self.pointKList[pointK])
            xlabel('Frame')
            ylabel('Number of Pixels')
            plt.legend(self.name)
        
            plt.show()
            
        
    def showAccuracy(self):
        
        print 'Plot graph for accuracy in predictors by frames'
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Get the error by frame array at position i
            yPlot = self.errorFrame[i]
            
            #Add one to the errors in order to get inverse
            yPlot = yPlot + 1
            #Take the inverse of the result
            yPlot = yPlot ** -1
            
            '''#Save data to file
            fo = open('Accuracy_byFrame_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()'''
            
            #Plot the error in the subplot
            plt.plot(self.x[i], yPlot)
            
        title('Accuracy on Prediction')
        xlabel('Frame')
        ylabel('Accuracy')
        plt.legend(self.name)
        plt.show()
        
    def showAccuracyConfidence(self):
        
        print 'Plot graph for accuracy and confidence in predictors by frames'
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Define a 3-dimensional array that will contain accuracy * Confidence
        accConfidence = zeros((len(self.y), len(self.y[0]), len(self.y[0][0])))
        
        for pred in range(0,len(accConfidence)):
            for frame in range(0,len(accConfidence[0])):
                for pointK in range(0,len(accConfidence[0][0])):
                    error = self.y[pred][frame][pointK]
                    conf = self.confidence[pred][frame][pointK]
                    accConfidence[pred][frame][pointK] = ((error+1)**-1)*conf
        
        #Define a 2-dimensional array that contains the average of accConfidence
        #for each frame
        yaccConf = zeros((len(self.y), len(self.y[0])))
        for pred in range(0,len(yaccConf)):
            for frame in range(0,len(yaccConf[0])):
                yaccConf[pred][frame] = sum(accConfidence[pred][frame])
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Get the error by frame array at position i
            yPlot = yaccConf[i]
            
            '''#Save data to file
            fo = open('AccuracyandConfidence_byFrame_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()'''
            
            #Plot the error in the subplot
            plt.plot(self.x[i], yPlot)
            
        title('Accuracy and Confidence on Prediction')
        xlabel('Frame')
        ylabel('Accuracy * Confidence')
        plt.legend(self.name)
        plt.show()     

    def computeErrorByFrame(self):
        
        #Create a 2-dimensional array, predictors x frames
        self.errorFrame = zeros((len(self.name), len(self.y[0])))
        
        for pred in range(0,len(self.errorFrame)):
            for frame in range(0,len(self.errorFrame[0])):
                self.errorFrame[pred][frame] = sum(self.y[pred][frame])
        #Divide over the number of point kinds
        self.errorFrame = self.errorFrame / len(self.y[0][0])  
        
        #Debugging purposes-----------------------------------------------------
        print 'errorFrame:\n', self.errorFrame
        #-----------------------------------------------------------------------
        
    def cutArray(self, array, upperBound):
        '''This method takes an array and every value greater than the upper
        bound is changed to upper bound''' 
        
        for i in range(0,len(array)):
            
            if array[i] > upperBound:
                array[i] = upperBound
                
        return array