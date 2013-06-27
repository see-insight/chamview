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

'''This file implements classes where the performance of predictors is computed.
Input: A stack of images, ground truth data, and a predictor
Output: A list and graphs that show the performance of predictors
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
        self.totalPredictors = 0 #Number of predictors
        self.totalFrames = 0 #Keep track of the number of frames of dataset
        self.totalPointK = 0 #Keep track of the number of point kinds of dataset
        self.maxDistance = 0 #Contains the maximum distance between two point in a frame
        
        self.filledLists = False
        self.numImagesTested = 0 #Keeps track of the number of images tested
        self.upperB =  50 #Max number of pixels that we care about for error
        self.tpBound = 5 #Bound to split True Positives and False Negatives
        self.numPlots = 0 #Determine the number of plots showed
        
        #Variables used to save information into a text file
        self.fo = None 
        self.division = '--\n' #String that determines the division between two evaluations
        self.predLabel = 'Predictor: ' #String that saves the label for predictors in text file
        self.pointKLabel = 'Point Kind: ' #String that saves the label for point kind in text file
        self.numPredictorsL = 'Number_of_Predictors: ' #Label for number of predictors 
        self.numFramesL = 'Number_of_Frames: ' #Label for number of frames
        self.numPointKL = 'Number_of_Point_Kinds: ' #Label for number of point kinds
        self.upperBoundL = 'Upper_Bound: ' #Label for the upper bound
        self.infVal = 'INF' #Label that indicates the error is very large
        #Define an array that saves all the graph names
        self.oracleN = 'Oracle'
        self.graphNames = ['ERROR BY FRAME\n', 'ERROR BY POINT KIND\n', 'PERCENTAGE OF POINTS\n']
        self.graphNames.append('RECEIVER OPERATING CHARACTERISTIC (ROC) CURVE\n')
        self.graphNames.append('ACCURACY IN PREDICTION\n')
        
        #Variables used to match with chamview.py requirements
        self.editedPointKinds = False
        self.activePoint = -1
        self.selectedPredictions = []
        self.stagedToSave = ['', '']

    def setupPar(self,argEvaluate):
        
        #Get parameters: Output-upperBound-TruePositiveBound
        parameters = argEvaluate.split('-')
        
        #Update variables
        if parameters[0] != '': self.outputName = parameters[0]
        if parameters[1] != '': self.upperB = int(parameters[1])
        if parameters[2] != '': self.tpBound = int(parameters[2])

    def teardown(self):

        #Define Oracle predictor, build it, and append results to other predictors results
        self.appendOracle()

        #Compute the error by frame for each predictor to plot results in
        #different ways
        self.computeErrorByFrame()
        
        #Open a text file to save results
        self.fo = open(self.outputName,'w')
        self.fo.write('THIS FILE CONTAINS RESULTS OBTAINED OF PREDICTORS EVALUATION\n')
               
        #Save important values in text file
        self.fo.write(self.numPredictorsL + str(self.totalPredictors) + '\n')
        self.fo.write(self.numFramesL + str(self.totalFrames) + '\n')
        self.fo.write(self.numPointKL + str(self.totalPointK) + '\n')
        
        #TURN ON OR OFF THE GRAPHS THAT NEED TO BE DISPLAYED
        
        #Possible graphs that can be used in a future
        #self.showAccuracyConfidence()
        #self.showError3D()
        #self.showROC()
        #self.showConfidence()
        
        #Show results in text files and in graphs
        self.showErrorByFrame()
        self.showErrorByPointKind()
        self.showErrorEachPointK()
        self.showAccuracy()
        self.showPercentageError()
        
        #Close text file
        self.fo.close()
        print 'Report saved to ' + self.outputName

    def choose(self,stack,predicted,predictor_name):
        
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
            self.totalPredictors = len(predictor_name)

        #Compute maximum distance of current image
        maxD = (stack.img_current.size[0]**2 + stack.img_current.size[1]**2)**0.5
        if maxD > self.maxDistance: self.maxDistance = maxD         
        
        #Get the accuracy of each predictor
        for pred in range(0,len(self.name)):
            
            #Add the accuracy given for each pointkind
            for pKind in range(0,stack.point_kinds):
                
                xGT = stack.point[stack.current_frame, pKind, 0]
                yGT = stack.point[stack.current_frame, pKind, 1]
                
                if xGT == 0 and yGT == 0:
                    #If point has no ground truth, do not count it, put -1
                    dist = -1
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
        
        if self.numImagesTested == stack.total_frames:
            
            stack.exit = True              
                                 
    def showErrorByFrame(self):
                
        #Save title in text file and in graphNames array
        gName = 'ERROR BY FRAME'
        self.fo.write('\n' + gName + '\n')
        
        #Define a new figure
        self.numPlots += 1
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n')
            
            #Get the error by frame array at position i
            yPlot = zeros(len(self.errorFrame[i]))
            for j in range(0,len(yPlot)):            
                yPlot[j] = self.errorFrame[i][j]
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                self.fo.write('  ' + str(self.x[i][j]).zfill(4)+','+ str(yPlot[j]) +'\n')
            
            #Cut error by a given upper bound
            yPlot = self.cutArray(yPlot, self.upperB)
            
            #Sort errors to avoid annoying graphs
            yPlot.sort()
        
            #Plot the error in the subplot
            if self.name[i] != self.oracleN:
                plt.plot(self.x[i], yPlot)
            else:
                plt.plot(self.x[i], yPlot, '--', color = 'k')
            
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
        
        self.numPlots += 1
        #Define a new figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n')
        
            #An array that contains the averages of errors by point kind
            yPlot = zeros(self.totalPointK)
            
            for pointK in range(0,len(yPlot)):
                count = 0 #Variable that counts errors well computed
                for frame in range(0,self.totalFrames):
                    err = self.y[i][frame][pointK]
                    if err >= 0:    
                        yPlot[pointK] += err
                        count += 1            
                if count == 0:
                    yPlot[pointK] = -1
                else:
                    #Divide over the number of frames
                    yPlot[pointK] /= count
        
            #Save data to file
            for j in range(0,self.errorKindX[i].shape[0]):
                self.fo.write('  ' + self.pointKList[j] +','+str(yPlot[j])+'\n')
        
            #Cut error by a given upper bound
            yPlot = self.cutArray(yPlot, self.upperB)    
            
            #Plot error
            xPlot = arange(self.totalPointK)
            width = 1.0 / self.totalPredictors
            
            if self.name[i] != self.oracleN:
                plt.bar(xPlot + width * i, yPlot, width, color=cm.jet(1.*i/len(xPlot)))
            else:
                plt.bar(xPlot + width * i, yPlot, width, color='k')
                
            plt.xticks( xPlot + 0.5,  self.pointKList)
            
        #Write division into file
        self.fo.write(self.division)
            
        title('Error by Point Kind\nThis graph shows errors less or equal than '
               +str(self.upperB)+' pixels')
        xlabel('Point Kind')
        ylabel('Number of Pixels')
        plt.legend(self.name)
        plt.show()

    def showErrorEachPointK(self):
        
        #Save title in text file and in graphNames array
        gName = 'ERROR FOR EACH POINT KIND'
        self.fo.write('\n' + gName + '\n')
        
        #Go through each point kind
        for pointK in range(0, self.totalPointK):
            
            self.fo.write(' ' + self.pointKLabel + self.pointKList[pointK] + '\n') #Write point kind
            
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
            
                #Save data to file
                for j in range(0,self.x[i].shape[0]):
                    self.fo.write('   ' + str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            
                #Cut error by a given upper bound
                yPlot = self.cutArray(yPlot, self.upperB)
                
                #Sort errors to avoid annoying graphs
                yPlot.sort()
            
                #Plot the error in the subplot
                if self.name[i] != self.oracleN:                                    
                    plt.plot(self.x[i],yPlot, lw = 1)
                else:
                    plt.plot(self.x[i], yPlot, '--', color = 'k', lw = 1)
            
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
        gName = 'PERCENTAGE OF POINTS'
        self.fo.write('\n' + gName + '\n')
        
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
                    error = self.y[i][frame][pointK]
                    if error >= 0:
                        errors[itr] = error 
                        itr += 1

            errors = errors[0:itr]
            
            #Sort errors array
            errors.sort()
            
            yPlot = zeros(int(self.maxDistance))
            xPlot = arange(0,int(self.maxDistance), 1)
            
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
            for j in range(0, xPlot.shape[0]):
                self.fo.write('  ' + str(xPlot[j]).zfill(4)+','+str(yPlot[j])+'\n')
                        
            #Take only the important part to plot
            xPlot = xPlot[:self.upperB + 1]
            yPlot = yPlot[:self.upperB + 1]

            #Plot the error in the subplot
            if self.name[i] != self.oracleN:                
                plt.plot(xPlot,yPlot, lw = 1)
                plt.scatter(xPlot, yPlot, s=5)
            else:
                plt.plot(xPlot,yPlot, '--', color = 'k', lw = 1)
            
        #Write division into file
        self.fo.write(self.division)
        
        title('Percentage of Points\n(For a given error from 1 to ' + 
              str(self.upperB) + ' pixels,\nthe next graph shows the percentage of ' +
              'points with at most that error)') 
        xlabel('Error in Pixels')
        ylabel('Percentage of Points')
        plt.legend(self.name)
        plt.show()
        
    def showAccuracy(self):
                
        #Save title in text file and in graphNames array
        gName = 'ACCURACY IN PREDICTION'
        self.fo.write('\n' + gName + '\n')
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Go through each predictor
        for i in range(0,len(self.name)):
            
            self.fo.write(' ' + self.predLabel + self.name[i] + '\n')
            
            #Define y-array for plot
            yPlot = zeros(self.totalFrames)
            
            for frame in range(0, self.totalFrames): 

                for pointK in range(0, self.totalPointK):
                    if self.y[i][frame][pointK] <= self.tpBound:
                        yPlot[frame] += 1
                
                #Add previous accuracy
                yPlot[frame] += yPlot[frame - 1] * frame * self.totalPointK
                #Compute new accuracy
                yPlot[frame] /= (frame + 1) * self.totalPointK 

            #Sort array to get a nice graph
            yPlot.sort()
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                self.fo.write('  ' + str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            
            #Plot the error in the subplot
            if self.name[i] != self.oracleN:                
                plt.plot(self.x[i], yPlot, lw = 1)
            else:
                plt.plot(self.x[i], yPlot, '--', color = 'k', lw = 1)
           
        #Write division into file
        self.fo.write(self.division) 
  
        title(gName + '\nThis graph shows how accuracy changes through frames')
        xlabel('Frame')
        ylabel('Accuracy')
        plt.legend(self.name)
        plt.show()
        
    def showAccuracyConfidence(self):
       
        #Save title in text file and in graphNames array
        gName = 'ACCURACY WITH CONFIDENCE'
        self.fo.write('\n' + gName + '\n')
        
        self.numPlots += 1
        
        #Define a initial figure
        plt.figure(self.numPlots)
        
        #Define a 3-dimensional array that will contain accuracy * Confidence
        accConfidence = zeros((len(self.y) - 1, self.totalFrames, self.totalPointK))
        
        for pred in range(0,len(accConfidence)):
            for frame in range(0,len(accConfidence[0])):
                for pointK in range(0,len(accConfidence[0][0])):
                    if self.y[pred][frame][pointK] < self.tpBound:
                        conf = self.confidence[pred][frame][pointK]
                        accConfidence[pred][frame][pointK] = conf
        
        #Define a 2-dimensional array that contains the average of accConfidence
        #for each frame
        yaccConf = zeros((len(accConfidence), self.totalFrames))
        for pred in range(0,len(yaccConf)):
            
            for frame in range(0,len(yaccConf[0])):
                yaccConf[pred][frame] = sum(accConfidence[pred][frame])
                
                #Add previous accuracy
                yaccConf[pred][frame] += yaccConf[pred][frame - 1] * frame * self.totalPointK
                #Compute new accuracy
                yaccConf[pred][frame] /= (frame + 1) * self.totalPointK
        
        #Go through each predictor
        for i in range(0,len(yaccConf)):
            
            self.fo.write(' ' + self.predLabel + self.name[i])
            
            #Get the error by frame array at position i
            yPlot = yaccConf[i]
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                self.fo.write(' ' + str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            
            #Plot the error 
            if self.name[i] != self.oracleN:
                plt.plot(self.x[i], yPlot, lw = 1)
            else:
                plt.plot(self.x[i], yPlot, '--', color = 'k', lw = 1)
            
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

                count = 0 #Variable that counts the number of errors well computed
                for pointK in range(0, self.totalPointK):

                    err = self.y[pred][frame][pointK]

                    if err >= 0:  
                        self.errorFrame[pred][frame] += err
                        count += 1
                        
                #Divide over the number of errors computed
                if count == 0:
                    self.errorFrame[pred][frame] = -1
                else:
                    self.errorFrame[pred][frame] /= count
        
    def appendOracle(self):
        #This method adds a new 2-dimensional array to y with the smallest error
        #for each frame and point kind. We call this "predictor" Oracle
        
        yOracle = zeros((self.totalFrames, self.totalPointK))
        for i in range(0, self.totalFrames):
            for j in range(0, self.totalPointK):
                
                #Get the minimum error for a frame and a point kind
                yOracle[i][j] = self.minError(i, j)
                
        #Add new name to predictors
        self.name.append(self.oracleN)
        self.totalPredictors += 1
        #Add an extra array in x and errorKindX
        self.x.append(arange(0,self.totalFrames,1))
        self.errorKindX.append(arange(0,self.totalPointK,1) + 1)
        #Add new error matrix for Oracle predictor
        self.y = concatenate((self.y, [yOracle]))
        
    def minError(self, i, j):
        #This method return the minimum error for a frame and a point kind
        
        minVal = self.y[0][i][j]

        for pred in range(1, self.totalPredictors):
            if(self.y[pred][i][j] < minVal):
                minVal = self.y[pred][i][j]

        return minVal
        
    def cutArray(self, array, upperBound):
        '''This method takes an array and every value greater than the upper
        bound is changed to upper bound''' 
        
        for i in range(0,len(array)):
            
            if array[i] > upperBound or array[i] < 0:
                array[i] = upperBound
                
        return array
        
    def showConfidence(self):
        #This method shows a graph with predictor confidence
        
        #For each predictor
        for i in range(0,self.totalPredictors):
        
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
                    zPlot[itr] = self.confidence[i][frame][pointK]
                    itr += 1      
                              
            zPlot = np.array(zPlot).reshape(xPlot.shape)
                    
            ax = fig.gca(projection='3d')
            
            surf = ax.plot_surface(xPlot, yPlot, zPlot, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)

            ax.zaxis.set_major_locator(LinearLocator(10))
            ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

            fig.colorbar(surf, shrink=0.5, aspect=5)
            
            #Messages for plot
            title('Confidence of Predictor: ' + self.name[i])
            xlabel('Frames')
            ylabel('Point Kinds')
            plt.legend(self.name)
            
            plt.show()