from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pylab import ginput

def picker (imgL, imgR):

    print 'Pick a similar point on both images'
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    imgL = imgL.transpose(Image.FLIP_TOP_BOTTOM)
    ax1.imshow(imgL)
    ax2 = fig.add_subplot(122)
    imgR = imgR.transpose(Image.FLIP_TOP_BOTTOM)
    ax2.imshow(imgR)
    LOffset = ginput(1)
    print 'Clicked',LOffset
    ROffset = ginput(1)
    print 'Clicked',ROffset
    
    offset = [0,0]
    offset[0] = int(LOffset[0][0]-ROffset[0][0])
    offset[1] = int(LOffset[0][1]-ROffset[0][1])
    return offset

def WA(im1, im2, t):
    
    t = int32([round(i) for i in t])
    t = t[::-1]
    

    x1 = im1[:,0,0].size
    x2 = im2[:,0,0].size
    y1 = im1[0,:,0].size
    y2 = im2[0,:,0].size
    
    xb = array([0, t[0], x1, x2+t[0]])
    yb = array([0, t[1], y1, y2+t[1]])

    xmin = min(xb)
    xmax = max(xb)
    ymin = min(yb)
    ymax = max(yb)

    im = uint8(zeros((xmax-xmin, ymax-ymin, 3)))

    r1 = 0
    r2 = t[0]
    c1 = 0
    c2 = t[1]
    bound = array([r2, x2, c2, y2])

    if (t[0] < 0):
        r1 = -t[0]
        r2 = 0
        bound[0] = r1
        bound[1] = x2
        print 'swapping r'

    if (t[1] < 0):
        c1 = -t[1]
        c2 = 0
        bound[2] = c1
        bound[3] = y2
        print 'swapping c'

    im[r1:r1+x1, c1:c1+y1, :] = im1
    IA = im[bound[0]:bound[1]+1, bound[2]:bound[3]+1, :]
    return IA

def moviestitch(im1, im2, t):

    im1 = mpimg.imread(im1)
    im2 = mpimg.imread(im2)

    IA = WA(im1,im2,t)
    
    t = int32([int(i) for i in t])
    t = t[::-1]

    x1 = im1[:,0,0].size
    x2 = im2[:,0,0].size
    y1 = im1[0,:,0].size
    y2 = im2[0,:,0].size
    
    xb = array([0, t[0], x1, x2+t[0]])
    yb = array([0, t[1], y1, y2+t[1]])

    xmin = min(xb)
    xmax = max(xb)
    ymin = min(yb)
    ymax = max(yb)

    im = uint8(zeros((xmax-xmin, ymax-ymin, 3)))

    r1 = 0
    r2 = t[0]
    c1 = 0
    c2 = t[1]
    bound = array([r2, x2, c2, y2])

    if (t[0] < 0):
        r1 = -t[0]
        r2 = 0
        bound[0] = r1
        bound[1] = x2
        print 'swapping r'

    if (t[1] < 0):
        c1 = -t[1]
        c2 = 0
        bound[2] = c1
        bound[3] = y2
        print 'swapping c'

    x = arange(1,(bound[3]-bound[2]+2))
    y = arange(1,(bound[1]-bound[0]+2))
    [a,b] = meshgrid(x,y)

    if (1+t[0] < 1):
        b = b.max()-b

    if (1+t[1] < 1):
        a = a.max()-a
    
    m1 = minimum(a,b)
    m2 = minimum(a.max()-a, b.max()-b)
    tot = m1 + m2

    A = zeros((bound[1]-bound[0]+1, bound[3]-bound[2]+1, 3))
    B = zeros((bound[1]-bound[0]+1, bound[3]-bound[2]+1, 3))
    A[:,:,0] = double(m1)/double(tot)
    A[:,:,1] = double(m1)/double(tot)
    A[:,:,2] = double(m1)/double(tot)
    B[:,:,0] = double(m2)/double(tot)
    B[:,:,1] = double(m2)/double(tot)
    B[:,:,2] = double(m2)/double(tot)

    im[r1:r1+x1, c1:c1+y1, :] = im1
    
    im[r2:r2+x2, c2:c2+y2, :] = im2
    IB = im[bound[0]:bound[1]+1, bound[2]:bound[3]+1, :]
    
    im[bound[0]:bound[1]+1, bound[2]:bound[3]+1, :] = uint8(double(IA)*B + double(IB)*A)

    return im

i1 = 'img_file'
i2 = 'img_file'

#t = picker(i1, i2)
t = [350.3,16.3]

imgplot = plt.imshow(moviestitch(i1,i2,t), origin='lower')
