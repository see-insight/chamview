from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pylab import ginput

def picker (im1, im2):

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
    LOffset = ginput(1)
    ROffset = ginput(1)
    fig1 = plt.close()
    
    offset = [0,0]
    # Offset is set up as [row,column] and not [x,y]
    offset[0] = LOffset[0][1]-ROffset[0][1]
    offset[1] = LOffset[0][0]-ROffset[0][0]
    return offset

# Wrapper function for evaluating the variable IA.
def WA(im1, im2, t):
    
    t = int32([round(i) for i in t]) 

    row1 = im1[:,0,0].size
    row2 = im2[:,0,0].size
    col1 = im1[0,:,0].size
    col2 = im2[0,:,0].size
    
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

    if (1+t[0] < 1):
        r1 = -t[0]
        r2 = 0
        bound[0] = r1
        bound[1] = row2

    if (1+t[1] < 1):
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

    row1 = im1[:,0,0].size
    row2 = im2[:,0,0].size
    col1 = im1[0,:,0].size
    col2 = im2[0,:,0].size

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
    if (1+t[0] < 1):
        r1 = -t[0]
        r2 = 0
        bound[0] = r1
        bound[1] = row2
        print 'swapping r'

    if (1+t[1] < 1):
        c1 = -t[1]
        c2 = 0
        bound[2] = c1
        bound[3] = col2
        print 'swapping c'
    
    x = arange(1,bound[3]-bound[2]+1)
    y = arange(1,bound[1]-bound[0]+1)
    [a,b] = meshgrid(x,y)

    if (1+t[0] < 1):
        b = b.max()-b

    if (1+t[1] < 1):
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

imgfile_1 = 'test_file'
imgfile_2 = 'test_file'

t = picker(imgfile_1, imgfile_2)
fig2 = plt.imshow(imagestitch(imgfile_1,imgfile_2,t), origin='lower')
fig2.axes.get_xaxis().set_visible(False)
fig2.axes.get_yaxis().set_visible(False)
