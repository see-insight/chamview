#!/usr/bin/env python
#This file allows to run evaluators through command line
#Manuel E. Dosal
#June 5, 2013
"""Chamview Evaluator

Usage options:
    -h --help       Print this help message.
    -d --dirImg     Image directory. Default is (none).
    -i --prep       Preprocessor subclass. Default is (none).
    -k --pkind      Point kind file. Default is (defaultPointKinds.txt).
    -p --dirGT      Ground Truth points directory. Default is (none).
    -r --predictor  Predictor Name that will be evaluated. Default is all the predictors.
    -o --output     Output directory where results are saved. Default is None.
    -u --upBound    Determines the upper bound of results we can see. Default is 50.
    -t --truePos    Determines the maximum error in pixels of a prediction to be considered as true positive. Default is 5.
    -n --dontShow   It indicates that user doesn't want to see the graphs created at the moment
    -s --savedGraph Data results previously saved in text file that is used to graph.
    -m --metadata   File of metadata.txt to plot graphs using the information in it. 
    -c --comDataSet Directory of datasets used to compare evaluations on them
    -a --runCham    Indicates that chamview interface will be displayed to save or use predictions
    -v --savePreds  File to save the Predicted Points to for re-use later
    -f --usePreds   Previously saved predicted points file to use as predicted points to save time
    -w --inspectout Specifies a file to save system and running time data

Example:

    $ evaluatePredictor.py -d ./images/Chameleon -p ./images/points.txt -o ./results.txt

"""
import os
import subprocess
import sys
import getopt
from plotPerformance import PlotData
import imp
import dircache
import timeit
import vocabulary as vocab
from numpy import *
from imagestack import ImageStack
from grammar import Grammar
from inspector import SystemInspector as si
import time

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def main(argc,argv):
    #Default arguments
    argFrameDir = ''
    argGroundT = ''
    argOutput = ''
    argPKind = 'defaultPointKinds.txt'
    argSysInspector = ''
    argPred = []
    argPreproc = ''
    argUpBound = 50
    argTruePos = 5
    argSavedGraph = ''
    argMetadata = ''
    argShow = True
    argComDataSet = ''
    argSavePred = ''
    argUsePred = ''
    argRunCham = False

    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hd:i:p:o:w:r:u:t:s:m:k:nc:v:f:a', ['help','dirImg=',
                         'prep=', 'dirGT=','output=', 'inspectout=', 'predictor=','upBound=','truePos=',
                         'savedGraph=', 'metadata=', 'pkind=', 'dontShow', 'argComDataSet=',
                         'savePreds=', 'usePreds=', 'runCham='])

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
            elif opt in ('-w', '--inspectout'):
                argSysInspector = arg
            elif opt in ('-r', '--predictor'):
                argPred.append(arg)
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
                argSavePred = arg
            elif opt in ('-f', '--usePreds'):
                argUsePred = arg
            elif opt in ('-a', '--runCham'):
                argRunCham = True

        #Determine if user wants to compute errors or plot a previously saved data
        if argSavedGraph != '':
            
            #-s Option
            #Plot dataset from a text file
            pd = PlotData(argSavedGraph, argUpBound)
            pd.plotSavedG(argOutput, argShow)
            
        elif argComDataSet != '':

            #-c Option
            #Show graphs to compare evaluations between datasets
            pd = PlotData(argComDataSet)
            pd.compareMetas(argOutput, argShow)

        elif argRunCham:
            
            if argSavePred == '' and argUsePred == '':
                #If both arguments are empty, then user can use chamview.py instead
                print 'If you do not want to save or use predictions, use the current version of chamview.py'
                
            else:
            
                #Run chamview gui because user wants to save or use predictions in a text file
                runChamview(argFrameDir, 'BasicGui', argPreproc, argOutput, argPKind, argGroundT, argSysInspector, argPred, argUpBound, argTruePos, argShow, argSavePred, argUsePred)

        elif argGroundT != '' or argMetadata != '':
            
            if argMetadata != '':
                #-m Option
                #Show graphs using Metadata info
                pd = PlotData(argMetadata)
                pd.plotMeta(argOutput, argShow)
            
            if argGroundT != '':
                #User wants to compute error in predictions and runs performance chooser
                runChamview(argFrameDir, 'Performance', argPreproc, argOutput, argPKind, argGroundT, argSysInspector, argPred, argUpBound, argTruePos, argShow, argSavePred, argUsePred)
    
        else:
                
            print 'No enough arguments were found to do the evaluation'

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2


