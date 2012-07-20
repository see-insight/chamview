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
from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pylab import ginput
from string import atoi

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;

def picker(im1, im2):

    imgL = Image.open(im1)
    imgR = Image.open(im2)

    print 'Pick a similar point on both images'
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(121)
    ax1.set_axis_off()
    ax1.imshow(imgL, origin='lower')
    ax2 = fig1.add_subplot(122)
    ax2.set_axis_off()
    ax2.imshow(imgR, origin='lower')
    LOffset,ROffset = ginput(2)
    plt.close()
    
    offset = [0,0]
    # Makes sure that the right-most image can be chosen first.
    # However, it is assumed that the left-most image is displayed
    # on the left.
    if ROffset[0] <= ROffset[0]:
        offset[0] = LOffset[1]-ROffset[1]
        offset[1] = LOffset[0]-ROffset[0]
    if ROffset[0] > LOffset[0]:
        offset[0] = ROffset[1]-LOffset[1]
        offset[1] = ROffset[0]-LOffset[0]
    return offset

# Wrapper function for evaluating the variable IA.
def WA(im1, im2, t):
    
    t = int32([round(i) for i in t])
    
    row1,col1 = im1[:,:,0].shape
    row2,col2 = im2[:,:,0].shape
    
    row_b = array([0, t[0], row1, row2+t[0]])
    col_b = array([0, t[1], col1, col2+t[1]])
    rmin = min(row_b)
    rmax = max(row_b)
    cmin = min(col_b)
    cmax = max(col_b)

    im = uint8(zeros((rmax-rmin, cmax-cmin, 3)))

    r1 = 0
    r2 = t[0]
    c1 = 0
    c2 = t[1]
    bound = array([r2, row1, c2, col1])

    if (t[0] < 0):
        r1 = -t[0]
        r2 = 0
        bound[0] = r1
        bound[1] = row2

    if (t[1] < 0):
        c1 = -t[1]
        c2 = 0
        bound[2] = c1
        bound[3] = col2

    im[r1:r1+row1, c1:c1+col1, :] = im1
    # Overlap of image A
    IA = im[bound[0]:bound[1], bound[2]:bound[3], :]
    return IA
  

def imagestitch(im1, im2, t):

    # Solves the problem of images appearing upside-down
    im1 = Image.open(im1)
    im2 = Image.open(im2)
    im1 = mpimg.pil_to_array(im1)
    im2 = mpimg.pil_to_array(im2)
    
    IA = WA(im1,im2,t)
    
    t = int32([round(i) for i in t])

    row1,col1 = im1[:,:,0].shape
    row2,col2 = im2[:,:,0].shape

    # Potential boundaries of the new image
    row_b = array([0, t[0], row1, row2+t[0]])
    col_b = array([0, t[1], col1, col2+t[1]])

    rmin = min(row_b)
    rmax = max(row_b)
    cmin = min(col_b)
    cmax = max(col_b)

    # Blank template the size of the new image
    im = uint8(zeros((rmax-rmin, cmax-cmin, 3)))

    r1 = 0
    r2 = t[0]
    c1 = 0
    c2 = t[1]
    bound = array([r2, row1, c2, col1])

    # Swapping statements if any value is negative
    if (t[0] < 0):
        r1 = -t[0]
        r2 = 0
        bound[0] = r1
        bound[1] = row2
        print 'swapping r'

    if (t[1] < 0):
        c1 = -t[1]
        c2 = 0
        bound[2] = c1
        bound[3] = col2
        print 'swapping c'
    
    x = arange(1,bound[3]-bound[2]+1)
    y = arange(1,bound[1]-bound[0]+1)
    [a,b] = meshgrid(x,y)

    if (t[0] < 0):
        b = b.max()-b

    if (t[1] < 0):
        a = a.max()-a

    # Minimum distance to the upper left and lower right edges of overlap    
    m1 = minimum(a,b)
    m2 = minimum(a.max()-a, b.max()-b)
    tot = m1 + m2

    # Ratio of pixels in each image
    A = zeros((tot[:,0].size,tot[0,:].size,3))
    B = zeros((tot[:,0].size,tot[0,:].size,3))
    A[:,:,0] = double(m1)/double(tot)
    A[:,:,1] = double(m1)/double(tot)
    A[:,:,2] = double(m1)/double(tot)
    B[:,:,0] = double(m2)/double(tot)
    B[:,:,1] = double(m2)/double(tot)
    B[:,:,2] = double(m2)/double(tot)

    im[r1:r1+row1, c1:c1+col1, :] = im1
    im[bound[0]:bound[1], bound[2]:bound[3], :] = 0
    im[r2:r2+row2, c2:c2+col2, :] = im2
    # Overlap of image B
    IB = im[bound[0]:bound[1], bound[2]:bound[3], :]
    # Blending of overlapped pixels
    im[bound[0]:bound[1], bound[2]:bound[3], :] = uint8(double(IA)*B + double(IB)*A)

    return im

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
        imagefile_1 = args[-0]
        imagefile_2 = args[-1]
        if(t[0] == 0 and t[1] == 0):
            t = picker(imagefile_1, imagefile_2)
        fig2 = plt.imshow(imagestitch(imagefile_1,imagefile_2,t), origin='lower')
        fig2.axes.get_xaxis().set_visible(False)
        fig2.axes.get_yaxis().set_visible(False)
        plt.show()
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

