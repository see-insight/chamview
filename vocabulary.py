#!/usr/bin/env python
"""Lists and manages current image grammar vocabular


"""


import os
import sys
import getopt
import imp
import dircache
from numpy import *
from imagestack import ImageStack
from plugins import grammar 


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
        show()
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, 'For help use --help'
        return 2
def show():
    print "Choosers:"
    classes,names = find_subclasses('plugins',grammar.Chooser)
    print names
    print "" 
    print "Predictors:"
    classes,names = find_subclasses('plugins',grammar.Predictor)
    print names
    print "" 
    print "Preprocessors:"
    classes,names = find_subclasses('plugins',grammar.Preprocessor)
    print names
    print "" 

def getChooser(argChooser):
    #Load the Chooser subclass instance
    chooser_class,chooser_name = find_subclasses('plugins',grammar.Chooser)
    if not (argChooser in chooser_name):
        raise Usage('Chooser "'+argChooser+'" not found in plugins directory')
    chooser = chooser_class[chooser_name.index(argChooser)]()
    return chooser

def getPreprocessor(argPreproc):
    #Load the Preprocessor subclass instance
    if argPreproc != '':
        preproc_class,preproc_name = find_subclasses('plugins',grammar.Preprocessor)
        if not (argPreproc in preproc_name):
            raise Usage('Preprocessor "'+argPreproc+'" not found in plugins '+
                                                                        'directory')
        preproc = preproc_class[preproc_name.index(argPreproc)]()
        #If Preprocessors ever accept input arguments, they would replace None below
        preproc.setup(None)
    else:
        preproc = None
    return preproc

def getPredictors():
    #Load the Predictor subclass instances
    predictor,predictor_name = find_subclasses('plugins',grammar.Predictor)
    for i in range(0,len(predictor)):
        #predictor[i] will now hold a reference to an instance of the subclass
        predictor[i] = predictor[i]()
    return predictor,predictor_name

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
