import os
from PIL import Image
from pylab import *
from scipy.ndimage import filters


#args: absolute path to folder (string), file extension including the '.' (string)
#returns: list of absolute paths to files in the folder with that extension (list of strings)
def get_filelist(path,extension):
    files = []
    for f in os.listdir(path):
        if f.endswith(extension):
            files.append(os.path.join(path,f))
    return files


#Note that this crops with the origin in the top-left corner
#args: image to crop (numpy array), x,y,width,height of new image (ints)
#returns: cropped image (numpy array)
def img_crop(img,x,y,width,height):
    return img.crop((x,y,x+width,y+height))


#args: image to convert (PIL image)
#returns: converted image (numpy array)
def img_toArr(img):
    return array(img.convert('L'))


#args: image to convert (numpy array)
#returns: converted image (PIL image)
def img_fromArr(arr):
    return Image.fromarray(arr)


#args: two images to make into one (numpy arrays)
#returns: im1 appended to the left of im2 (numpy array)
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