def runChamview(argFrameDir, argChooser, argPreproc, argOutput, argPKind, argGroundT, argSysInspector, argPred, argUpBound, argTruePos, argShow, argSavePred, argUsePred):
    '''This method runs a similar program as chamview, with the chooser performance or basicgui'''
    
    #Start timer if argSysInspector
    if argSysInspector: start = timeit.default_timer()

    #Load images into memory
    imstack = ImageStack(argFrameDir)
    if imstack.total_frames == 0:
        raise Usage('No valid image files found in "'+argFrameDir+'"')
    imstack.load_img()

    #Load point kind and point position files
    imstack.get_point_kinds(argPKind)
    if argGroundT != '':
        pointsReceived = imstack.load_points(argGroundT)
        if not(pointsReceived): raise Usage('No valid points file found in "'+argGroundT+'"')

    #Load predictions previously computed
    if argUsePred != '':
        predictionsReceived = imstack.load_predictions(argUsePred)
        if not(predictionsReceived): raise Usage('No valid predictions file found in "'+argUsePred+'"')

    #Load the Chooser subclass instance
    chooser = vocab.getChooser(argChooser)
    chooser.setup()
      
    #Setup parameters if evaluation
    if argChooser == 'Performance':
        argEvaluate = argOutput + '-' + str(argUpBound) + '-' + str(argTruePos) + '-' + str(argShow) + '-' + argFrameDir
        chooser.setupPar(argEvaluate)

    #Load the Preprocessor subclass instance
    preproc = vocab.getPreprocessor(argPreproc)

    #Load the Predictor subclass instances
    predictor,predictor_name = vocab.getPredictors()

    #Load the Predictors needed for user
    if len(argPred) > 0:
        newPredictor = []
        newPredictor_name = []
        for p in argPred:
            try:
                predIndex = predictor_name.index(p)
                newPredictor.append(predictor[predIndex])
                newPredictor_name.append(predictor_name[predIndex])
            except Exception:
                pass #Continue with the same predictors
        predictor = newPredictor
        predictor_name = newPredictor_name

    #Instantiate predictions array of imstack
    if argUsePred == '': imstack.build_predictionsArray(len(predictor))

    #Preprocess the ImageStack image
    if preproc: imstack.img_current = preproc.process(imstack.img_current)

    #Initialize every predictor and optionally get a first guess
    predict_point = zeros((len(predictor),imstack.point_kinds,3))
    for i in range(0,len(predictor)):
        guess = predictor[i].setup(imstack)
        if guess != None:
            for j in range(0,imstack.point_kinds):
                predict_point[i,j] = guess
            #Add to predictions array
            if argUsePred == '': imstack.predictions[0] = predict_point

    #Pass argOutput to chooser if possible
    try:
        chooser.saveFile = argOutput
    except NameError:
        pass


    #Give this result to the chooser to get the initial ground-truth point
    chooser.choose(imstack,predict_point,predictor_name)

    if chooser.editedPointKinds:
        predict_point = update_point_array(predict_point,chooser.added,chooser.deleted)

    #Repeat until the chooser signals to exit
    while(imstack.exit == False):

        #Preprocess the ImageStack image
        if preproc: imstack.img_current = preproc.process(imstack.img_current)

        if argUsePred == '':

            #Give each predictor the current image stack and get a prediction back
            for i in range(0,len(predictor)):
                #print 'Predicting using:', predictor_name[i]
                predict_point[i] = predictor[i].predict(imstack,chooser.editedPointKinds)

            #Save predictions in predictions array of imstack
            #if imstack.current_frame < imstack.total_frames:
            imstack.predictions[imstack.current_frame] = predict_point

        else:
            #Use predictions previously computed and saved
            predict_point = imstack.predictions[imstack.current_frame]

        #Give this result to the chooser to get the "real" point
        chooser.choose(imstack,predict_point,predictor_name)
        if chooser.editedPointKinds:
            predict_point = update_point_array(predict_point,chooser.added,chooser.deleted)

    #Save points to text file
    try:
        if chooser.saveFile != '':
            pass
    except NameError:
        if argOutput != '': imstack.save_points(argOutput)

    #Save predicted points in a text file
    if argSavePred != '': imstack.save_predictions(argSavePred, predictor_name)

    #Run System Inspector
    if argSysInspector:
        import string

         #Stop timer and compute total time
        end = timeit.default_timer()
        totalTime = end - start

        #Compute the number of points modified and frames modified
        pointsModified = imstack.pointsModified()
        framesModified = imstack.framesModified()

        #Compute predictor activity aka how many accepted points came from each predictor
        pred_activity = [[string.upper(predictor_name[i])+'_POINTS',0] for i in range(len(predictor_name))]
        pred_activity.append(['MANUAL_POINTS',0])
        for frame in range(len(imstack.point_sources)):
            for kind in range(len(imstack.point_sources[frame])):
                source = imstack.point_sources[frame][kind]
                if imstack.point[frame][kind][0] > 0 or imstack.point[frame][kind][1] > 0:
                    pred_activity[source][1] += 1

        #Compute time data
        try:
            timePerPoint = totalTime / pointsModified
            timePerFrame = totalTime / framesModified
        except ZeroDivisionError:
            timePerPoint = 'N/A'
            timePerFrame = 'N/A'

        #Compile list of tuples of chamview specific attributes
        attributes = [('CHOOSER',argChooser),
                      ('PREPROCESSOR',argPreproc),
                      ('PREDICTORS',predictor_name),
                      ('IMAGE_DIRECTORY',argFrameDir),
                      ('TOTAL_POINTS',imstack.total_frames * imstack.point_kinds),
                      ('POINTS_MODIFIED',pointsModified),
                      ('MANUAL_POINTS',pred_activity[-1][1])]
        for source in pred_activity[:-1]:
            attributes.append((source[0],source[1]))
        attributes.extend([('TOTAL_FRAMES',imstack.total_frames),
                           ('FRAMES_MODIFIED',framesModified),
                           ('TOTAL_TIME',time.strftime('%H:%M:%S', time.gmtime(totalTime))),
                           ('TIME/POINT',timePerPoint),
                           ('TIME/FRAME',timePerFrame)])
                           
        if argUsePred != '':
            #Append a message that tells us if saved predictions were used
            attributes.append(('THEORETICAL_TIME', True))

        #Create SystemInspector object and pass it the additional chamview
        #specific attributes then write the object to a file
        inspector = si.SystemInspector(attributes)
        try:
            inspector.write_to_file(argSysInspector)
        except TypeError:
            inspector.write_to_file()

    #Clear out any Chooser or Predictor data
    chooser.teardown()
    for pred in predictor:
        pred.teardown()

