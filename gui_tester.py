#!/usr/bin/env python
"""BasicGui tester program
Written by Dirk

Usage options:
    -h --help Print this help message
    -d --dir= image directory default (./images/)

See help for slideshow for more information
"""

import sys
import getopt
from imagestack import *
from grammar import basicgui

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def show(dirname='./images/'):
    print dirname
    imst = ImageStack(dirname)
    imst.get_point_kinds() #load default point names
    gui = basicgui.BasicGui()
    gui.setup()
    while (imst.exit == False):
        predict_point = zeros((1,imst.point_kinds,3))
        gui.choose(imst,predict_point,[])
        imst.next()

def main(argv=None):
    dirname='./images'
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
        show(dirname) 
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
