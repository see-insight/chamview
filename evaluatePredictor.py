#!/usr/bin/env python
"""Evaluator for Chamview predictors

Usage options:
    -h --help       Print this help message
    -i --dirImg     Image directory. Default is (./dataSets/ChamB_LB/frames)
    -g --dirGT      Ground Truth data directory. Default is (./dataSets/ChamB_LB/manualpoints/2013_06_04_dosalman/points.txt)
    -o --output     Output file. Default is (none)
    -p --predictor  Predictor Name. Default is (Kinematic)

Example: 
    
    $ evaluatePredictor.py -i ./images/Chameleon -g ./images/points.txt -o ./results.txt

"""

import subprocess
import sys
import getopt
from numpy import *


class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def main(argc,argv):
    #Default arguments
    argFrameDir = './dataSets/ChamB_LB/frames'
    argGroundT = './dataSets/ChamB_LB/manualpoints/2013_06_04_dosalman/points.txt'
    argOutput = ''
    argPredictor = 'Kinematic'
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hi:g:o:p:', ['help','dirImg=','dirGT=','output=', 'predictor='])
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
            
        if argOutput == '':
            argOutput = argFrameDir + '.txt'

        callChamview(argFrameDir, argGroundT, argOutput, argPredictor)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2


def callChamview(argFrameDir, argGroundT, argOutput, argPredictor):

    command = ["./chamview.py", "-c", "Performance", "-r"]

    #Get predictor name
    command.append(argPredictor)

    command.append("-d")
    
    #Get path for frames
    command.append(argFrameDir)
    
    command.append("-p")
    
    #Get ground truth path
    command.append(argGroundT)
    
    subprocess.call(command)
    
if __name__ == '__main__':
    argc = len(sys.argv)
    sys.exit(main(argc,sys.argv))