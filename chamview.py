#!/usr/bin/env python
"""Main Chamview testing program

Usage options:
    -h --help    Print this help message
    -d --dir     Image directory. Default is (./images)
    -c --chooser Chooser subclass. Default is (BasicGui)
    -i --prep    Preprocessor subclass. Default is (none)
    -o --output  Output file. Default is (none)
    -k --pkind   Point kind file. Default is (defaultPointKinds.txt)
    -p --ppos    Previously saved output file. Default is (none)

Example:

    >>> print "hello world"
    hello world

"""


import os
import sys
import getopt
import imp
import dircache
import timeit
import vocabulary as vocab
from numpy import *
from imagestack import ImageStack
from grammar import Grammar


class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;


def main(argc,argv):
    #Default arguments
    argDir = './images'
    argChooser = 'BasicGui'
    argPreproc = ''
    argOutput = ''
    argPKind = 'defaultPointKinds.txt'
    argPPos = ''
    argSysInspector = ''
    try:
        try:
            opts, args = getopt.getopt(argv[1:],
                                      'hd:c:i:o:k:p:s',
                                      ['help','dir=','chooser=','prep=',
                                      'output=','pkind=','ppos=','inspect='])
        except getopt.error, msg:
            raise Usage(msg)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            elif opt in ('-d', '--dir'):
               argDir = arg
            elif opt in ('-c', '--chooser'):
                argChooser = arg
            elif opt in ('-i', '--prep'):
                argPreproc = arg
            elif opt in ('-o', '--output'):
                argOutput = arg
            elif opt in ('-k', '--pkind'):
                argPKind = arg
            elif opt in ('-p', '--ppos'):
                argPPos = arg
            elif opt in ('-s', '--inspect'):
                argSysInspector = arg
        if argOutput == '':
            argOutput = argDir+'.txt'
        run(argDir,argChooser,argPreproc,argOutput,argPKind,argPPos)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2


def run(argDir,argChooser,argPreproc,argOutput,argPKind,argPPos):
    
    #Compute the time since beginning to the end--------------------------------
    if argSysInspector: start = timeit.default_timer()
    #---------------------------------------------------------------------------
    
    #Load images into memory
    imstack = ImageStack(argDir)
    if imstack.total_frames == 0:
        raise Usage('No valid image files found in "'+argDir+'"')
    imstack.load_img()

    #Load point kind and point position files
    imstack._get_point_kinds(argPKind)
    if argPPos != '': imstack.load_points(argPPos)

    #Load the Chooser subclass instance
    chooser = vocab.getChooser(argChooser)
    chooser.setup()

    #Load the Preprocessor subclass instance
    preproc = vocab.getPreprocessor(argPreproc)

    #Load the Predictor subclass instances
    predictor,predictor_name = vocab.getPredictors()
    
    #Picking only some predictors for debugging purposes------------------------
    predictor= [predictor[1], predictor[3]]
    predictor_name= [predictor_name[1], predictor_name[3]]
    #---------------------------------------------------------------------------

    #Preprocess the ImageStack image
    if preproc: imstack.img_current = preproc.process(imstack.img_current)

    #Initialize every predictor and optionally get a first guess
    predict_point = zeros((len(predictor),imstack.point_kinds,3))
    for i in range(0,len(predictor)):
        guess = predictor[i].setup(imstack)
        if guess != None:
            for j in range(0,imstack.point_kinds):
                predict_point[i,j] = guess

    def print_var_info():
        print '****SELECTED POINTS:****\n', imstack.point
        print '****PREDICTED POINTS:****\n', predict_point
        #print '****CURRENT FRAME:****\n', imstack.current_frame
        print '****ACTIVE POINT:****\n', chooser.activePoint
        print '****PREDICTOR HISTORY:****\n', chooser.selectedPredictions
        #print '****POINT KINDS:****\n', imstack.point_kind_list
        #print '****POINT KINDS ADDED:****\n', chooser.added
        #print '****POINT KINDS DELETED:****\n', chooser.deleted

        
    print_var_info()

    #Give this result to the chooser to get the initial ground-truth point
    print 'call chooser'
    chooser.choose(imstack,predict_point,predictor_name)
    print 'exit chooser'
    if chooser.editedPointKinds:    
        predict_point = update_point_array(predict_point,chooser.added,chooser.deleted)

    print 'ENTER loop'
    #Repeat until the chooser signals to exit
    while(imstack.exit == False):
        #Preprocess the ImageStack image
        if preproc: imstack.img_current = preproc.process(imstack.img_current)
        #Give each predictor the current image stack and get a prediction back
        for i in range(0,len(predictor)):
            predict_point[i] = predictor[i].predict(imstack)
            
        print_var_info()
        
        #Give this result to the chooser to get the "real" point
        print 'call chooser'
        chooser.choose(imstack,predict_point,predictor_name)
        print 'exit chooser'

        if chooser.editedPointKinds:    
            predict_point = update_point_array(predict_point,chooser.added,chooser.deleted)
            
    print '\n###### FINAL VARIABLE VALUES ######\n'
    print_var_info()

    #Save points to file
    if argOutput != '': imstack.save_points(argOutput)
    print 'EXIT loop'
    
    #Run System Inspector
    if argSysInspector : 
        
         #Stop timer and compute total time
        end = timeit.default_timer()
        totalTime = end - start

        #Compute the number of points modified and frames modified
        pointsModified = imstack.pointsModified()
        framesModified = imstack.framesModified()
        try:
            timePerPoint = totalTime / pointsModified
            timePerFrame = totalTime / framesModified
        except ZeroDivisionError:
            timePerPoint = 'N/A'
            timePerFrame = 'N/A'
        
        dictionary = {'CHOOSER':argChooser,
                      'PREPROCESSOR':argPreproc,
                      'PREDICTORS':predictor_name,
                      'TOTAL_POINTS':imstack.total_frames * imstack.point_kinds,
                      'TOTAL_FRAMES':imstack.total_frames,
                      'TOTAL_TIME':totalTime,
                      'POINTS_MODIFIED':pointsModified,
                      'FRAMES_MODIFIED':framesModified,
                      'TIME/POINT': timePerPoint,
                      'TIME/FRAME': timePerFrame}
                      
        inspector = SystemInspector(dictionary)
        inspector.write_to_file(argSysInspector)
        
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

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
