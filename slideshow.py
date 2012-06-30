#!/usr/bin/env python
"""SlideShow Function
Slideshow test program written by Dirk

Usage options:
    -h --help Print this help message
    -d --dir= change directory

Using convention described in the following blog post:
   http://www.artima.com/weblogs/viewpost.jsp?thread=4829

Should be able to use the program in the following ways:

*nix command line:
    ./slideshow.py options

As an argument to python:
    python slideshow options

Python Prompt
    >>>import slideshow
    >>>slideshow.main(options)
"""

import time
import sys
import getopt
from imagestack import *

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def main(argv=None):
    dirname = './images/'
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'h:d', ['help','dir='])
        except getopt.error, msg:
            raise Usage(msg)
        
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            elif opt in ('-d', '--dir'):
               dirname = arg 
       
        print dirname 
        imst = ImageStack(dirname)
        while (imst.current_frame < imst.total_frames):
            im = imst.show()
            time.sleep(1)
            imst.next()
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
