#!/usr/bin/env python
"""SlideShow Function
Slideshow test program written by Dirk

Usage options:
    -h --help Print this help message
    -d --dir= change directory
    -p --pre= add preprocessor

Using convention described in the following blog posts:
    http://www.artima.com/weblogs/viewpost.jsp?thread=4829
    http://www.doughellmann.com/PyMOTW/getopt/

Should be able to use the program in the following ways:

*nix command line:
    ./slideshow.py 
    ./slideshow.py --help
    ./slideshow.py --dir ./new/image/directory/ 

As an argument to python:
    python slideshow.py --dir=./new/image/directory/

Python Prompt
    >import slideshow
    >slideshow.show('./new/image/directory/')
"""

import time
import sys
import getopt
from imagestack import *
from grammar import Grammar
import vocabulary as vocab

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def imshow(im,name=''):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(im,origin='lower')
    ax.set_axis_off()
    ax.set_title(name)
    fig.show()
    time.sleep(1)

def imshow2(im,name=''):
    im.show()
    time.sleep(1)

def slideshow(dirname='./images/',preprocessor=None):
    print dirname
    imst = ImageStack(dirname)
    while (imst.current_frame < imst.total_frames):
        im = imst.img_current
        if(im!=None and preprocessor!=None):
            #print "preprocess" 
            im=preprocessor.process(im)
        imshow(im,imst.name_current)
        imst.next()


def main(argv=None):
    dirname='./images'
    preprocessor=None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'h:d:p', ['help','dir=','pre='])
        except getopt.error, msg:
            raise Usage(msg)
        
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            elif opt in ('-d', '--dir'):
               dirname = arg 
            elif opt in ('-p', '--pre'):
               preprocessor = arg
        pre=vocab.getPreprocessor(preprocessor)
        slideshow(dirname,pre) 
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
