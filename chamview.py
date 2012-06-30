#!/usr/bin/env python
""" Main Chamview Testing Program
Usage:
     python chamview.py imageDirectory chooserClass [outputFile] [pointKindFile] [pointPositionFile]
    
Example:
    python chamview.py ./images/ Max

"""
import os
import sys
import imp
import dircache
from numpy import *
from imagestack import ImageStack
from plugins import base


def main(argc,argv):
    #Did the user specify the correct arguments?
    if argc < 3 or argc > 6:
        print "usage: python chamview.py imageDirectory chooserClass \
        [outputFile] [pointKindFile] [pointPositionFile]"
        sys.exit()

    #Get the image directory from the command line and load it
    imstack = ImageStack(argv[1])
    if imstack.total_frames == 0:
        print "No valid image files found in '"+argv[2]+"'"
        exit()
    imstack.load_img()

    #Get the name of the chooser to use from the command line and load it
    chooser_class,chooser_name = find_subclasses('plugins',base.Chooser)
    if not (argv[2] in chooser_name):
        print "Chooser '",argv[2],"' not found in plugins folder"
        sys.exit()
    chooser = chooser_class[chooser_name.index(argv[2])]()
    chooser.setup()

    #Get the output file name, if any
    if argc >= 4: outfile_name = argv[3]
    else: outfile_name = ''

    #Load point kinds from the file specified by the command line or the default
    if argc >= 5: imstack.get_point_kinds(argv[4])
    else: imstack.get_point_kinds()

    #Load point positions from the file specified by the command line, if any
    if argc == 6: imstack.load_points(argv[5])

    #Create an instance of every predictor in the plugins folder
    predictor,predictor_name = find_subclasses('plugins',base.Predictor)
    for i in range(0,len(predictor)):
        #predictor[i] will now hold a reference to an instance of the subclass
        predictor[i] = predictor[i]()

    #Initialize every predictor and optionally get a first guess
    predict_point = zeros((len(predictor),imstack.point_kinds,3))
    for i in range(0,len(predictor)):
        guess = predictor[i].setup(imstack)
        for j in range(0,imstack.point_kinds):
            predict_point[i,j] = guess

    #Give this result to the chooser to get the "real" first point
    chooser.choose(imstack,predict_point,predictor_name)

    #Repeat until the chooser wants to exit
    while(imstack.exit == False):
        #Give each predictor the current image stack and get a prediction back
        for i in range(0,len(predictor)):
            for j in range(0,imstack.point_kinds):
                predict_point[i,j] = predictor[0].predict(imstack)
        #Give this result to the chooser to get the "real" point
        chooser.choose(imstack,predict_point,predictor_name)

    #Save points to file
    if outfile_name != '': imstack.save_points(outfile_name)

    #Clear out any chooser or predictor data
    chooser.teardown()
    for pred in predictor:
        pred.teardown()


def find_subclasses(path,superclass):
    #Returns a list of subclasses of 'superclass' given a directory 'path' to
    #search in and their class names. Adapted from www.luckydonkey.com
    subclasses = []
    subclassnames = []

    def look_for_subclass(modulename):
        module = __import__(modulename)
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
                modulename = path.rsplit('.',1)[0].replace('/','.')
                look_for_subclass(modulename)

    return subclasses,subclassnames


if __name__ == '__main__':
    argc = len(sys.argv)
    main(argc,sys.argv)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
