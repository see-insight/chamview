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
        self.showBool = True; ##Boolean that determines if show or don't graphs
        self.subdirectories = []
        
        #Atribbutes that are obtained from performance class
        self.graphNames = []
        self.argGraphs = []
        self.division = ''
        #Label variables used to match with text file information
        self.predLabel = ''
        self.predictorsL = ''
        self.pointKLabel = ''
        self.numPredictorsL = ''
        self.numFramesL = ''
        self.numPointKL = ''
        self.infVal = ''
        self.fileArr = [] #Contains the data from text file
        self.oracleN = ''
        
        #Attributes that are obtained from text file
        self.numPredictors = 0
        self.predList = []
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
        self.plotAll()
        
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
            if fileArr[i][0:-1] in (self.graphNames):
                break
        self.fileArr = fileArr[i:]
        
    def plotAll(self):
        
        itr = 0 #Iterator that traverses fileArr
       
        #While loop that checks if there are still data to plot
        while itr < len(self.fileArr):
        
            #Check if current line cotains a graph name
            if self.fileArr[itr][0:-1] in self.graphNames:
            
                graphTitle = self.fileArr[itr]
                itr += 1
                
                if graphTitle == self.graphNames[0]:
                    #ERROR BY FRAME Case
                    
                    #Get data arrays to plot
                    itr, xPlot, yPlot = self.getInfoErrorByFrame(itr)
                    
                    #Get arguments for graph
                    titleG = self.argGraphs[0][1] + '\n' + self.argGraphs[0][2] + str(self.upperB) + self.argGraphs[0][3]
                    xLabel = self.argGraphs[0][4]
                    yLabel = self.argGraphs[0][5]
                    
                    #Call method to plot graph
                    self.plotLine(xPlot, yPlot, titleG, xLabel, yLabel)
                    
                elif graphTitle == self.graphNames[1]:
                    #ERROR BY POINT KIND
                    
                    #Get data arrays
                    itr, xPlot, yPlot = self.getInfoErrorByPointK(itr)
                    
                    #Get arguments for graph
                    titleG = self.argGraphs[1][1] + '\n' + self.argGraphs[1][2] + str(self.upperB) + self.argGraphs[1][3]
                    xLabel = self.argGraphs[1][4]
                    yLabel = self.argGraphs[1][5]
                    
                    #Call method to plot
                    self.plotConsecutiveBars(xPlot, yPlot, titleG, xLabel, yLabel, self.predList, 0)

                elif graphTitle == self.graphNames[2]:
                    #ERROR FOR EACH POINT KIND
                    
                    for i in range(0, self.numPointK):
                            
                        #Get name of pointK
                        pointK = self.fileArr[itr].split(':')[-1]
                        itr += 1
                            
                        #Get data arrays
                        itr, xPlot, yPlot = self.getInfoErrorByFrame(itr)
                        
                        #Get arguments for graph
                        titleG = self.argGraphs[2][1] + pointK + self.argGraphs[2][2] + str(self.upperB) + self.argGraphs[2][3]
                        xLabel = self.argGraphs[2][4]
                        yLabel = self.argGraphs[2][5]
                        
                        #Call method to plot graph
                        self.plotLine(xPlot, yPlot, titleG, xLabel, yLabel)
                        
                elif graphTitle == self.graphNames[3]:
                    #PERCENTAGE OF POINTS
                    
                    #Get data arrays to plot
                    itr, xPlot, yPlot = self.getInfoPercentagePoints(itr)
                    
                    #Get arguments for graphs
                    titleG = self.argGraphs[3][1] + str(self.upperB) + self.argGraphs[3][2] + '\n' + self.argGraphs[3][3]
                    xLabel = self.argGraphs[3][4]
                    yLabel = self.argGraphs[3][5]
                    
                    #Call method to plot graph
                    self.plotLine(xPlot, yPlot, titleG, xLabel, yLabel, 5)
                    
                elif graphTitle == self.graphNames[4]:
                    #ACCURACY
                    
                    #Get data arrays to plot
                    itr, xPlot, yPlot = self.getInfoErrorByFrame(itr)
                    
                    #Get arguments for graphs
                    titleG = self.argGraphs[4][1] + '\n' +self.argGraphs[4][2]
                    xLabel = self.argGraphs[4][3]
                    yLabel = self.argGraphs[4][4]
                    
                    #Call method to plot graph
                    self.plotLine(xPlot, yPlot, titleG, xLabel, yLabel)
                    
                elif graphTitle == self.graphNames[5]:
                    
                    #title = graphTitle + 'A predictor is better if its curve is above other'
                    #xlabel = 'False Positive Rate'
                    #ylabel = 'True Positive Rate'
                    
                    #Method not implemented because right now ROC is not important at the moment
                    pass
                    
                else:
                    
                    print 'Graph Name was not found'
            else:
                itr += 1
        
    def getInfoErrorByFrame(self, itr):
        
        #Define two lists to save numbers to plot
        xPlot = zeros((self.numPredictors, self.numFrames))
        yPlot = zeros((self.numPredictors, self.numFrames))
        
        for i in range(0, self.numPredictors):
            
            itr += 1 #Discard predictor name
            for j in range(0, self.numFrames):
                xPlot[i][j], yPlot[i][j] = self.getXY(self.fileArr[itr])
                itr += 1
                
            yPlot[i].sort() #Sort yPlot to avoid annoying graphs
            
            #Cut yPlot to values less or equal than upper Bound
            for j in range(0, self.numFrames):
                if yPlot[i][j] > self.upperB: yPlot[i][j] = self.upperB
            
        return itr, xPlot, yPlot
        
    def getInfoErrorByPointK(self, itr):
        
        #Define two lists to save data
        xPlot = []
        yPlot = zeros((self.numPredictors, self.numPointK))
        
        for i in range(0, self.numPredictors):
            
            itr +=1 #Discard predictor name
            
            for j in range(0, self.numPointK):
                newX, yPlot[i][j] = self.getXY(self.fileArr[itr])
                if i == 0: xPlot.append(newX)
                if yPlot[i][j] > self.upperB: yPlot[i][j] = self.upperB
                itr += 1
                
        return itr, xPlot, yPlot
        
    def getInfoPercentagePoints(self, itr):
        
        #Define two lists to save the data
        xPlot = []
        yPlot = []
        
        for i in range(0, self.numPredictors):
            
            xPlot.append([])
            yPlot.append([])            
            
            itr += 1 #Discard predictor name
            
            while not(self.fileArr[itr].startswith(self.predLabel)) and ',' in self.fileArr[itr]:
                newX, newY = self.getXY(self.fileArr[itr])
                xPlot[i].append(int(newX))
                yPlot[i].append(float(newY))
                itr += 1
        
            #Only take the important part of the data
            if self.upperB < len(yPlot[i]):
                yPlot[i] = yPlot[i][0:self.upperB]
                xPlot[i] = xPlot[i][0:self.upperB]     
                     
        return itr, xPlot, yPlot
        
    
    def plotLine(self, xPlot, yPlot, titleG, xLabel, yLabel, scatt = 0):
        
        self.numPlots += 1
        #Define a new figure
        plt.figure(self.numPlots)
        
        for i in range(0, len(self.predList)): 
            if self.predList[i] != self.oracleN:
                plt.plot(xPlot[i], yPlot[i])
                #if scatt != 0: plt.scatter(xPlot[i], yPlot[i], s=scatt)
            else:
                plt.plot(xPlot[i], yPlot[i], '--', color = 'k')
                
        plt.title(titleG)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
                  
        plt.legend(self.predList)
        plt.show()
               
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
        pred = fram = pointK = predL = False

        for line in inputFile:
            #Get number of predictors, frames, and point kinds
            if line.startswith(self.numPredictorsL):
                arr = line.split()
                self.numPredictors = int(arr[-1])
                pred = True
            if line.startswith(self.numFramesL):
                arr = line.split()
                self.numFrames = int(arr[-1])
                fram = True
            if line.startswith(self.numPointKL):
                arr = line.split()
                self.numPointK = int(arr[-1])
                pointK = True
            if line.startswith(self.predictorsL):
                self.predList = self.getPred(line, False)
                predL = True
                
            
            if pred and fram and pointK and predL: break
            
    def getPerformanceAtt(self):
        #Create a new performance object
        per = vocab.getChooser('Performance')
        per.setup()
        
        #Update global variables
        self.graphNames = per.graphNames
        self.argGraphs = per.argGraphs
        self.division = per.division
        self.predLabel = per.predLabel
        self.pointKLabel = per.pointKLabel
        self.numPredictorsL = per.numPredictorsL
        self.numFramesL = per.numFramesL
        self.numPointKL = per.numPointKL
        self.infVal = per.infVal
        self.oracleN = per.oracleN
        self.predictorsL = per.predictorsL
        
    #Method that plots information from Metadata file
    def plotMeta(self, output, argShow):
        
        #If filename does not exist, return
        if os.path.exists(self.directory) == False: return
        
        #Get the path where graphs will be saved
        self.outputName = output
        if output != '' and not(output.endswith('/')): self.outputName += '/'
        
        #Get boolean variable for show
        self.showBool = argShow
        
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
                predictors = self.getPred(line, True)
        
        #Plot times
        self.plotTimes(totalPoints, pointsModified, totalFrames, framesModified,
                       totalTime, timePerPoint, timePerFrame)
        
        #Obtain how many points came from each predictor
        predictorUse = self.getUsePredictors(metaArr, predictors, manualPoints)
        
        #Plot how many accepted points came from each predictor and manually
        self.plotUsePredictors(predictorUse, pointsModified)
    
    def getUsePredictors(self, metaArr, predictors, manualPoints):
        #Method that obtains the use of the predictors when running chamview
    
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
        gName = 'METADATA INFORMATION'
        text(.25, .9, gName, size = 24)
        
        text(0.05, 0.5, 'Total Points: ' + str(totalPoints) + '\n'
              'Points Modified: ' + str(pointsModified) + '\n'
              'Total Frames: ' + str(totalFrames) + '\n'
              'Frames Modified: ' + str(framesModified) + '\n'
              'Total Time: ' + totalTime + '\n'
              'Time Per Point: ' + self.getTime(timePerPoint) + '\n'
              'Time Per Frame: ' + self.getTime(timePerFrame) + '\n',
              verticalalignment = 'center', size = 22)
        ax.set_axis_off()
        
        #Save figure if output file is given
        if self.outputName != '':
            figPath = self.outputName + gName + '.jpg'
            savefig(figPath)
            print 'Graph saved in', figPath
        
        #Show graphs if user wants
        if self.showBool: show()                            
    
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
        gName = 'Use of Predictors'
        title(gName + '\nPoints modified: ' + str(pointsModified))
        
        #Save figure if output file is given
        if self.outputName != '':
            figPath = self.outputName + gName + '.jpg'
            savefig(figPath)
            print 'Graph saved in', figPath
        
        #Show graph only if user wants
        if self.showBool: show()

    #Method that receives a string and return an array
    def getPred(self, line, lowerC):
        
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
            
            #Make lowerC if needed
            if lowerC:
                newList[i] = string.lower(pred)
            else:
                newList[i] = pred
            
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
        
    def compareMetas(self, output, argShow):
        '''This method looks for metadata and points files in order to compare evaluations
        between datasets. It takes self.directory and finds all these two files in subdirectories'''
        
        self.outputName = output
        if output != '' and not(output.endswith('/')): self.outputName += '/'
        
        self.showBool = argShow

        #Get all the subdirectories that contain metadata files
        self.getSubdirectories(self.directory, 'metadata.txt')
        
        #Arrays that saves the information needed to plot for each dataset
        dataInfo = [] #Saves use of predictors for each dataset
        addInfo = [] #Saves additional information used to plot
        
 
        #Add arrays that will contain important information of the dataset       
        for i in range(0, 7): addInfo.append([])
        
        #Get the information of each metadata file
        for i in range(0, len(self.subdirectories)):
            infoD = self.getInfoDatasets(self.subdirectories[i])
            if infoD != None:
                dataInfo.append(infoD['predictorUse'])
                addInfo[0].append(infoD['nameDataset'])
                addInfo[1].append(infoD['typeDataset'])
                addInfo[2].append(infoD['pointsModified'])
                addInfo[3].append(infoD['timePoint'])
                addInfo[4].append(infoD['timeFrame'])
                addInfo[5].append(infoD['predUsed'])                       
                addInfo[6].append(infoD['theoTime'])
        
        numDatasets = len(addInfo[0])
        
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
       
        #Create arrays for dataInfo and addInfo only for datasets that used predictors
        #This is for graphs that show how often predictors are used
        predDataInfoG, predAddInfo = self.getPredDataset(dataInfoG, addInfo)
        #Remove repeated data and take averages if repetitions
        predDataInfoG, predAddInfo = self.removeRepeatedData(predDataInfoG, predAddInfo)
        predNumDatasets = len(predDataInfoG[0])
        
        
        #Split datasets into three sets: no-predictors, predictors, theoretical-time
        #This is to compare the times for these three type of analysis of chamview
        pDataInfoG, pAddInfo, npDataInfoG, npAddInfo, ttDataInfoG, ttAddInfo = self.splitDatasets(dataInfoG, addInfo)
        #If one dataset has more than one metadata file, then take average of times and usage
        pDataInfoG, pAddInfo,  = self.removeRepeatedData(pDataInfoG, pAddInfo)
        npDataInfoG, npAddInfo = self.removeRepeatedData(npDataInfoG, npAddInfo)
        ttDataInfoG, ttAddInfo = self.removeRepeatedData(ttDataInfoG, ttAddInfo)
        
        #Call methods to graph results
        
        #Call methods to plot the use of predictors, only use pDataInfoG and pAddInfo
        self.plotByDatasetName(predNumDatasets, numPred, predAddInfo[0], predictors, predDataInfoG, predAddInfo[2])
        self.plotByDatasetType(predNumDatasets, numPred, predAddInfo[1], predictors, predDataInfoG)
        
        #Call methods to plot comparison between using predictors and not using them
        self.plotCompPredName(pAddInfo, npAddInfo, ttAddInfo, True)
        self.plotCompPredType(pAddInfo, npAddInfo, ttAddInfo)
        
    def plotCompPredType(self,predInfo, noPredInfo, ttInfo):

        #Define an array that will contain all the dataset types from pred, noPred, or theoTime
        typesD = []
        numRepPred = [] #Saves the number of repetitions for a dataset type and for predInfo
        numRepNoPred = [] #Saves the number of repetitions for a dataset type and for noPredInfo
        numRepTheoTime = [] #Saves the number of repetitions for a dataset type and for theoTime
        #Fill up typesD
        for i in range(0, len(predInfo[0])):
            if predInfo[1][i] not in typesD:
                typesD.append(predInfo[1][i])
                numRepPred.append(1)
                numRepNoPred.append(0)
                numRepTheoTime.append(0)
            else:
                idx = typesD.index(predInfo[1][i])
                numRepPred[idx] += 1
        for i in range(0, len(noPredInfo[0])):
            if noPredInfo[1][i] not in typesD:
                typesD.append(noPredInfo[1][i])
                numRepPred.append(0)
                numRepNoPred.append(1)
                numRepTheoTime.append(0)
            else:
                idx = typesD.index(noPredInfo[1][i])
                numRepNoPred[idx] += 1
        for i in range(0, len(ttInfo[0])):
            if ttInfo[1][i] not in typesD:
                typesD.append(ttInfo[1][i])
                numRepPred.append(0)
                numRepNoPred.append(0)
                numRepTheoTime.append(1)
            else:
                idx = typesD.index(ttInfo[1][i])
                numRepTheoTime[idx] += 1
                
        #Define two arrays to save timePoint and timeFrame
        #Index 0 is for pred, 1 i for noPred, 2 is for theoTime
        timePoint = zeros((3, len(typesD)))
        timeFrame = zeros((3, len(typesD)))
        #Fill up these arrays
        for i in range(0, len(predInfo[0])):
            idx = typesD.index(predInfo[1][i])
            timePoint[0][idx] += predInfo[3][i] / numRepPred[idx]
            timeFrame[0][idx] += predInfo[4][i] / numRepPred[idx]
        for i in range(0, len(noPredInfo[0])):
            idx = typesD.index(noPredInfo[1][i])
            timePoint[1][idx] += noPredInfo[3][i] / numRepNoPred[idx]
            timeFrame[1][idx] += noPredInfo[4][i] / numRepNoPred[idx]
        for i in range(0, len(ttInfo[0])):
            idx = typesD.index(ttInfo[1][i])
            timePoint[2][idx] += ttInfo[3][i] / numRepTheoTime[idx]
            timeFrame[2][idx] += ttInfo[4][i] / numRepTheoTime[idx]
        
        legend = ['Predictors', 'No Predictors', 'Theoretical Time']
        gName1 = 'Average Time per Point for Dataset Type'
        self.plotConsecutiveBars(typesD, timePoint, gName1, 'Dataset Type', 'Time in seconds', legend, 0)
        gName2 = 'Average Time per Frame for Dataset Type'
        self.plotConsecutiveBars(typesD, timeFrame, gName2, 'Dataset Type', 'Time in seconds', legend, 0)
              
    def plotCompPredName(self,predInfo, noPredInfo, ttInfo, complete):
        
        #Define an array that will contain all the datasets from pred, noPred, and theoTime
        namesD = []
        
        #Check if caller wants to graph only complete dataset, that means, datasets that contains
        #information for pred, noPred, and theoTime
        if complete:
            
            #Add only complete datasets
            for i in range(0, len(predInfo[0])):
                if predInfo[0][i] in noPredInfo[0] and predInfo[0][i] in ttInfo[0]:
                    namesD.append(predInfo[0][i])
                    
            #Define two arrays to save timePoint and timeFrame
            #Index 0 is for pred, 1 is for noPred, 2 is for theoTime
            timePoint = zeros((3, len(namesD)))
            timeFrame = zeros((3, len(namesD)))
            #Fill up arrays
            for i in range(0, len(namesD)):
                
                idx = predInfo[0].index(namesD[i])
                timePoint[0][i] = predInfo[3][idx]
                timeFrame[0][i] = predInfo[4][idx]
                
                idx = noPredInfo[0].index(namesD[i])
                timePoint[1][i] = noPredInfo[3][idx]
                timeFrame[1][i] = noPredInfo[4][idx]
                
                idx = ttInfo[0].index(namesD[i])
                timePoint[2][i] = ttInfo[3][idx]
                timeFrame[2][i] = ttInfo[4][idx]
                
            
        else:
        
            #Fill up namesD to graph all information even if it is not complete
            for i in range(0, len(predInfo[0])):
                if predInfo[0][i] not in namesD:
                    namesD.append(predInfo[0][i])
            for i in range(0, len(noPredInfo[0])):
                if noPredInfo[0][i] not in namesD:
                    namesD.append(noPredInfo[0][i])
            for i in range(0, len(ttInfo[0])):
                if ttInfo[0][i] not in namesD:
                    namesD.append(ttInfo[0][i])
        
            #Define two arrays to save timePoint and timeFrame
            #Index 0 is for pred, 1 is for noPred, 2 is for theoTime
            timePoint = zeros((3, len(namesD)))
            timeFrame = zeros((3, len(namesD)))
            #Fill up these arrays
            for i in range(0, len(predInfo[0])):
                idx = namesD.index(predInfo[0][i])
                timePoint[0][idx] = predInfo[3][i]
                timeFrame[0][idx] = predInfo[4][i]
            for i in range(0, len(noPredInfo[0])):
                idx = namesD.index(noPredInfo[0][i])    
                timePoint[1][idx] = noPredInfo[3][i]
                timeFrame[1][idx] = noPredInfo[4][i]
            for i in range(0, len(ttInfo[0])):
                idx = namesD.index(ttInfo[0][i])    
                timePoint[2][idx] = ttInfo[3][i]
                timeFrame[2][idx] = ttInfo[4][i] 
                
        legend = ['Predictors', 'No Predictors', 'Theoretical Time']
        gName1 = 'Average Time per Point for Each Dataset'
        self.plotConsecutiveBars(namesD, timePoint, gName1, 'Dataset', 'Time in seconds', legend, 30)
        gName2 = 'Average Time per Frame for Each Dataset'
        self.plotConsecutiveBars(namesD, timeFrame, gName2, 'Dataset', 'Time in seconds', legend, 30)
        
    def plotConsecutiveBars(self, xLabels, yPlots, gName, xl, yl, leg, rot):
        '''This method makes a graph with consecutive bars for each single x value'''
        
        xPlot = arange(len(xLabels)) #Array for x axis
        
        col = ['b', 'r', 'g', 'k']
        
        for i in range(0, len(yPlots)):
            
            width = 1.0 / (len(yPlots) + 1.5)
            plt.bar(xPlot + width * i, yPlots[i], width, color=col[i%len(col)])            
            plt.xticks( xPlot  + 0.25,  xLabels, rotation=rot)
            
        plt.title(gName)
        xlabel(xl)
        ylabel(yl)
        plt.legend(leg, prop = {'size':10})
        
        #Save figure
        if self.outputName != '':
            figPath = self.outputName + gName + '.jpg'
            plt.savefig(figPath)
            print 'Figure saved to:', figPath
        
        #Show figure
        if self.showBool: plt.show()                 
 
    def removeRepeatedData(self, dataInfo, addInfo):
        
        #addInfo[0] has the dataset name
        #Define a new array that has all the names but without repetition
        names = []
        numRepetitions = []
        for i in range(0, len(addInfo[0])):
            if addInfo[0][i] not in names:
                names.append(addInfo[0][i])
                numRepetitions.append(1)
            else:
                idx = names.index(addInfo[0][i])
                numRepetitions[idx] += 1
      
        #Define new arrays for dataInfo
        newDataInfo = zeros((len(dataInfo), len(names)))
        #Fill up dataInfo
        for i in range(0, len(dataInfo[0])):
            idx = names.index(addInfo[0][i])
            for j in range(0, len(dataInfo)):
                newDataInfo[j][idx] += dataInfo[j][i]
        
        
        #Define new arrays for addInfo
        newAddInfo = []
        newAddInfo.append(names) #Add dataset names list

        newAddInfo.append([]) #Add dataset types array
        #Fill up types array
        for i in range(0, len(names)):
            idx = addInfo[0].index(names[i])
            typeDataset = addInfo[1][idx]
            newAddInfo[1].append(typeDataset)
            
        #Add pointsModified, timePoint, timeFrame, predUsed
        for i in range(0, 4): newAddInfo.append(zeros(len(names)))
        #Fill up remaining arrays
        for i in range(0, len(addInfo[0])):
            idx = names.index(addInfo[0][i])
            for j in range(2, 5):
                newAddInfo[j][idx] += addInfo[j][i]
            if addInfo[5][i] > newAddInfo[5][idx]:
                newAddInfo[5][idx] = addInfo[5][i]
                
        #Take average for timePoint, timeFrame
        for i in range(0, len(newAddInfo[0])):
            newAddInfo[3][i] /= numRepetitions[i]
            newAddInfo[4][i] /= numRepetitions[i]
            
        newAddInfo.append([]) #Add theoTime array
        #Fill up theoTime array
        for i in range(0, len(names)):
            idx = addInfo[0].index(names[i])
            theoTime = addInfo[6][idx]
            newAddInfo[6].append(theoTime)
       
        return newDataInfo, newAddInfo
        
        

    def splitDatasets(self, dataInfoG, addInfo):
        
        #Define a new array where analysis with predictors information will be saved
        pDIG = []
        for i in range(0, len(dataInfoG)): pDIG.append([])
        pAI = []
        for i in range(0, len(addInfo)): pAI.append([])
        #Define a new array where analysis with no predictors information will be saved
        noPDIG = []
        for i in range(0, len(dataInfoG)): noPDIG.append([])
        noPAI = []
        for i in range(0, len(addInfo)): noPAI.append([])
        #Define a new array where analysis with predictors and theoretical time will be saved
        ttDIG = []
        for i in range(0, len(dataInfoG)): ttDIG.append([])
        ttAI = []
        for i in range(0, len(addInfo)): ttAI.append([])
        
        #Find datasets that didn't use any predictor for the analysis
        for dataset in range(0, len(addInfo[0])):
            
            if addInfo[5][dataset] == 0:

                #Add information to noPDIG and noPAI
                for i in range(0, len(dataInfoG)):
                    noPDIG[i].append(dataInfoG[i][dataset])
                for i in range(0, len(addInfo)):
                    noPAI[i].append(addInfo[i][dataset])
            
            elif addInfo[6][dataset] == True:
                
                #Add information to ttDIG and ttAI
                for i in range(0, len(dataInfoG)):
                    ttDIG[i].append(dataInfoG[i][dataset])
                for i in range(0, len(addInfo)):
                    ttAI[i].append(addInfo[i][dataset])
                    
            else:
                
                #Add information to pDIG and pAI
                for i in range(0, len(dataInfoG)):
                    pDIG[i].append(dataInfoG[i][dataset])
                for i in range(0, len(addInfo)):
                    pAI[i].append(addInfo[i][dataset])
        
        return pDIG, pAI, noPDIG, noPAI, ttDIG, ttAI
        
    def getPredDataset(self, dataInfoG, addInfo):
        
        #Define a new array where analysis with predictors information will be saved
        pDIG = []
        for i in range(0, len(dataInfoG)): pDIG.append([])
        pAI = []
        for i in range(0, len(addInfo)): pAI.append([])
        
        #Find datasets that use predictors for the analysis
        for dataset in range(0, len(addInfo[0])):
            
            if addInfo[5][dataset] != 0:
                
                #Add information to pDIG and pAI
                for i in range(0, len(dataInfoG)):
                    pDIG[i].append(dataInfoG[i][dataset])
                for i in range(0, len(addInfo)):
                    pAI[i].append(addInfo[i][dataset])
                    
        return pDIG, pAI
        
 
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
        plt.legend(predictors, prop = {'size':10})
        
        #Save figure
        if self.outputName != '':
            figPath = self.outputName + gName + '.jpg'
            plt.savefig(figPath)
            print 'Figure saved to:', figPath
        
        #Show figure
        if self.showBool: plt.show()
                
    def getInfoDatasets(self, pathFile):
   
        #Open file and read each line     
        metaFile = open(pathFile)
        metaArr = metaFile.readlines()
        
        #Define a list that will contain all the returned values
        returnInfo = {}
        
        #Define boolean variables to know if info was obtained
        pointsM = manualP = pred = name = timeF = timeP = theoTime = False
        
        #Obtain each value
        for line in metaArr:
            
            if line.startswith('POINTS_MODIFIED'):
                returnInfo['pointsModified'] = int(line.split()[-1])
                pointsM = True
                
            elif line.startswith('MANUAL_POINTS'):
                manualPoints = int(line.split()[-1])
                manualP = True
                
            elif line.startswith('PREDICTORS'):
                predictors = self.getPred(line, True)
                
                returnInfo['predUsed'] = len(predictors)
                
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

            elif line.startswith('THEORETICAL_TIME') and 'True' in line:
                returnInfo['theoTime'] = True
                theoTime = True
            
        #Put false if theoTime line was not found
        if theoTime == False: returnInfo['theoTime'] = False
        
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
        
        
        