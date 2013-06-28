#!/usr/bin/env python
""" Return the most useful 2-dimensional representation of an image
Written by Jeremy Martin

Usage options:
    -h --help Print this help message
    
Example:
    colorspace.py imagefile
"""
import sys
import getopt
from numpy import *
from PIL import Image
from PIL import ImageEnhance
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import skimage.color as color
from skimage.feature import match_template

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg;


#Function to take the given template and match it (from skimage)
def test(image, template):
    result = match_template(image, template)
    ij = unravel_index(argmax(result), result.shape)
    x, y = ij[::-1]
    return y,x

def colorspace(image):
    pil_im = Image.open(image) 
    enhancer = ImageEnhance.Contrast(pil_im)
    im_enh = enhancer.enhance(2)
    #Conversions to separate color spaces
    rgb = mpimg.pil_to_array(pil_im)
    hsv = color.rgb2hsv(rgb)
    xyz = color.rgb2xyz(rgb)
    grey = color.rgb2grey(rgb)
    cie = color.rgb2rgbcie(rgb)
    enh = mpimg.pil_to_array(im_enh)

    r,c = rgb[:,:,0].shape
    #Slicing of arrays to get each 2-dimensional matrix
    #(z-slice produces an error, still not fixed)
    names = [ 'red', 'green', 'blue',
              'Hue', 'Saturation', 'Valuse',
              'Gray',
              'Enhanced Red', 'Enhanced Green', 'Enhanced Blue',
              'CIE[1]', 'CIE[2]', 'CIE[3]',
              'X', 'Y', 'Z']
    slices = [rgb[:,:,0], rgb[:,:,1], rgb[:,:,2],
              hsv[:,:,0], hsv[:,:,1], hsv[:,:,2],
              grey,
              enh[:,:,0], enh[:,:,1], enh[:,:,2],
              cie[:,:,0], cie[:,:,1], cie[:,:,2],
              xyz[:,:,0], xyz[:,:,1]]#, xyz[:,:,2]]
    #Reference to where the templates should be matched to
    dist_compare = [[int(r*3/40),int(r*12/40),
                     int(c*6/40),int(c*19/40)],
                    [int(r*3/40),int(r*7/40),
                     int(c*18/40),int(c*22/40)],
                    [int(r*4/40),int(r*9/40),
                     int(c*24/40),int(c*35/40)],
                    [int(r*9/40),int(r*12/40),
                     int(c*33/40),int(c*35/40)],
                    [int(r*19/40),int(r*23/40),
                     int(c*12/40),int(c*17/40)],
                    [int(r*18/40),int(r*25/40),
                     int(c*22/40),int(c*27/40)],
                    [int(r*16/40),int(r*20/40),
                     int(c*35/40),int(c*39/40)],
                    [int(r*28/40),int(r*38/40),
                     int(c*4/40),int(c*19/40)],
                    [int(r*25/40),int(r*32/40),
                     int(c*31/40),int(c*37/40)],
                    [int(r*34/40),int(r*38/40),
                     int(c*25/40),int(c*31/40)]]
    slice_count = 0
    errors = []
    fig = plt.figure() 
    while slice_count < len(slices):
        temp_count = 0
        err_dist = 0
        curr_im = slices[slice_count]
        #Test templates of the current image
        templates = [curr_im[int(r*3/40):int(r*12/40),
                             int(c*6/40):int(c*19/40)],
                     curr_im[int(r*3/40):int(r*7/40),
                             int(c*18/40):int(c*22/40)],
                     curr_im[int(r*4/40):int(r*9/40),
                             int(c*24/40):int(c*35/40)],
                     curr_im[int(r*9/40):int(r*12/40),
                             int(c*33/40):int(c*35/40)],
                     curr_im[int(r*19/40):int(r*23/40),
                             int(c*12/40):int(c*17/40)],
                     curr_im[int(r*18/40):int(r*25/40),
                             int(c*22/40):int(c*27/40)],
                     curr_im[int(r*16/40):int(r*20/40),
                             int(c*35/40):int(c*39/40)],
                     curr_im[int(r*28/40):int(r*38/40),
                             int(c*4/40):int(c*19/40)],
                     curr_im[int(r*25/40):int(r*32/40),
                             int(c*31/40):int(c*37/40)],
                     curr_im[int(r*34/40):int(r*38/40),
                             int(c*25/40):int(c*31/40)]]
        ##TODO show image here
        ax = fig.add_subplot(3,5,slice_count,title=names[slice_count])
        ax.set_axis_off()
        ax.imshow(slices[slice_count], origin='lower')
        while temp_count < len(templates):
            row,col = test(slices[slice_count],templates[temp_count])
            #Total errors in current image
            err_dist += sqrt((row-dist_compare[temp_count][0])**2+
                             (col-dist_compare[temp_count][2])**2)
            temp_count += 1
        ax.set_xlabel(err_dist)
        errors.append(err_dist)
        slice_count += 1
    fig.show();
    raw_input("Press Enter to continue...")
    #Least defaults to first slice
    least_item = errors[0]
    least_ind = 0
    for index,item in enumerate(errors):   
        if item < least_item:
            least_item = item
            least_ind = index
    return slices[least_ind]

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
        print args
        imagefile = args[-0]
        return colorspace(imagefile)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
