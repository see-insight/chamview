import os
from PIL import Image
from pylab import *
from scipy.ndimage import filters


'''
Creates a list of filenames of every image with a certain extension in a
directory
-path is a string absolute path to the folder
-extension is a string extension, including the '.' (ie '.jgg')
-returns a list
'''
def get_filelist(path,extension):
    files = []
    for f in os.listdir(path):
        if f.endswith(extension):
            files.append(os.path.join(path,f))
    return files


'''
Resize an image
-arr is a numpy array, size an integer
-returns a numpy array
'''
def img_resize(arr,size):
    img = Image.fromarray(uint8(arr))
    return array(img.resize(size))


'''
Convert a PIL image to a numpy array
-img is a PIL image
-returns a numpy array
'''
def img_toArr(img):
    return array(img.convert('L'))


'''
Convert a numpy array to a PIL image
-arr is a numpy array
-returns a PIL image
'''
def img_fromArr(arr):
    return Image.fromarray(arr)


'''
Returns a new image that appends the two images side-by-side. Any difference
in size is filled in with black
-im1, im2 are numpy arrays
-returns a numpy array
'''
def img_append(im1,im2):
    # select the image with the fewest rows and fill in enough empty rows
    rows1 = im1.shape[0]
    rows2 = im2.shape[0]
    if rows1 < rows2:
        im1 = concatenate((im1,zeros((rows2-rows1,im1.shape[1]))),axis=0)
    elif rows1 > rows2:
        im2 = concatenate((im2,zeros((rows1-rows2,im2.shape[1]))),axis=0)
    # if none of these cases they are equal, no filling needed.
    return concatenate((im1,im2), axis=1)


