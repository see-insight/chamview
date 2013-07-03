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
    
    def __init__(self,directory='', upBound=50):

        #Attributes
        self.numPlots = 0
        self.file_in = None
        self.directory = directory
        self.outputName = '' #Name of output directory
        self.subdirectories = []
        
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
        self.oracleN = ''
        
        #Attributes that are obtained from text file
        self.numPredictors = 0
        self.numFrames = 0
        self.numPointK = 0
        self.upperB = int(upBound)
        
        
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
            print 'File Not Found in this directory:', filename
            return
        
        #Open file and read each line
        inputFile = open(filename)
        fileArr = inputFile.readlines()
        
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

                        try:
                            xPlot.append(int(newX))
                        except ValueError:
                            xPlot.append(newX)
                            
                        yPlot.append(float(newY))
                        itr += 1                           
                    
                    if graphTitle == 'PERCENTAGE OF POINTS\n':
                        
                        #Only take the important part of the data
                        if self.upperB < len(yPlot):
                            yPlot = yPlot[0:self.upperB]
                            xPlot = xPlot[0:self.upperB]
                        
                        if pred != self.oracleN:
                            plt.plot(xPlot, yPlot)
                            plt.scatter(xPlot, yPlot, s=5)
                        else:
                            plt.plot(xPlot, yPlot, '--', color = 'k')

                    elif graphTitle == 'ERROR BY POINT KIND\n':
                        
                        #Cut yPlot to values less or equal than upper Bound
                        for i in range(0, len(yPlot)):
                            if yPlot[i] > self.upperB: yPlot[i] = self.upperB
                        
                        #Plot error with bars if it is by point kinds
                        i = len(predictors) - 1
                        x = arange(self.numPointK)
                        width = 1.0 / (self.numPredictors + 1.5)
                        
                        if pred != self.oracleN:
                            plt.bar(x + width * i, yPlot, width, color=cm.jet(1.*i/len(x)))
                        else:
                            plt.bar(x + width * i, yPlot, width, color='k')
                        
                        plt.xticks( x + 0.5,  xPlot)
                        
                    else:
                        
                        yPlot.sort() #Sort yPlot to avoid annoying graphs
                        #Cut yPlot to values less or equal than upper Bound
                        for i in range(0, len(yPlot)):
                            if yPlot[i] > self.upperB: yPlot[i] = self.upperB   
                        #Plot the error in the subplot
                        
                        if pred != self.oracleN:
                            plt.plot(xPlot, yPlot)
                        else:
                            plt.plot(xPlot, yPlot, '--', color = 'k')
                                                        
                
                #Choose the correct labels for x and y axis
                if graphTitle == 'ERROR BY POINT KIND\n':
                    
                    title(graphTitle + 'This graph shows errors less or equal than '
                    +str(self.upperB)+' pixels')
                    xlabel('Point Kind')
                    ylabel('Number of Pixels')
                    
                elif graphTitle == 'PERCENTAGE OF POINTS\n':
                    
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
        if (xy[1] == self.infVal + '\n') or (xy[1] == '-1.0\n'):
            xy[1] = self.upperB
        return xy[0], xy[1]
        
    def getPredictor(self, line):
        idx = line.index(self.predLabel) + len(self.predLabel)
        return line[idx:-1]
        
    def getNumbers(self, filename):
        
        #If file does not exists, return
        if os.path.exists(filename) == False: return        
        inputFile = open(filename)
        
        #Define a boolean variables that tell us what values have been obtained        
        pred = fram = pointK = False

        for line in inputFile:
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
            
            if pred and fram and pointK: break
            
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
        self.infVal = per.infVal
        self.oracleN = per.oracleN
        
    #Method that plots information from Metadata file
    def plotMeta(self):
        
        #If filename does not exist, return
        if os.path.exists(self.directory) == False: return
        
        #Open file and read each line
        inputFile = open(self.directory)
        metaArr = inputFile.readlines()

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
                
            elif line.startswith('TOTAL_TIME'):
                totalTime = self.getTime(line.split()[-1])
                
            elif line.startswith('TIME/POINT'):
                timePerPoint = float(line.split()[-1])
                
            elif line.startswith('TIME/FRAME'):
                timePerFrame = float(line.split()[-1])
                
            elif line.startswith('PREDICTORS'):
                predictors = self.getPred(line)
        
        #Plot times
        self.plotTimes(totalPoints, pointsModified, totalFrames, framesModified,
                       totalTime, timePerPoint, timePerFrame)
        
        #Obtain how many points came from each predictor
        predictorUse = self.getUsePredictors(metaArr, predictors, manualPoints)
        
        #Plot how many accepted points came from each predictor and manually
        self.plotUsePredictors(predictorUse, pointsModified)
    
    #Method that obtains the use of the predictors when running chamview
    def getUsePredictors(self, metaArr, predictors, manualPoints):
    
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
        
        return predictorUse
    
    #Plot information given by metadata file
    def plotTimes(self, totalPoints, pointsModified, totalFrames, framesModified,totalTime, timePerPoint, timePerFrame):
        fig = plt.figure()
        ax = fig.add_axes([0., 0., 1., 1.])
        text(.25, .9, 'METADATA INFORMATION', size = 24)
        
        text(0.05, 0.5, 'Total Points: ' + str(totalPoints) + '\n'
              'Points Modified: ' + str(pointsModified) + '\n'
              'Total Frames: ' + str(totalFrames) + '\n'
              'Frames Modified: ' + str(framesModified) + '\n'
              'Total Time: ' + totalTime + '\n'
              'Time Per Point: ' + self.getTime(timePerPoint) + '\n'
              'Time Per Frame: ' + self.getTime(timePerFrame) + '\n',
              verticalalignment = 'center', size = 22)
        ax.set_axis_off()
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
            
            strTime = ''
            if int(tSplit[0]) > 0:
                strTime += tSplit[0] + ' hrs '
            if int(tSplit[1]) > 0:
                strTime += tSplit[1] + ' min '
            if int(tSplit[2]) > 0:
                strTime += tSplit[2] + ' sec '
            
            return strTime
            
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
        
    def compareMetas(self, output):
        '''This method looks for metadata and points files in order to compare evaluations
        between datasets. It takes self.directory and finds all these two files in subdirectories'''
        
        self.outputName = output

        #Get all the subdirectories that contain metadata files
        self.getSubdirectories(self.directory, 'metadata.txt')
        
        #Arrays that saves the information needed to plot for each dataset
        dataInfo = [] #Save use of predictors for each dataset
        names = [] #Save datasets name, e.g. ChamB_LB
        types = [] #Save datasets type, e.g. Chameleon, Wings
        pointsM = [] #Save number of points modified
        timePoint = [] #Saves the average time per point of the analysis
        timeFrame = [] #Saves the average time per frame of the analysis
        
        #Get the information of each metadata file
        for i in range(0, len(self.subdirectories)):
            infoD = self.getInfoDatasets(self.subdirectories[i])
            if infoD != None:
                dataInfo.append(infoD['predictorUse'])
                names.append(infoD['nameDataset'])
                types.append(infoD['typeDataset'])
                pointsM.append(infoD['pointsModified'])
                timePoint.append(infoD['timePoint'])
                timeFrame.append(infoD['timeFrame'])
                
        #WORKING HERE#########################################################################
        #JOIN METADATA IF IMAGE DIRECTORIES ARE EQUAL
        
        numDatasets = len(names)
        
        #Get the maximum set of predictors possible
        numPred = 0
        indexNumPred = -1
        for i in range(0, numDatasets):
            if len(dataInfo[i]) > numPred:
                numPred = len(dataInfo[i])
                indexNumPred = i

        #Get list of predictors
        predictors = []
        for i in range(0, len(dataInfo[indexNumPred])):
            predictors.append(dataInfo[indexNumPred][i][0])
        
        #Define an array that rearrange data info in order to create a graph
        dataInfoG = zeros((numPred, numDatasets))
        for i in range(0, numDatasets):
            for j in range(0, len(dataInfo[i])):
                predName = dataInfo[i][j][0] #Get name of the predictor
                indexPred = predictors.index(predName) #Get the index of predictor
                dataInfoG[indexPred][i] = dataInfo[i][j][1] #Put value in correct position
       
        #Call methods to graph results 
        self.plotByDatasetName(numDatasets, numPred, names, predictors, dataInfoG, pointsM)
        self.plotByDatasetType(numDatasets, numPred, types, predictors, dataInfoG)
 
    def plotByDatasetName(self, numDatasets, numPred, names, predictors, dataInfoG, pointsM):
        
        #Compute percentage of usage
        for i in range(0, numPred):
            for j in range(0, numDatasets):
                dataInfoG[i][j] = dataInfoG[i][j] * 100.0 / pointsM[j]    
        
        #Call method for plot stacked bars
        gName = 'Usage of Predictors'
        self.plotBarsStack(gName, numDatasets, names, numPred, predictors, dataInfoG, 30, 8)
 
    def plotByDatasetType(self, numDatasets, numPred, types, predictors, dataInfoG):
        
        #Get list of types
        typesList = []
        for i in range(0, len(types)):
            if types[i] not in typesList:
                typesList.append(types[i])
                
        numTypes = len(typesList)
        
        #Join data of the same data type
        dataByType = zeros((numPred, numTypes)) #Array that contains usage for each data type
        pointsModType = zeros(numTypes) #Array that contains num points modified for each type
        for i in range(0, numPred):
            for j in range(0, numDatasets):
                
                #Get index type of current data
                idx = typesList.index(types[j])
                
                #Add the usage of predictor i in dataset j
                dataByType[i][idx] += dataInfoG[i][j]
                #Add points modified from dataset j to type idx
                pointsModType[idx] += dataInfoG[i][j]
          
        #Get percentage of usage
        for i in range(0, numPred):
            for j in range(0, numTypes):
                dataByType[i][j] = dataByType[i][j] * 100.0 / pointsModType[j]
        
        #Call method for plot stacked bars
        gName = 'Usage of Predictors by Data Type'
        self.plotBarsStack(gName, numTypes, typesList, numPred, predictors, dataByType, 0, 10)     
        
    def plotBarsStack(self, gName, xLength, names, numPred, predictors, dataInfoG, rot, fontS):
        
        xPlot = np.arange(xLength)    #the x locations for the groups
        width = 0.5                   #width of the bars
        
        #Define a array that will contain the sum of use of predictors for each dataset
        accumulativeUse = zeros(xLength)
        
        #Define plots
        plt.figure(1)
        plots = []
        for i in range(0, numPred):            
            p = plt.bar(xPlot, dataInfoG[i], width, color=cm.jet(1.*i/numPred), bottom=accumulativeUse)
            plots.append(p)
            
            #Add dataInfoF[i] to accumulativeUse array
            for j in range(0, xLength):
                accumulativeUse[j] += dataInfoG[i][j]
        
        plt.ylabel('Percentage for Usage of Predictors')
        plt.xlabel('Data Sets', fontsize = 12)
        plt.title(gName)
        plt.xticks(xPlot + 0.25, names, rotation=rot, fontsize = fontS)
        
        plt.yticks(np.arange(0,100,5))
        plt.legend(predictors, prop = {'size':8})
        
        #Save figure
        if not(self.outputName.endswith('/')): self.outputName += '/'
        figPath = self.outputName + gName + '.jpg'
        plt.savefig(figPath)
        print 'Figure saved to:', figPath
        
        #Show figure
        plt.show()
                
    def getInfoDatasets(self, pathFile):
   
        #Open file and read each line     
        metaFile = open(pathFile)
        metaArr = metaFile.readlines()
        
        #Define a list that will contain all the returned values
        returnInfo = {}
        
        #Define boolean variables to know if info was obtained
        pointsM = manualP = pred = name = timeF = timeP = False
        
        #Obtain each value
        for line in metaArr:
            
            if line.startswith('POINTS_MODIFIED'):
                returnInfo['pointsModified'] = int(line.split()[-1])
                pointsM = True
                
            elif line.startswith('MANUAL_POINTS'):
                manualPoints = int(line.split()[-1])
                manualP = True
                
            elif line.startswith('PREDICTORS'):
                predictors = self.getPred(line)
                pred = True
                
            elif line.startswith('TIME/FRAME'):
                returnInfo['timeFrame'] = float(line.split()[-1])
                timeF = True
                
            elif line.startswith('TIME/POINT'):
                returnInfo['timePoint'] = float(line.split()[-1])
                timeP = True
            
            elif line.startswith('IMAGE_DIRECTORY'):
                
                #Get path to image directory
                lenLabel = len('IMAGE_DIRECTORY: ')
                returnInfo['pathImages'] = line[lenLabel:]
                
                pathSplit = line.split('/')
                
                #Remove no valid directories for pathSplit
                noValid = 0
                while pathSplit[noValid-1] == '' or pathSplit[noValid-1] == '\n':
                    noValid -= 1
                
                returnInfo['nameDataset'] = pathSplit[-2 + noValid] #Get name of dataset
                returnInfo['typeDataset'] = pathSplit[-3 + noValid] #Get dataset type
                name = True
            
        if not(pointsM and manualP and pred and timeF and timeP and name): return None
        
        #Obtain how many points came from each predictor
        returnInfo['predictorUse'] = self.getUsePredictors(metaArr, predictors, manualPoints)
        
        return returnInfo
    
    def getSubdirectories(self, dirData, filename):
        
        #Check if exists metadata in current directory
        metaDir = dirData + '/' + filename
        
        if os.path.isfile(metaDir):

            #Add to array of subdirectories
            self.subdirectories.append(metaDir)
                        
        else:

            #Check subdirectories

            #Get all subdirectories
            subDirs = os.walk(dirData).next()[1]
            
            for sub in subDirs:

                newDirData = dirData + '/' + sub
                
                #Look in the new subdirectory
                self.getSubdirectories(newDirData, filename)
        
        
        