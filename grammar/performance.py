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
import matplotlib.patches as patches

'''This file implements classes where the performance of predictors is computed.
Input: A stack of images, ground truth data, and a set of predictors
Output: An output text file and graphs that show predictors performance
'''

class Performance(Chooser):
    '''It is used to compute the error of predictions and ground-truth points. It
    outpus the difference (in pixels) to file and displays a graph.
    The error is according frames or according kind_point.
    '''
    
    def setup(self):
        '''This method instantiates all class attributes'''
        
        self.x = [] #Frame number
        self.errorKindX = [] #Kind point number
        self.y = [] #Error from ground-truth
        self.errorFrame = [] #Error compute by frame
        self.confidence = [] #Multidimensional array that saves the confidence
        self.outputName = '' #Name of output directory
        self.frameDir = ''
        self.showBool = True #Boolean that determines if show or don't graphs
        
        
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
        self.predLabel = 'Predictor: ' #String that saves the label for predictors in text file
        self.pointKLabel = 'Point Kind: ' #String that saves the label for point kind in text file
        self.numPredictorsL = 'Number_of_Predictors: ' #Label for number of predictors 
        self.predictorsL = 'PREDICTORS: '
        self.numFramesL = 'Number_of_Frames: ' #Label for number of frames
        self.numPointKL = 'Number_of_Point_Kinds: ' #Label for number of point kinds
        self.frameDirL = 'Directory: '
        self.tpBoundL = 'tpBound: '
        self.oracleN = 'Oracle' #Label for Oracle predictor
        
        #Define an array that saves all the graph names
        self.graphNames = ['ERROR_BY_FRAME', 'ERROR_BY_POINT_KIND']
        self.graphNames.append('ERROR_FOR_EACH_POINT_KIND')
        self.graphNames.append('PERCENTAGE_OF_POINTS')
        self.graphNames.append('ACCURACY_IN_PREDICTION')
        self.graphNames.append('RECEIVER_OPERATING CHARACTERISTIC_(ROC)_CURVE')
        
        #Define an array that saves all the arguments for graphs
        self.argGraphs = []
        #Error by frame
        self.argGraphs.append([self.graphNames[0],
            'Average Distance Error by Frame (in Pixels)', 'Errors are up to ', ' pixels',
            'Frame', 'Distance Error in Pixels', ''])
        #Error by point kind
        self.argGraphs.append([self.graphNames[1],
            'Average Distance Error by Point Kind (in Pixels)', 'Errors are up to ', ' pixels',
            'Point Kind', 'Distance Error in Pixels', ''])
        #Error by each point kind
        self.argGraphs.append([self.graphNames[2],
            'Distance Error (in Pixels). Point Kind: ', 'Errors are up to ', ' pixels',
            'Frame', 'Distance Error in Pixels', ''])
        #Percentage of error
        self.argGraphs.append([self.graphNames[3],
            'Percentage of Predicted Points within', 'a Given Radius from the Ground Truth Point', '',
            'Maximum Distance Away from Ground Truth Point (in Pixels)', 'Percentage of Predicted Points', ''])
        #Accuracy
        self.argGraphs.append([self.graphNames[4],
            'Percentage of Predictions', 'Within ', ' Pixels Over Time',
            'Frame', 'Percent',  '', ''])
        
        #Variables used to match with chamview.py requirements
        self.editedPointKinds = False
        self.activePoint = -1
        self.selectedPredictions = []
        self.stagedToSave = ['', '']

    def setupPar(self,argEvaluate):
        '''This method instantiates arguments obtained from evaluatePredictor class and are special
        for this class'''
        
        #Get parameters: Output-upperBound-TruePositiveBound
        parameters = argEvaluate.split('-')
        
        #Update variables
        if parameters[0] != '': self.outputName = parameters[0]
        if parameters[1] != '': self.upperB = int(parameters[1])
        if parameters[2] != '': self.tpBound = int(parameters[2])        
        if parameters[3] == 'False': self.showBool = False
        if parameters[4] != '': self.frameDir = parameters[4]
        
        #Make outputName correct
        if self.outputName != '': self.outputName = self.outputName + '/'

    def teardown(self):
        '''Final called method of this class, it saves an output file and calls methods
        to display all the graphs'''

        #Define Oracle predictor, build it, and append results to other predictors results
        self.appendOracle()

        #Compute the error by frame for each predictor to plot results in
        #different ways
        self.computeErrorByFrame()
        
        #Define path to text file to save results
        outTextFile = self.outputName + 'Performance_Report.txt'
        
        #Open a text file to save results
        self.fo = open(outTextFile,'w')
        self.fo.write('THIS FILE CONTAINS RESULTS OBTAINED OF PREDICTORS EVALUATION\n')
               
        #Save important values in text file
        self.fo.write(self.frameDirL + self.frameDir + '\n')
        self.fo.write(self.numPredictorsL + str(self.totalPredictors) + '\n')
        self.fo.write(self.numFramesL + str(self.totalFrames) + '\n')
        self.fo.write(self.numPointKL + str(self.totalPointK) + '\n')
        self.fo.write(self.predictorsL + str(self.name) + '\n')
        
        #Update the image directories to be displayed on graphs
        for i in range(0, len(self.argGraphs)):
            self.argGraphs[i][6] = self.argGraphs[i][6] + self.frameDir
        
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
        print 'Results saved in ' + outTextFile

    def choose(self,stack,predicted,predictor_name):
        '''This method uses chamview implementation to compute predictions and then measure
        the error of ground truth data and predictions'''
        
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
        '''This method computes the average error by frame and displays a graph'''
                
        #Save title in text file and in graphNames array
        gName = self.graphNames[0]
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
        
        titleLa = self.argGraphs[0][1] + '\n' + self.argGraphs[0][2] + str(self.upperB) +self.argGraphs[0][3]
        
        #Put labels in graph
        self.putLabels(titleLa, self.argGraphs[0][4], self.argGraphs[0][5], self.name, self.upperB) 
        
        #Save figure
        self.saveGraph(gName)
        
        if self.showBool: plt.show()                 
        
    def showErrorByPointKind(self):
        '''This method computes the average error by point kind and displays a bar graph'''
        
        #Save title in text file and in graphNames array
        gName = self.graphNames[1]
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
            width = 1.0 / (self.totalPredictors + 1.5)
            
            if self.name[i] != self.oracleN:
                plt.bar(xPlot + width * i, yPlot, width, color=cm.jet(1.*i/len(xPlot)))
            else:
                plt.bar(xPlot + width * i, yPlot, width, color='k')
                
            plt.xticks( xPlot + 0.5,  self.pointKList)
        
        titleLa = self.argGraphs[1][1] + '\n' + self.argGraphs[1][2] + str(self.upperB) + self.argGraphs[1][3]
        
        #Put labels in graph
        self.putLabels(titleLa, self.argGraphs[1][4], self.argGraphs[1][5], self.name, self.upperB)
        
        #Save figure
        self.saveGraph(gName)
        
        if self.showBool: plt.show()

    def showErrorEachPointK(self):
        '''This method computes the error by frame for each point kind
        and displays a graph for each point kind'''
        
        #Save title in text file and in graphNames array
        gName = self.graphNames[2]
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
            
            titleLa = self.argGraphs[2][1] + self.pointKList[pointK] + '\n' + self.argGraphs[2][2] + str(self.upperB) + self.argGraphs[2][3]

            #Put labels in graph
            self.putLabels(titleLa, self.argGraphs[2][4], self.argGraphs[2][5], self.name, self.upperB)
        
            #Save figure
            self.saveGraph(gName, str(pointK + 1))
        
            if self.showBool: plt.show()
            
    def showPercentageError(self):
        '''This method computes the percentage of points whithin a given interval of error and
        displays a graph'''
        
        #Save title in text file and in graphNames array
        gName = self.graphNames[3]
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
        
        titleLa = self.argGraphs[3][1] + '\n' + self.argGraphs[3][2]
        yLimit = 100
        xlim(0,self.upperB)
        ylim(0, yLimit)
        
        #Put labels in graph
        self.putLabels(titleLa, self.argGraphs[3][4], self.argGraphs[3][5], self.name, yLimit)
        
        #Save figure
        self.saveGraph(gName)
        
        if self.showBool: plt.show()
        
    def showAccuracy(self):
        '''This method computes the accuracy of predictors and display a graph'''
                
        #Save title in text file and in graphNames array
        gName = self.graphNames[4]
        self.fo.write('\n' + gName + '\n')
        self.fo.write(self.tpBoundL + str(self.tpBound) + '\n')
        
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
                
            #Multiply by 100 to get percentage
            yPlot *= 100
            
            #Save data to file
            for j in range(0,self.x[i].shape[0]):
                self.fo.write('  ' + str(self.x[i][j]).zfill(4)+','+str(yPlot[j])+'\n')
            
            #Plot the error in the subplot
            if self.name[i] != self.oracleN:                
                plt.plot(self.x[i], yPlot, lw = 1)
            else:
                plt.plot(self.x[i], yPlot, '--', color = 'k', lw = 1)
        
        titleLa = self.argGraphs[4][1] + '\n' + self.argGraphs[4][2] + str(self.tpBound) + self.argGraphs[4][3]
        yLimit = 100
        ylim(0, yLimit)
        
        #Put labels in graph
        self.putLabels(titleLa, self.argGraphs[4][4], self.argGraphs[4][5], self.name, yLimit)
        
        #Save figure
        self.saveGraph(gName)
        
        if self.showBool: plt.show()
        
    def showAccuracyConfidence(self):
        '''This graph computes the accuracy * confidence of predictors and display a graph
        Now, it is not working because confidence of some predictor is missing'''
       
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

        #Put labels in graph
        self.putLabels(titleLa, 'Frame', 'Accuracy * Confidence', self.name, 100)
        
        #Save figure
        self.saveGraph(gName)
        
        if self.showBool: plt.show()     
    
    def showROC(self):
        '''This method computes true and false positives rate and display an ROC curve'''
   
        #Save title in text file and in graphNames array
        gName = self.graphNames[5]
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
                  
        titleLa = 'Receiver Operating Characteristic (ROC) Curve\nA predictor is better if its curve is above other'

        #Put labels in graph
        self.putLabels(titleLa, 'False Positive Rate', 'True Positive Rate', self.name, 1)
        
        #Save figure
        self.saveGraph(gName)
        
        if self.showBool: plt.show()          
      
    def showError3D(self):
        '''This method display a 3D plot that shows predictors error, where the x and y dimensions
        are frame and point kind'''
        
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
            titleLa = 'Error in Predictor: ' + self.name[i]
 
            #Put labels in graph
            self.putLabels(titleLa, 'Frame', 'Point Kinds', self.name, self.upperB)
            
            #Save figure
            self.saveGraph(gName)
            
            if self.showBool: plt.show() 
                            

    def computeErrorByFrame(self):
        '''This method is used to compute the average error by frame'''
        
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
        '''This method adds a new 2-dimensional array to y with the smallest error
        for each frame and point kind. We call this "predictor" Oracle'''
        
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
        '''This method return the minimum error for a frame and a point kind'''
        
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
        '''This method shows a graph with predictor confidence'''
        
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
            plt.legend(self.name, prop={'size':8}, bbox_to_anchor=(1, 1), loc=2, borderaxespad=0)
        
            #Save figure
            self.saveGraph(gName)
            
            if self.showBool: plt.show()
            
    def saveGraph(self, name, name2 = ''):
        '''This method saves a graph as an image'''
        if self.outputName != '':
            plt.savefig(self.outputName + name + name2 + '.png', bbox_inches='tight')
            #Increase size image: dpi = 600
            
    def putLabels(self, titleLa, xL, yL, leg, yDistance):
        '''This method receives several labels to be placed in the graph'''
        
        plt.title(titleLa, size = 17)
        plt.xlabel(xL, size=15)
        plt.ylabel(yL, size = 15)     
        plt.legend(leg, prop={'size':8}, bbox_to_anchor=(1, 1), loc=2, borderaxespad=0)
        
        plt.text(0, yDistance + yDistance/8, 'Directory: ' + self.frameDir, horizontalalignment='left',
        verticalalignment='bottom', size = 8)