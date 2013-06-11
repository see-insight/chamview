#This class takes a text file and graphs errors on predictors
#Manuel E. Dosal
#June 10, 2013

import os
import vocabulary as vocab
from pylab import *
import matplotlib.pyplot as plt
from decimal import *
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np

class PlotData:
    
    def __init__(self,directory=''):

        #Attributes
        self.numPlots = 0
        self.file_in = None
        
        #Atribbutes that are obtained from performance class
        self.graphNames = []
        self.division = ''
        self.endDocument = ''
        self.predLabel = ''
        self.pointKLabel = ''
        self.numPredictorsL = ''
        self.numFramesL = ''
        self.numPointKL = ''
        self.fileArr = [] #Contains information about 
        
        #Attributes that are obtained from text file
        self.numPredictors = 0
        self.numFrames = 0
        self.numPointK = 0
        self.upperB = 0
        
        #Get performance attributes
        self.getPerformanceAtt()
        
        #Get number of predictros, frames, and point kinds
        self.getNumbers(directory)
        
        #Get the dataset into an array
        self.readFile(directory)
        
        #Debugging purposes-----------------------------------------------------
        print 'self.numPredictors', self.numPredictors
        print 'self.numFrames', self.numFrames
        print 'self.numPointK', self.numPointK
        print 'self.upperB', self.upperB
        #print 'self.fileArr', self.fileArr
        #-----------------------------------------------------------------------
        
        #Plot all the graphs
        self.plot()
        
    def readFile(self, filename):
        
        #If filename does not exist, return
        if os.path.exists(filename) == False: return
        
        input = open(filename)
        fileArr = input.readlines()
        
        for i in range(0, len(fileArr)):
            if fileArr[i] in (self.graphNames):
                break
        self.fileArr = fileArr[i:]
        
    def plot(self):
        
        itr = 0 #Iterator that traverses fileArr
       
        #While loop that checks if there are still data to plot
        while itr < len(self.fileArr):
        
            if self.fileArr[itr] in self.graphNames or self.pointKLabel in self.fileArr[itr]:
            
                self.numPlots += 1
                #Define a initial figure
                plt.figure(self.numPlots)
                
                graphTitle = self.fileArr[itr] #Save graph title
                itr += 1
                
                predictors = [] #Define an array that will save predictor names
                
                #Plot a line for each predictor
                while self.predLabel in self.fileArr[itr]:
                    
                    pred = self.getPredictor(self.fileArr[itr]) #Get predictor name
                    predictors.append(pred) #Put in the array
                    itr += 1
                    
                    #Define xPlot and yPlot
                    xPlot = []
                    yPlot = []

                    while not(self.predLabel in self.fileArr[itr] or self.fileArr[itr] == self.division or self.pointKLabel in self.fileArr[itr]):
                        newX, newY = self.getXY(self.fileArr[itr])
                        xPlot.append(newX)
                        yPlot.append(newY)
                        itr += 1
                        
                    #Debugging purposes-----------------------------------------
                    #print 'xPlot: ', xPlot
                    #print 'yPlot: ', yPlot
                    #-----------------------------------------------------------   
                        
                    if graphTitle == 'ERROR BY POINT KIND\n':
                        #Plot error with bars if it is by point kinds
                        i = len(predictors) - 1
                        x = arange(self.numPointK)
                        width = 0.35
                        plt.bar(x + width * i, yPlot, width, color=cm.jet(1.*i/len(x)))
                        plt.xticks( x + 0.5,  xPlot)
                    else:
                        #Plot the error in the subplot
                        plt.plot(xPlot,yPlot)
                
                #Debugging purposes---------------------------------------------
                print 'predictors: ', predictors
                #--------------------------------------------------------------- 
                
                title(graphTitle)
                
                if graphTitle == 'ERROR BY POINT KIND\n':
                    xlabel('Point Kind')
                    ylabel('Number of Pixels')
                elif graphTitle == 'PERCENTAGE OF ERROR\n':
                    xlabel('Error in Pixels')
                    ylabel('Percentage of Points')
                elif graphTitle == 'RECEIVER OPERATING CHARACTERISTIC (ROC) CURVE\n':
                    xlabel('False Positive Rate')
                    ylabel('True Positive Rate')
                elif graphTitle == 'ACCURACY IN PREDICTION\n':
                    xlabel('Frame')
                    ylabel('Accuracy')
                else:    
                    xlabel('Frame')
                    ylabel('Number of Pixels')
                    
                plt.legend(predictors)
                plt.show()
        
            else:
                itr += 1
               
    def getXY(self, line):
        xy = line.split(',')         
        if xy[1] == 'INF\n':
            xy[1] = self.upperB
        return xy[0], xy[1]
        
    def getPredictor(self, line):
        p = line.split()
        return p[len(p) - 1]
            
        
    def plotGraph(self,graphName):     
                    
        #If the next graph is for each point kind, we need a graph for each one
        #Then do it recursively with each point kind
        if graphName == 'ERROR FOR EACH POINT KIND':
            newGName = self.file_in.read()
            self.plotGraph(newGName)
        
        for pred in range(0, self.numPredictors):

            predictor, xPlot, yPlot = self.getLine()            
    
    def getLine(self):
        
        predictor = self.file_in.read()
        arr = predictor.split() 
        predictor = ''.join(arr[1:])
            
        print 'predictor--', predictor
        
    def getNumbers(self, filename):
        
        #If file does not exists, return
        if os.path.exists(filename) == False: return        
        input = open(filename)
        
        #Define a boolean variables that tell us what values have been obtained        
        pred = fram = pointK = uB = False

        for line in input:
            #Get number of predictors, frames, and point kinds
            if line.startswith(self.numPredictorsL):
                arr = line.split()
                self.numPredictors = int(arr[len(arr)-1])
                pred = True
            if line.startswith(self.numFramesL):
                arr = line.split()
                self.numFrames = int(arr[len(arr)-1])
                fram = True
            if line.startswith(self.numPointKL):
                arr = line.split()
                self.numPointK = int(arr[len(arr)-1])
                pointK = True
            if line.startswith(self.upperBoundL):
                arr = line.split()
                self.upperB = int(arr[len(arr)-1])
                uB = True
            
            if pred and fram and pointK and uB: break
            
    
    def getPerformanceAtt(self):
        #Create a new performance object
        per = vocab.getChooser('Performance')
        per.setup()
        
        #Update global variables
        self.graphNames = per.graphNames
        self.division = per.division
        self.predLabel = per.predLabel
        self.pointKLabel = per.pointKLabel
        self.numPredictorsL = per.numPredictorsL
        self.numFramesL = per.numFramesL
        self.numPointKL = per.numPointKL
        self.upperBoundL = per.upperBoundL
        self.endDocument = per.endDocument