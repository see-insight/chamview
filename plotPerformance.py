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
import string

class PlotData:
    
    def __init__(self,directory=''):

        #Attributes
        self.numPlots = 0
        self.file_in = None
        self.directory = directory
        
        #Atribbutes that are obtained from performance class
        self.graphNames = []
        self.division = ''
        #Label variables used to match with text file information
        self.predLabel = ''
        self.pointKLabel = ''
        self.numPredictorsL = ''
        self.numFramesL = ''
        self.numPointKL = ''
        self.infVal = ''
        self.fileArr = [] #Contains the data from text file
        
        #Attributes that are obtained from text file
        self.numPredictors = 0
        self.numFrames = 0
        self.numPointK = 0
        self.upperB = 0
        
        
    def plotSavedG(self):
        
        #Get performance attributes
        self.getPerformanceAtt()
        
        #Get number of predictors, frames, and point kinds
        self.getNumbers(self.directory)
        
        #Get the dataset into an array
        self.readFile(self.directory)
        
        #Plot all the graphs
        self.plot()
        
    def readFile(self, filename):
        
        #If filename does not exist, return
        if os.path.exists(filename) == False:
            print 'FileNotFound'
            return
        
        #Open file and read each line
        input = open(filename)
        fileArr = input.readlines()
        
        #Find the index i for the first graph name and discard the data before it
        for i in range(0, len(fileArr)):
            if fileArr[i] in (self.graphNames):
                break
        self.fileArr = fileArr[i:]
        
    def plot(self):
        
        itr = 0 #Iterator that traverses fileArr
       
        #While loop that checks if there are still data to plot
        while itr < len(self.fileArr):
        
            #Check if current line cotains a graph name or a point kind name
            if self.fileArr[itr] in self.graphNames or self.pointKLabel in self.fileArr[itr]:
            
                self.numPlots += 1
                #Define a new figure
                plt.figure(self.numPlots)
                
                graphTitle = self.fileArr[itr] #Save graph title
                itr += 1
                
                predictors = [] #Define an array that will save predictor names
                
                #Plot a line for each predictor
                while self.predLabel in self.fileArr[itr]:
                    
                    pred = self.getPredictor(self.fileArr[itr]) #Get predictor name
                    predictors.append(pred) #Put it in the array
                    itr += 1
                    
                    #Define xPlot and yPlot
                    xPlot = []
                    yPlot = []

                    while not(self.predLabel in self.fileArr[itr] or self.fileArr[itr] == self.division or self.pointKLabel in self.fileArr[itr]):
                        newX, newY = self.getXY(self.fileArr[itr])
                        xPlot.append(newX)
                        yPlot.append(float(newY))
                        itr += 1  
                        
                    if graphTitle == 'ERROR BY POINT KIND\n':
                        
                        #Plot error with bars if it is by point kinds
                        i = len(predictors) - 1
                        x = arange(self.numPointK)
                        width = 0.2
                        plt.bar(x + width * i, yPlot, width, color=cm.jet(1.*i/len(x)))
                        plt.xticks( x + 0.5,  xPlot)
                        
                    else:
                        
                        #Plot the error in the subplot
                        plt.plot(xPlot,yPlot)
                
                #Choose the correct labels for x and y axis
                if graphTitle == 'ERROR BY POINT KIND\n':
                    
                    title(graphTitle + 'This graph shows errors less or equal than '
                    +str(self.upperB)+' pixels')
                    xlabel('Point Kind')
                    ylabel('Number of Pixels')
                    
                elif graphTitle == 'PERCENTAGE OF ERROR\n':
                    
                    title(graphTitle + '(For a given error from 1 to ' + 
                    str(self.upperB) + ' pixels,\nthe next graph shows the percentage of ' +
                    'points with at most that error)')
                    xlabel('Error in Pixels')
                    ylabel('Percentage of Points')
                    
                elif graphTitle == 'RECEIVER OPERATING CHARACTERISTIC (ROC) CURVE\n':
                    
                    title(graphTitle + 'A predictor is better if its curve is above other')
                    xlabel('False Positive Rate')
                    ylabel('True Positive Rate')
                    
                elif graphTitle == 'ACCURACY IN PREDICTION\n':
                    
                    title(graphTitle)
                    xlabel('Frame')
                    ylabel('Accuracy')
                    
                else:    
                    
                    title(graphTitle + 'This graph shows errors less or equal than '
                    + str(self.upperB) + ' pixels')
                    xlabel('Frame')
                    ylabel('Number of Pixels')
                    
                plt.legend(predictors)
                plt.show()
        
            else:
                itr += 1
               
    def getXY(self, line):
        xy = line.split(',')         
        if xy[1] == self.infVal + '\n':
            xy[1] = self.upperB
        return xy[0], xy[1]
        
    def getPredictor(self, line):
        idx = line.index(self.predLabel) + len(self.predLabel)
        return line[idx:]
        
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
        self.infVal = per.infVal
        
    #Method that plots information from Metadata file
    def plotMeta(self):
        
        #If filename does not exist, return
        if os.path.exists(self.directory) == False: return
        
        #Open file and read each line
        input = open(self.directory)
        metaArr = input.readlines()

        #Obtain each value
        for line in metaArr:
            
            if line.startswith('TOTAL_POINTS'):
                totalPoints = int(line.split()[-1])
            
            elif line.startswith('POINTS_MODIFIED'):
                pointsModified = int(line.split()[-1])
                
            elif line.startswith('MANUAL_POINTS'):
                manualPoints = int(line.split()[-1])
                
            elif line.startswith('TOTAL_FRAMES'):
                totalFrames = int(line.split()[-1])
                
            elif line.startswith('FRAMES_MODIFIED'):
                framesModified = int(line.split()[-1])
                
            if line.startswith('TOTAL_TIME'):
                totalTime = self.getTime(line.split()[-1])
                
            if line.startswith('TIME/POINT'):
                timePerPoint = float(line.split()[-1])
                
            if line.startswith('TIME/FRAME'):
                timePerFrame = float(line.split()[-1])
                
            if line.startswith('PREDICTORS'):
                predictors = self.getPred(line)
        
        #Define an array to save how many accepted points came from each predictor
        #Put initially the manual points
        predictorUse = [['manual', manualPoints]]
        
        #Obtain how many points came from each predictor
        for line in metaArr:
            
            if '_POINTS' in line:

                idx = line.index('_POINTS')
                p = string.lower(line[:idx])
                
                if p in predictors:
                    predictorUse.append([p, int(line.split()[-1])])
        
        #Plot times
        self.plotTimes(totalPoints, pointsModified, totalFrames, framesModified,
                       totalTime, timePerPoint, timePerFrame)
        
        #Plot how many accepted points came from each predictor and manually
        self.plotUsePredictors(predictorUse, pointsModified)
    
    #Plot information given by metadata file
    def plotTimes(self, totalPoints, pointsModified, totalFrames, framesModified,totalTime, timePerPoint, timePerFrame):
        plt.figure()
        title('METADATA INFORMATION', size = 24)
        
        text(0.05, 0.5, 'Total Points: ' + str(totalPoints) + '\n'
              'Points Modified: ' + str(pointsModified) + '\n'
              'Total Frames: ' + str(totalFrames) + '\n'
              'Frames Modified: ' + str(framesModified) + '\n'
              'Total Time: ' + totalTime + '\n'
              'Time Per Point: ' + self.getTime(timePerPoint) + '\n'
              'Time Per Frame: ' + self.getTime(timePerFrame) + '\n',
              verticalalignment = 'center', size = 22)
        show()                            
    
    #This method plots how many time each predictor was used for annotating points
    def plotUsePredictors(self, predictorUse, pointsModified):
        
        plt.figure()
        
        xPlot = []
        yPlot = zeros(len(predictorUse))
        
        for i in range(0, len(predictorUse)):
            yPlot[i] = predictorUse[i][1]
            xPlot.append(predictorUse[i][0] + '\n' + str(int(yPlot[i])))
        
        #Plot error
        x = arange(len(predictorUse))
        bar(x, yPlot)
        xticks( x + 0.4, xPlot )
        title('Use of Predictors\nPoints modified: ' + str(pointsModified))
        show()

    #Method that receives a string and return an array
    def getPred(self, line):
        
        #Get the indexes for array bounds
        first = line.index('[')
        last = line.index(']')
        
        #Check if the list is empty
        if last - first <= 1: return []
        
        List = line[first + 1 : last]
        newList = List.split(',')
        
        for i in range(0, len(newList)):
            
            pred = newList[i] #Get predictor i and remove ' '
            
            f = pred.index("'") #Find first (')
            pred = pred[f+1:]
            
            l = pred.index("'") #Find last (')
            pred = pred[:l]
            
            newList[i] = string.lower(pred)
            
        return newList
            
    #This method receives time in seconds and returns time in hrs, min, sec
    def getTime(self, time):
        
        if isinstance(time, basestring) and ':' in time:
            #Case when time is in HH:MM:SS format
            tSplit = time.split(':')
            return tSplit[0] + ' hrs ' + tSplit[1] + ' min ' + tSplit[2] + ' s'
        else:
            time = int(time * 100) / 100.0
            seconds = time % 60
            totalMinutes = (time - seconds) / 60
            minutes = totalMinutes % 60
            hours = (totalMinutes - minutes) / 60
        
            strTime = ''
            if hours > 0: strTime += str(int(hours)) + ' hrs ' 
            if minutes > 0: strTime += str(int(minutes)) + ' min '
            return strTime + str(seconds) + ' s'
        
        
        