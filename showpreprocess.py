#!/usr/bin/env python
""" Stitch two imges together into a single image
Algorithm by Dirk Colbry
Written by Jeremy Martin

Usage options:
    -h --help Print this help message
    -r --row row offset (user will be prompted if not specified)
    -c --col column offset (user will be prompted if not specified)
    
Example:
    imagestitch.py image1 image2
    (left-most image must be chosen as image1)
"""
import sys
import getopt
import slideshow
from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import vocabulary as vocab
from pylab import ginput
from string import atoi

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

    
def main(argv=None):
    dirname='./images'
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'r:c:h:d', ['row=', 'col=', 'help','dir='])
        except getopt.error, msg:
            raise Usage(msg)
        t = [0,0]
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            elif opt in ('-r', '--row'):
                print arg
                t[0] = atoi(arg)
            elif opt in ('-c', '--col'):
                print arg
                t[1] = atoi(arg)
        print args

        im = Image.open(args[-0]) 
        dir(im)
        slideshow.imshow(im)
        preps,names = vocab.getPreprocessors()       
        for p,n in zip(preps,names):
            print n
            pim = p.process(im)
            slideshow.imshow(pim,n)        


 
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

