#!/usr/bin/env python
#This file allows to run evaluators through command line
#Manuel E. Dosal
#June 5, 2013
"""Evaluator for Chamview predictors

Usage options:
    -h --help       Print this help message.
    -d --dirImg     Image directory. Default is (./dataSets/ChamB_LB/frames).
    -i --prep       Preprocessor subclass. Default is (none).
    -k --pkind      Point kind file. Default is (defaultPointKinds.txt).
    -p --dirGT      Ground Truth points directory. Default is (./dataSets/ChamB_LB/manualpoints/2013_06_04_dosalman/points.txt).
    -r --predictor  Predictor Name. Default is all predictors.
    -o --output     Output directory where results are saved. Default is current directory.
    -u --upBound    Determines the upper bound of results we can see. Default is 50.
    -t --truePos    Determines the maximum value of a prediction to be considered as true positive. Default is 5.
    -s --savedGraph Data results previously saved in text file that is used to graph.
    -m --metadata   Directory of metadata to plot graphs using the information there.
    -n --dontShow   It indicates that user doesn't want to plot graphs at the moment
    -c --comDataSet Directory of datasets used to compare evaluations on them
    -v --savePreds  File to save the Predicted Points to for re-use later
    -f --usePreds   Previously saved predicted points file to use as predicted points to save time

Example:

    $ evaluatePredictor.py -d ./images/Chameleon -p ./images/points.txt -o ./results.txt

"""
import subprocess
import sys
import getopt
from plotPerformance import PlotData

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def main(argc,argv):
    #Default arguments
    argFrameDir = ''
    argGroundT = ''
    argOutput = ''
    argPKind = ''
    argPredictor = []
    argPreproc = ''
    argUpBound = 50
    argTruePos = 5
    argSavedGraph = ''
    argMetadata = ''
    argShow = True
    argComDataSet = ''
    argSavePreds = ''
    argUsePreds = ''

    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hd:i:p:o:r:u:t:s:m:k:nc:v:f:', ['help','dirImg=',
                         'prep=', 'dirGT=','output=', 'predictor=','upBound=','truePos=',
                         'savedGraph=', 'metadata=', 'pkind=', 'dontShow', 'argComDataSet=',
                         'savePreds=', 'usePreds='])

        except getopt.error, msg:
            raise Usage(msg)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            elif opt in ('-d', '--dirImg'):
                argFrameDir = arg
            elif opt in ('-i', '--prep'):
                argPreproc = arg
            elif opt in ('-p', '--dirGT'):
                argGroundT = arg
            elif opt in ('-o', '--output'):
                argOutput = arg
            elif opt in ('-r', '--predictor'):
                argPredictor.append(arg)
            elif opt in ('-u', '--upBound'):
                argUpBound = arg
            elif opt in ('-t', '--truePos'):
                argTruePos = arg
            elif opt in ('-s', '--savedGraph'):
                argSavedGraph = arg
            elif opt in ('-m', '--metadata'):
                argMetadata = arg
            elif opt in ('-k', '--pkind'):
                argPKind = arg
            elif opt in ('-n', '--dontShow'):
                argShow = False
            elif opt in ('-c', '--comDataSet'):
                argComDataSet = arg
            elif opt in ('-v', '--savePreds'):
                argSavePreds = arg
            elif opt in ('-f', '--usePreds'):
                argUsePreds = arg

        #Determine if user wants to compute errors or plot a previously saved data
        if argSavedGraph != '':

            #Plot dataset from a text file
            pd = PlotData(argSavedGraph, argUpBound)
            pd.plotSavedG()

        elif argMetadata != '':

            #Show graphs using Metadata info
            pd = PlotData(argMetadata)
            pd.plotMeta()

        elif argComDataSet != '':

            #Show graphs to compare evaluations between datasets
            pd = PlotData(argComDataSet)
            pd.compareMetas(argOutput)

        else:
            #compute errors and then plot
            callChamview(argFrameDir, argGroundT, argOutput, argPredictor, argUpBound, argTruePos, argPKind, argPreproc, argShow, argSavePreds, argUsePreds)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2


def callChamview(argFrameDir, argGroundT, argOutput, argPredictor, argUpBound, argTruePos, argPKind, argPreproc, argShow, argSavePreds, argUsePreds):

    command = ["./chamview.py", "-c", "Performance"]

    #Get predictor names
    if len(argPredictor) > 0:
        for p in argPredictor:
            command.append("-r")
            command.append(p)

    #Get path for frames
    if argFrameDir != '':
        command.append("-d")
        command.append(argFrameDir)

    #Add preprocessor
    if argPreproc != '':
        command.append("-i")
        command.append(argPreproc)

    #Get ground truth path
    if argGroundT != '':
        command.append("-p")
        command.append(argGroundT)

    #Add pointK directory
    if argPKind != '':
        command.append("-k")
        command.append(argPKind)

    #Add predictor saving/using info
    if argSavePreds != '':
        command.append('-a')
        command.append(argSavePreds)
    if argUsePreds != '':
        command.append('-u')
        command.append(argUsePreds)
    if argSavePreds != '' or argUsePreds != '':
        command[0] = './chamsim.py'

    #Add evaluate argument
    command.append("-e")
    #Create Evaluate argument. This is: argOutput-argUpBound-argTruePos
    argEvaluate = argOutput + '-' + str(argUpBound) + '-' + str(argTruePos) + '-' + str(argShow)
    command.append(argEvaluate)

    #Call subprocess
    subprocess.call(command)

if __name__ == '__main__':
    argc = len(sys.argv)
    sys.exit(main(argc,sys.argv))