def update_point_array(n_array,add,delete):
    if delete != []:
        #Delete Point information in predict_point for each index provided.
        temp = n_array.tolist()
        new = []
        for block in temp:
            new_block = []
            for i in range(len(block)):
                if i not in delete:
                    new_block.append(block[i])
            new.append(new_block)
        n_array = array(new)
    if add >= 1:
        #Add n new Point Kinds to predict_point.
        new = n_array.tolist()
        for i in range(add):
            for block in new:
                block.append([0,0,0])
        n_array = array(new)
    return n_array


def find_subclasses(path,superclass):
    #Returns a list of subclasses of 'superclass' given a directory 'path' to
    #search in and their class names. Adapted from www.luckydonkey.com
    subclasses = []
    subclassnames = []

    def look_for_subclass(modulename):
        try:
            module = __import__(modulename)
        except Exception as e:
            #There's an error in the module - don't load it
            print 'Unable to load plugin "'+modulename+'": '+repr(e)
            return
        #walk the dictionaries to get to the last one
        d=module.__dict__
        for m in modulename.split('.')[1:]:
            d = d[m].__dict__
        #Look through this dictionary for things that are subclasses of
        #modulename but not modulename itself
        for key, entry in d.items():
            if key == superclass.__name__: continue
            try:
                if issubclass(entry,superclass):
                    subclasses.append(entry)
                    subclassnames.append(key)
            except TypeError:
                #Occurs when a non-type is passed in to issubclass()
                continue

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith('.py'):
                path = os.path.join(root,name)
                modulename = path.rsplit('.',1)[0].replace(os.path.sep,'.')
                look_for_subclass(modulename)

    return subclasses,subclassnames

if __name__ == '__main__':
    argc = len(sys.argv)
    sys.exit(main(argc,sys.argv))
