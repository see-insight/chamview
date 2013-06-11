#!/usr/bin/env python
"""Evaluator for Chamview predictors

Usage options:
    -h --help       Print this help message
    -i --dirImg     Image directory. Default is (./dataSets/ChamB_LB/frames)
    -g --dirGT      Ground Truth data directory. Default is (./dataSets/ChamB_LB/manualpoints/2013_06_04_dosalman/points.txt)
    -o --output     Output file. Default is (Performance_Report.txt)
    -p --predictor  Predictor Name. Default is all predictors
    -u --upBound    Determines the upper bound of results we can see
    -t --truePos    Determines the maximum value of a prediction to be considered as true positive
    -s --savedGraph Data results previously saved in text file that is used to graph.

Example: 
    
    $ evaluatePredictor.py -i ./images/Chameleon -g ./images/points.txt -o ./results.txt

"""
#This file helps to run evaluators through command line
#Manuel E. Dosal
#June 5, 2013

import subprocess
import sys
import getopt
from plotPerformance import PlotData

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def main(argc,argv):
    #Default arguments
    argFrameDir = './dataSets/ChamB_LB/frames'
    argGroundT = './dataSets/ChamB_LB/manualpoints/2013_06_04_dosalman/points.txt'
    argOutput = 'Performance_Report.txt'
    argPredictor = ''
    argUpBound = 50
    argTruePos = 5
    argSavedGraph = ''
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hi:g:o:p:u:t:s:', ['help','dirImg=','dirGT=','output=', 'predictor=','upBound=','truePos=', 'savedGraph='])
        except getopt.error, msg:
            raise Usage(msg)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            elif opt in ('-i', '--dirImg'):
               argFrameDir = arg
            elif opt in ('-g', '--dirGT'):
                argGroundT = arg
            elif opt in ('-o', '--output'):
                argOutput = arg
            elif opt in ('-p', '--predictor'):
                argPredictor = arg
            elif opt in ('-u', '--upBound'):
                argUpBound = arg
            elif opt in ('-t', '--truePos'):
                argTruePos = arg
            elif opt in ('-s', '--savedGraph'):
                argSavedGraph = arg

        #Determines if user wants to compute errors or plot a previously saved data
        if argSavedGraph != '':
            callPlotPerformance(argSavedGraph)
        else:
            callChamview(argFrameDir, argGroundT, argOutput, argPredictor, argUpBound, argTruePos)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2


def callChamview(argFrameDir, argGroundT, argOutput, argPredictor, argUpBound, argTruePos):
    
    command = ["./chamview.py", "-c", "Performance", "-r"]

    #Get predictor name
    command.append(argPredictor)
    
    command.append("-d")    
    
    #Get path for frames
    command.append(argFrameDir)    
    
    command.append("-p")    
    
    #Get ground truth path
    command.append(argGroundT)    
   
    #Create Evaluate argument. This is: argOutput-argUpBound-argTruePos
    argEvaluate = argOutput + '-' + str(argUpBound) + '-' + str(argTruePos) 
      
    #Add evaluate argument
    command.append("-e")
    command.append(argEvaluate)
   
    #Call subprocess 
    subprocess.call(command) 
    
def callPlotPerformance(argSavedGraph):
    #Define a new object to plot dataset    
    plotP = PlotData(argSavedGraph)
    plotP.plot()
    
if __name__ == '__main__':
    argc = len(sys.argv)
    sys.exit(main(argc,sys.argv))