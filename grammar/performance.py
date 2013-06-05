# -*- coding: utf-8 -*-
from Grammar import Chooser
import os
from pylab import *
import matplotlib.pyplot as plt
from decimal import *
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
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
        self.totalFrames = 0 #Keep track of the number of frames of dataset
        self.totalPointK = 0 #Keep track of the number of point kinds of dataset
        
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        self.className = 'Performance' #The name of this class
        self.upperB = 50 #Max number of pixels that we care about for error
        self.tpBound = 15 #Bound to split True Positives and False Negatives
        self.numPlots = 0 #Determine the number of plots showed
        
        #Variables used to match with chamview.py requirements
        self.editedPointKinds = False
        self.activePoint = -1
        self.selectedPredictions = []

    def teardown(self):
        
        #Print current informaction for debugging purposes----------------------
        #print 'self.name: ', self.name
        #print 'x:\n', self.x
        #print 'y:\n', self.y     
        #print 'errorKindX:\n', self.errorKindX   
        #----------------------------------------------------------------------- 

        #Compute the error by frame for each predictor to plot results in
        #different ways
        self.computeErrorByFrame()
        
        #self.showAccuracyConfidence()
        
        #Show results in text files and in graphs
        self.showErrorByFrame()
        self.showErrorByPointKind()
        self.showAccuracy()
        self.showErrorEachPointK()
        self.showROC()
        self.showPercentageError()
        self.showError3D()
        
        

    def choose(self,stack,predicted,predictor_name):
    
        #Print the frame number that we are working with
        #print 'Frame '+str(stack.current_frame).zfill(4)+'/'+str(stack.total_frames).zfill(4)
        
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
            
            #Get the total of point kinds and total of frames
            self.totalFrames = stack.total_frames
            self.totalPointK = stack.point_kinds

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
        #print 'Current image: ', stack.current_frame
        #print 'Predicted Points for current image\n', predicted
        #print 'Ground truth data for current image\n', stack.point[stack.current_frame]
        #-----------------------------------------------------------------------
     
            
    def showPercentageError(self):
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            #Define an array that will save the errors for predictor i
            errors = zeros(self.totalFrames * self.totalPointK)
            itr = 0;
            
            for frame in range(0,self.totalFrames):
                for pointK in range(0,self.totalPointK):
                    errors[itr] = self.y[i][frame][pointK]
                    itr += 1
            
            #Sort errors array
            errors.sort()
            
            yPlot = zeros(self.upperB)
            xPlot = arange(0,self.upperB,1)
            
            #Define two variables that traverse errors and yPlot arrays
            err = 0
            e = 0
            while e < len(errors) and err < len(yPlot):
                if errors[e] <= err:
                    e += 1
                else:
                    yPlot[err] = e
                    err += 1
            
            #Compute percentage of points
            yPlot = yPlot * 100 / len(errors)
            
            #Fill out the rest of the point
            for j in range(err, len(yPlot)):
                yPlot[j] = 100 
            
            #Save data to file
            fo = open('Percentage_of_Error'+self.name[i]+'.txt','w')
            for j in range(0,xPlot.shape[0]):
                fo.write(str(xPlot[j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()
                        
            #Plot the error in the subplot
            plt.plot(xPlot,yPlot)
            
        title('Percentage of Error\nThis graph shows the percentage of points'
             +'predicted with error less or equal than ' + str(self.upperB) + ' pixels') 
        xlabel('Error in Pixels')
        ylabel('Percentage of Points')
        plt.legend(self.name)
        plt.show()              
                                 
    def showErrorByFrame(self):
                
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
            '''fo = open('Error_byFrame_'+self.name[i]+'.txt','w')
            for j in range(0,self.x[i].shape[0]):
                fo.write(str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()'''
                        
            #Plot the error in the subplot
            plt.plot(self.x[i],yPlot)
            
        title('Error on Prediction\nThis graph shows errors less or equal than '
               +str(self.upperB)+' pixels')
        xlabel('Frame')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        plt.show()
        
    def showErrorByPointKind(self):
        
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
            '''fo = open('Error_byPointKind_'+self.name[i]+'.txt','w')
            for j in range(0,self.errorKindX[i].shape[0]):
                fo.write(str(self.errorKindX[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            fo.close()'''
        
            #Plot the error in the subplot
            plt.plot(self.errorKindX[i],yPlot)
            
        title('Error on Prediction\nThis graph shows errors less or equal than '
               +str(self.upperB)+' pixels')
        xlabel('Point Kind')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        plt.show()

    def showErrorEachPointK(self):
                
        #Go through each point kind
        for pointK in range(0, self.totalPointK):
            
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
            
            title('Point Kind: ' + self.pointKList[pointK]+'\nThis graph shows errors less or equal than '
                  +str(self.upperB)+' pixels')
            xlabel('Frame')
            ylabel('Number of Pixels')
            plt.legend(self.name)
        
            plt.show()
            
        
    def showAccuracy(self):
                
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
            
        title('Accuracy on Prediction\n'
              + 'It is a number between 0 and 1. Close to 1 means good prediction')
        xlabel('Frame')
        ylabel('Accuracy')
        plt.legend(self.name)
        plt.show()
        
    def showAccuracyConfidence(self):
                
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Define a 3-dimensional array that will contain accuracy * Confidence
        accConfidence = zeros((len(self.y), self.totalFrames, self.totalPointK))
        
        for pred in range(0,len(accConfidence)):
            for frame in range(0,len(accConfidence[0])):
                for pointK in range(0,len(accConfidence[0][0])):
                    error = self.y[pred][frame][pointK]
                    conf = self.confidence[pred][frame][pointK]
                    accConfidence[pred][frame][pointK] = ((error+1)**-1)*conf
        
        #Define a 2-dimensional array that contains the average of accConfidence
        #for each frame
        yaccConf = zeros((len(self.y), self.totalFrames))
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
        
    def showROC(self):
                
        self.numPlots += 1
        #Define a new figure
        plt.figure(self.numPlots)
        
        for pred in range(0,len(self.y)):
            
            numTP = 0
            numFP = 0
            
            #Here we count the number of True positives and False positives
            for frame in range(0,self.totalFrames):
                for pointK in range(0,self.totalPointK):
                    if self.y[pred][frame][pointK] <= self.tpBound:
                        numTP += 1
                    else:
                        numFP += 1
            
            #Define the units for true positives and false positives
            if numTP > 0:
                tpUnit = 1 / Decimal(numTP) 
            else:
                tpUnit = 0.0
            if numFP > 0:
                fpUnit = 1 / Decimal(numFP)
            else:
                fpUnit = 1.0
            
            
            #Debugging purposes-------------------------------------------------
            #print 'Predictor: ',pred
            #print 'numTP: ', numTP
            #print 'numFP: ', numFP
            #print 'tpUnit: ',tpUnit
            #print 'fpUnit: ', fpUnit
            #-------------------------------------------------------------------
            
            #Define arrays that are our x and y axis
            xPlot = arange(0,1 + fpUnit,fpUnit) 
            yPlot = zeros(len(xPlot))
            
            #Define a variable that know what is the current TP rate
            TPrate = 0
            
            itr = 0
            #Here we compute the TPrate and FPrate and then plot it
            for frame in range(0,self.totalFrames):
                for pointK in range(0,self.totalPointK):
                    if self.y[pred][frame][pointK] <= self.tpBound:
                        #Add to True Positives
                        TPrate += tpUnit
                        yPlot[itr] = TPrate
                    else:
                        #Add to False Negatives
                        itr += 1
                        yPlot[itr] = TPrate

            #Fill last position as 1
            yPlot[len(yPlot)-1] = 1
                                         
            #Plot the error in the subplot
            plt.plot(xPlot, yPlot)
            
        title('Receiver Operating Characteristic (ROC) Curve\n'+
              'A predictor is better if its curve is above other')
        xlabel('False Positive Rate')
        ylabel('True Positive Rate')
        plt.legend(self.name)
        plt.show()          
      
    def showError3D(self):
        
        #For each predictor
        for i in range(0,len(self.y)):
        
            self.numPlots += 1
            #Define a new figure
            fig = plt.figure(self.numPlots)    
                    
            #Define arrays for all axis
            xPlot = arange(0,self.totalFrames)
            yPlot = arange(0,self.totalPointK)
            
            xPlot, yPlot = np.meshgrid(xPlot, yPlot)
                                
            zPlot = zeros(self.totalFrames * self.totalPointK)
            
            #Fill up z axis vector
            itr = 0
            for frame in range(0,self.totalFrames):
                for pointK in range(0,self.totalPointK):
                    newError = self.y[i][frame][pointK]
                    if newError <= self.upperB:
                         zPlot[itr] = newError
                    else:
                        zPlot[itr] = self.upperB
                    itr += 1
                    
            zPlot = np.array(zPlot).reshape(xPlot.shape)
                    
            ax = fig.gca(projection='3d')
            
            surf = ax.plot_surface(xPlot, yPlot, zPlot, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)

            ax.zaxis.set_major_locator(LinearLocator(10))
            ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

            fig.colorbar(surf, shrink=0.5, aspect=5)
            
            #Messages for plot
            title('Error in Predictor: ' + self.name[i] + 
                 '\nRed color means high error, Blue color means low error')
            xlabel('Frames')
            ylabel('Point Kinds')
            #zlabel('Error in Pixels')
            plt.legend(self.name)
            #text(1, 1, 'Anything', fontsize=12) 
            
            plt.show() 
                            

    def computeErrorByFrame(self):
        
        #Create a 2-dimensional array, predictors x frames
        self.errorFrame = zeros((len(self.name), self.totalFrames))
        
        for pred in range(0,len(self.errorFrame)):
            for frame in range(0,len(self.errorFrame[0])):
                self.errorFrame[pred][frame] = sum(self.y[pred][frame])
        #Divide over the number of point kinds
        self.errorFrame = self.errorFrame / self.totalPointK  
        
    def cutArray(self, array, upperBound):
        '''This method takes an array and every value greater than the upper
        bound is changed to upper bound''' 
        
        for i in range(0,len(array)):
            
            if array[i] > upperBound:
                array[i] = upperBound
                
        return array