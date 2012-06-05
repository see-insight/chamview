import os
from PIL import Image
from pylab import *
from scipy.ndimage import filters


'''
Creates a list of filenames of all jpg images in a directory
-Returns a list of strings
'''
def get_imglist(path):
    files = []
    for f in os.listdir(path):
        if f.endswith('.jpg'):
            files.append(os.path.join(path,f))
    return files


'''
Resize an image array
-Returns a numpy array
'''
def img_resize(arr,size):
    img = Image.fromarray(uint8(arr))
    return array(img.resize(size))


'''
Histogram normalization of a grayscale image
-img is a PIL image
-Returns the new PIL image and the normalization function
'''
def img_normalize(img,nbr_bins=256):
    # get image histogram
    imhist,bins = histogram(img.flatten(),nbr_bins,normed=True)
    cdf = imhist.cumsum() #cumulative distribution function
    cdf = 255 * cdf / cdf[-1] #normalize

    # use linear interpolation of cdf to find new pixel values
    im2 = interp(img.flatten(),bins[:-1],cdf)
    return im2.reshape(img.shape), cdf


'''
Compute the average of a list of images
-Returns an numpy array
'''
def compute_average(imglist):
    #open first image and make into array of type float
    averageimg = array(Image.open(imglist[0]),'f')

    for imgname in imgist[1:]:
        try:
            averageim += array(Image.open(imgname))
        except:
            print imgname + '...skipped'
    averageimg /= len(imglist)

    #return average as uint8
    return array(averageimg,'uint8')


'''
Display a PIL image in a new figure with a title
'''
def img_display(img,display='Image'):
    figure()
    title(display)
    gray()
    imshow(img,origin='lower')
    axis('off')


'''
Convert a PIL image to a numpy array
-Returns a numpy array
'''
def img_toArr(img):
    return array(img.convert('L'))


'''
Convert a numpy array to a PIL image
-Returns a PIL image
'''
def img_fromArr(arr):
    return Image.fromarray(arr)


'''
Returns a new image that appends the two images side-by-side
-Input and output are PIL images
'''
def appendimages(im1,im2):
    # select the image with the fewest rows and fill in enough empty rows
    rows1 = im1.shape[0]
    rows2 = im2.shape[0]
    if rows1 < rows2:
        im1 = concatenate((im1,zeros((rows2-rows1,im1.shape[1]))),axis=0)
    elif rows1 > rows2:
        im2 = concatenate((im2,zeros((rows1-rows2,im2.shape[1]))),axis=0)
    # if none of these cases they are equal, no filling needed.
    return concatenate((im1,im2), axis=1)


