# -*- coding: utf-8 -*-
#This class implements evaluators for Chamview predictors
#Manuel E. Dosal
#May 28, 2013

from Grammar import Chooser
import os
from pylab import *
import matplotlib.pyplot as plt
from decimal import *
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

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
        self.outputName = 'Performance_Report.txt' #Name of output file
        
        #Variables from Image Stack class
        self.name = [] #Name of predictor
        self.pointKList = [] #Name of the point kinds
        self.totalFrames = 0 #Keep track of the number of frames of dataset
        self.totalPointK = 0 #Keep track of the number of point kinds of dataset
        
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        self.upperB =  50 #Max number of pixels that we care about for error
        self.tpBound = 5 #Bound to split True Positives and False Negatives
        self.numPlots = 0 #Determine the number of plots showed
        
        #Variables used to match with chamview.py requirements
        self.editedPointKinds = False
        self.activePoint = -1
        self.selectedPredictions = []
        self.stagedToSave = False
        
        #Variables used to save information into a text file
        self.fo = None 
        self.division = '--\n' #String that determines the division between two evaluations
        self.predLabel = 'Predictor: '
        self.graphNames = ['ERROR BY FRAME\n']

    def setupPar(self,argEvaluate):
        
        #Get parameters: Output-upperBound-TruePositiveBound
        parameters = argEvaluate.split('-')
        
        #Update variables
        if parameters[0] != '': self.outputName = parameters[0]
        if parameters[1] != '': self.upperB = int(parameters[1])
        if parameters[2] != '': self.tpBound = int(parameters[2])

    def teardown(self):

        #Compute the error by frame for each predictor to plot results in
        #different ways
        self.computeErrorByFrame()
        
        #Open a text file to save results
        self.fo = open(self.outputName,'w')
        self.fo.write('THIS FILE CONTAINS RESULTS OBTAINED OF PREDICTORS EVALUATION\n')
        self.fo.write('(We do not care about errors above ' + str(self.upperB) + 
                      ' pixels and they are written as INF)\n')        
        #self.showAccuracyConfidence()
        
        #Show results in text files and in graphs
        self.showErrorByFrame()
        self.showErrorByPointKind()
        self.showErrorEachPointK()
        self.showPercentageError()
        self.showROC()
        self.showAccuracy()
        #self.showError3D()
        
        #Close text file
        self.fo.close()
        print 'Report saved to ' + self.outputName

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
                
                xGT = stack.point[stack.current_frame, pKind, 0]
                yGT = stack.point[stack.current_frame, pKind, 1]
                
                if xGT == 0 and yGT == 0:
                    #If point has no ground truth, make the distance the largest possible
                    dist = self.upperB + 1
                else:
                    #Get distance between predicted and ground truth
                    dx = predicted[pred, pKind, 0] - xGT
                    dy = predicted[pred, pKind, 1] - yGT
            
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
                                 
    def showErrorByFrame(self):
                
        #Save title in text file and in graphNames array
        gName = 'ERROR BY FRAME'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n')
            
            #Get the error by frame array at position i
            yPlot = zeros(len(self.errorFrame[i]))
            for j in range(0,len(yPlot)):            
                yPlot[j] = self.errorFrame[i][j]
            
            #Cut error by a given upper bound
            yPlot = self.cutArray(yPlot, self.upperB)
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                if yPlot[j] >= self.upperB: yVal = 'INF' 
                else: yVal = yPlot[j]
                self.fo.write('  ' + str(self.x[i][j]).zfill(4)+','+ str(yVal) +'\n')
                        
            #Plot the error in the subplot
            plt.plot(self.x[i],yPlot)
            
        #Write division into file
        self.fo.write(self.division)
        
        title('Error on Prediction\nThis graph shows errors less or equal than '
               +str(self.upperB)+' pixels')
        xlabel('Frame')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        plt.show()
        
    def showErrorByPointKind(self):
        
        #Save title in text file and in graphNames array
        gName = 'ERROR BY POINT KIND'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
        self.numPlots += 1
        #Define a new figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n')
        
            #An array that contains the averages of errors by point kind
            yPlot = zeros(self.totalPointK)
            
            for pointK in range(0,len(yPlot)):
                for frame in range(0,self.totalFrames):
                    yPlot[pointK] += self.y[i][frame][pointK]            
            #Divide over the number of frames
            yPlot = yPlot / len(self.y[i])  
        
            #Cut error by a given upper bound
            yPlot = self.cutArray(yPlot, self.upperB)    
                                      
            #Save data to file
            for j in range(0,self.errorKindX[i].shape[0]):
                if yPlot[j] >= self.upperB: yVal = 'INF' 
                else: yVal = yPlot[j]
                self.fo.write('  ' + self.pointKList[j] +','+str(yVal)+'\n')
            
            #Plot error
            xPlot = arange(self.totalPointK)
            width = 0.35
            plt.bar(xPlot + width * i, yPlot, width, color=cm.jet(1.*i/len(xPlot)))
            plt.xticks( xPlot + 0.5,  self.pointKList)
            
        #Write division into file
        self.fo.write(self.division)
            
        title('Error on Prediction\nThis graph shows errors less or equal than '
               +str(self.upperB)+' pixels')
        xlabel('Point Kind')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        plt.show()

    def showErrorEachPointK(self):
        
        #Save title in text file and in graphNames array
        gName = 'ERROR FOR EACH POINT KIND'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
        #Go through each point kind
        for pointK in range(0, self.totalPointK):
            
            self.fo.write(' Point Kind: ' + self.pointKList[pointK] + '\n') #Write point kind
            
            self.numPlots += 1
            #Define a new figure
            plt.figure(self.numPlots)
            
            
            #Go through each predictor
            for i in range(0,len(self.name)):
        
                self.fo.write('  ' + self.predLabel + self.name[i] + '\n')
        
                #Get the error by frame array at position i
                yPlot = zeros(len(self.y[i]))
                for frame in range(0,len(yPlot)):            
                    yPlot[frame] = self.y[i][frame][pointK]
            
                #Cut error by a given upper bound
                yPlot = self.cutArray(yPlot, self.upperB)
            
                #Save data to file
                for j in range(0,self.x[i].shape[0]):
                    if yPlot[j] >= self.upperB: yVal = 'INF' 
                    else: yVal = yPlot[j]
                    self.fo.write('   ' + str(self.x[i][j]).zfill(4)+','+str(yVal)+'\n')
            
                #Plot the error in the subplot
                plt.plot(self.x[i],yPlot, lw = 1)
            
            title('Point Kind: ' + self.pointKList[pointK]+'\nThis graph shows errors less or equal than '
                  +str(self.upperB)+' pixels')
            xlabel('Frame')
            ylabel('Number of Pixels')
            plt.legend(self.name)
        
            plt.show()
        
        #Write division into file
        self.fo.write(self.division)
            
    def showPercentageError(self):
        
        #Save title in text file and in graphNames array
        gName = 'PERCENTAGE OF ERROR'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n') #Write predictor name
            
            #Define an array that will save the errors for predictor i
            errors = zeros(self.totalFrames * self.totalPointK)
            itr = 0;
            
            for frame in range(0,self.totalFrames):
                for pointK in range(0,self.totalPointK):
                    errors[itr] = self.y[i][frame][pointK]
                    itr += 1
            
            #Sort errors array
            errors.sort()
            
            yPlot = zeros(self.upperB + 1)
            xPlot = arange(0,self.upperB + 1,1)
            
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
            for j in range(0,xPlot.shape[0]):
                self.fo.write('  ' + str(xPlot[j]).zfill(4)+','+str(yPlot[j])+'\n')
                        
            #Plot the error in the subplot
            plt.plot(xPlot,yPlot, lw = 1)
            
        #Write division into file
        self.fo.write(self.division)
        
        title('Percentage of Error\n(For a given error from 1 to ' + 
              str(self.upperB) + ' pixels,\nthe next graph shows the percentage of ' +
              'points with at most that error)\n') 
        xlabel('Error in Pixels')
        ylabel('Percentage of Points')
        plt.legend(self.name)
        plt.show()
        
    def showAccuracy(self):
                
        #Save title in text file and in graphNames array
        gName = 'ACCURACY IN PREDICTION'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n')
            
            #Get the error by frame array at position i
            yPlot = self.errorFrame[i]
            
            #Add one to the errors in order to get inverse
            yPlot = yPlot + 1
            #Take the inverse of the result
            yPlot = yPlot ** -1
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                self.fo.write('  ' + str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            
            #Plot the error in the subplot
            plt.plot(self.x[i], yPlot, lw = 1)
           
        #Write division into file
        self.fo.write(self.division) 
  
        title('ACCURACY ON PREDICTION\n')
        xlabel('Frame')
        ylabel('Accuracy')
        plt.legend(self.name)
        plt.show()
        
    def showAccuracyConfidence(self):
       
        #Save title in text file and in graphNames array
        gName = 'ACCURACY WITH CONFIDENCE'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
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
            
            self.fo.write(' ' + self.predLabel + self.name[i])
            
            #Get the error by frame array at position i
            yPlot = yaccConf[i]
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                self.fo.write(' ' + str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            
            #Plot the error in the subplot
            plt.plot(self.x[i], yPlot, lw = 1)
            
        #Write division into file
        self.fo.write(self.division)

        title('Accuracy and Confidence on Prediction')
        xlabel('Frame')
        ylabel('Accuracy * Confidence')
        plt.legend(self.name)
        plt.show()     
        
    def showROC(self):
   
        #Save title in text file and in graphNames array
        gName = 'RECEIVER OPERATING CHARACTERISTIC (ROC) CURVE'
        self.fo.write('\n' + gName + '\n')
        self.graphNames.append(gName)
        
        self.numPlots += 1
        #Define a new figure
        plt.figure(self.numPlots)
        
        for pred in range(0,len(self.y)):
            
            self.fo.write(' ' + self.predLabel + self.name[pred] + '\n')
            
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
                     
            #Write results into file
            for i in range(0, len(xPlot)):
                self.fo.write('  ' + str(xPlot[i]) + ', ' + str(yPlot[i]) + '\n')                           
                                                                                 
            #Plot the error
            plt.plot(xPlot, yPlot, lw = 1)
         
        #Write division into file
        self.fo.write(self.division)   
                  
        title('Receiver Operating Characteristic (ROC) Curve\n'+
              'A predictor is better if its curve is above other')
        xlabel('False Positive Rate')
        ylabel('True Positive Rate')
        plt.legend(self.name)
        plt.show()          
      
    def showError3D(self):
        
        #Write title in text file
        self.fo.write('\nERROR FOR EACH PREDICTOR IN 3D\n')
        
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
            title('Error in Predictor: ' + self.name[i])
            xlabel('Frames')
            ylabel('Point Kinds')
            plt.legend(self.name)
            
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