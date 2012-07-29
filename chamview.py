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
    argOutput = './output_points.txt'
    argPKind = 'defaultPointKinds.txt'
    argPPos = ''
    try:
        try:
            opts, args = getopt.getopt(argv[1:],
                                      'hd:c:i:o:k:p:',
                                      ['help','dir=','chooser=','prep=',
                                      'output=','pkind=','ppos='])
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
        run(argDir,argChooser,argPreproc,argOutput,argPKind,argPPos)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2


def run(argDir,argChooser,argPreproc,argOutput,argPKind,argPPos):
    #Load images into memory
    imstack = ImageStack(argDir)
    if imstack.total_frames == 0:
        raise Usage('No valid image files found in "'+argDir+'"')
    imstack.load_img()

    #Load point kind and point position files
    imstack.get_point_kinds(argPKind)
    if argPPos != '': imstack.load_points(argPPos)

    #Load the Chooser subclass instance
    chooser = vocab.getChooser(argChooser)
    chooser.setup()

    #Load the Preprocessor subclass instance
    preproc = vocab.getPreprocessor(argPreproc)

    #Load the Predictor subclass instances
    predictor,predictor_name = vocab.getPredictors()

    #Preprocess the ImageStack image
    if preproc: imstack.img_current = preproc.process(imstack.img_current)

    #Initialize every predictor and optionally get a first guess
    predict_point = zeros((len(predictor),imstack.point_kinds,3))
    for i in range(0,len(predictor)):
        guess = predictor[i].setup(imstack)
        if guess != None:
            for j in range(0,imstack.point_kinds):
                predict_point[i,j] = guess

    #Give this result to the chooser to get the initial ground-truth point
    chooser.choose(imstack,predict_point,predictor_name)

    #Repeat until the chooser signals to exit
    while(imstack.exit == False):
        #Preprocess the ImageStack image
        if preproc: imstack.img_current = preproc.process(imstack.img_current)
        #Give each predictor the current image stack and get a prediction back
        for i in range(0,len(predictor)):
            predict_point[i] = predictor[i].predict(imstack)
        #Give this result to the chooser to get the "real" point
        chooser.choose(imstack,predict_point,predictor_name)

    #Save points to file
    if argOutput != '': imstack.save_points(argOutput)

    #Clear out any Chooser or Predictor data
    chooser.teardown()
    for pred in predictor:
        pred.teardown()


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
