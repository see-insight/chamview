import os
import sys
import imp
import dircache
from imagestack import ImageStack
from plugins import base


def main(argc,argv):
    if argc < 3 or argc > 5:
        print "usage: python chamview.py 'imageDirectory' chooserClass \
                                        [pointKindFile] [pointPositionFile]"
        sys.exit()

    #Get the image directory from the command line and load it
    imstack = ImageStack(argv[1])
    if imstack.total_frames == 0:
        print "No valid image files found in '"+argv[2]+"'"
        exit()
    imstack.load_img()

    #Get the name of the chooser to use from the command line and load it
    chooser_class,chooser_name = find_subclasses('plugins',base.Chooser)
    if not argv[2] in chooser_name:
        print "Chooser '",argv[1],"' not found in plugins folder"
        sys.exit()
    chooser = chooser_class[chooser_name.index(argv[2])]()
    chooser.setup()

    #Load point kinds from the file specified by the command line or the default
    if argc >= 4: imstack.get_point_kinds(argv[3])
    else: imstack.get_point_kinds()

    #Load point positions from the file specified by the command line, if any
    if argc == 5: imstack.load_points(argv[4])

    #Create an instance of every predictor in the plugins folder
    predictor_class,predictor_name = find_subclasses('plugins',base.Predictor)
    predictor = [[]]
    for subclass,name in predictor_class:
        predictor.append([subclass(),name])

    #Call init() on every predictor and get an initial guess from each

    #Hand this result over to the chooser

    #while(True) (figure out something better than True)
    #   for each predictor, give current imstack and get next predicted point
    #   hand predictions over to chooser

    #Save point positions to file



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
            if key == cls.__name__: continue
            try:
                if issubclass(entry,cls):
                    subclasses.append(entry)
                    subclassnames.append(key)
            except TypeError:
                #Occurs when a non-type is passed in to issubclass()
                continue

    for root, dirs, files in os.walk(path):
        for name in files:
            if (name.endswith('.py') or name.endswith('.pyc')):
                path = os.path.join(root,name)
                modulename = path.rsplit('.',1)[0].replace('/','.')
                look_for_subclass(modulename)

    return subclasses,subclassnames


if __name__ == '__main__':
    argc = len(sys.argv)
    main(argc,sys.argv)
