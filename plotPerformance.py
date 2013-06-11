#This class takes a text file and graphs errors on predictors
#Manuel E. Dosal
#June 10, 2013

import os
import vocabulary as vocab

class PlotData:
    
    def __init__(self,directory=''):

        #Attributes
        self.numberPlots = 0
        self.file_in = None
        self.graphNames = []
        self.division = ''
        
        #Get performance attributes
        self.getPerformanceAtt()
        
        #Get the dataset and plot
        self.readAndPlot(directory)
        
    def readAndPlot(self, filename):
        
        print 'graphNames: ', self.graphNames
        
        if os.path.exists(filename) == False: return
        
        self.file_in = open(filename)
        for line in self.file_in:
            if line in (self.graphNames):
                self.plotGraph(line)
        
    def plotGraph(self,graphName):
        
        for line in self.file_in:
            if line == self.division: break
            
            
            
            print line    
        
    def getPerformanceAtt(self):
        #Create a new performance object
        per = vocab.getChooser('Performance')
        per.setup()
        
        #Update global variables
        self.graphNames = per.graphNames
        self.division = per.division