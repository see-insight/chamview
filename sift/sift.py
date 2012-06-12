import os, sys
from PIL import Image
from pylab import *
import imtools


'''
Wrapper combining several functions into one. Use this to get the SIFT features
from a numpy image array.
-im: a numpy image array
-box: a list [x,y,width,height] of the image to crop out and analyze. If this is
specified, the x,y positions will be relative to the corner of the box and you
should use feature_shift() if you want global coordinates. If not specified, the
 whole image is used
-returns [x,y,scale,orientation in radians], [descriptors]
'''
def feature_getFromArr(im,box=None):
    imtools.img_fromArr(im).save('tmp.pgm')
    feature_save('tmp.pgm','tmp.key',box)
    loc,desc = feature_load('tmp.key')
    os.remove('tmp.key')
    return loc,desc


'''
Wrapper combining several functions into one. Use this to get the SIFT features
from an image file.
-im: path to the image file
-box: a list [x,y,width,height] of the image to crop out and analyze. If this is
specified, the x,y positions will be relative to the corner of the box and you
should use feature_shift() if you want global coordinates. If not specified, the
 whole image is used
-returns [x,y,scale,orientation in radians], [descriptors]
'''
def feature_getFromImg(im,box=None):
    feature_save(im,'tmp.key',box)
    loc,desc = feature_load('tmp.key')
    os.remove('tmp.key')
    return loc,desc


'''
Process an image and save the results in a file. Each row contains the
coordinates, scale, and rotation angle(radians) for each interest point as the
first four values, followed by the 128 values of the corresponding descriptor
-box: if specified, the image is first cropped before being fed into SIFT.
 Box is a 4x1 list [x,y,width,height] describing the crop and the top-left
 corner of the image is the origin. Note that the saved x,y coordinates will
 be relative to the box, not the whole image.
'''
def feature_save(imagename,resultname,box=None,params="--edge-thresh 10 --peak-thresh 5"):
    #Did the call request the image to be cropped first?
    if box != None:
        im = Image.open(imagename).convert('L')
        grab = im.crop((box[0],box[1],box[0]+box[2],box[1]+box[3]))
        grab.save('tmp.pgm')
        imagename = 'tmp.pgm'
    #convert to a pgm file if it isn't already
    if os.path.splitext(imagename)[1] != '.pgm':
        im = Image.open(imagename).convert('L')
        im.save('tmp.pgm')
        imagename = 'tmp.pgm'
    #Hand it over to the OS-specific SIFT binary for processing
    command = os.getcwd()+os.path.sep+'vlfeat'+os.path.sep
    if sys.platform.startswith('linux'):
        command += 'glnx86'
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        command += 'win32'
    elif sys.platform == 'darwin':
        command += 'maci'
    else:
        print 'sift.py error: cannot identify your platform'
        return()
    command += os.path.sep
    os.system(command+'sift '+imagename+' --output='+resultname+' '+params)
    #Delete the temporary file we created
    if imagename == 'tmp.pgm': os.remove(imagename)


'''
Runs SIFT on every image in a folder and saves the key in a folder called 'keys'
-output: True = outputs a message for every file saved, False = no output
'''
def feature_save_all(folder,extension,output = False):
    #Make a 'keys' folder to save keys in
    if folder.endswith(os.path.sep): folder = folder[:-1]
    destination = folder+os.path.sep+'keys'+os.path.sep
    if os.path.isdir(destination) == False: os.mkdir(destination)
    #Iterate over a list of every desired image
    files = imtools.get_filelist(folder,extension)
    count = len(files)
    for f in files:
        #If the key doesn't already exist, compute and save it
        fname = os.path.basename(f).split('.')[0]+'.key'
        if os.path.isfile(destination+fname) == False:
            feature_save(f,destination+fname)
        if output:
            count = count - 1
            print 'Remaining: '+str(count)


'''
Read feature properties from a file and return a numpy array
-Returns [x,y,scale,orientation in radians], [descriptors]
'''
def feature_load(filename):
    f = loadtxt(filename)
    try:
        return f[:,:4],f[:,4:]
    except:
        #Are there no lines at all?
        if len(f) == 0:
            return zeros((2,132),'int')
        #Is there only one line?
        return zeros((2,132),'int') + f


'''
Shifts a location array over by a certain amount. Use this after getting SIFT
features from a cropped portion of an image and you want the x,y coordinates
to be global, not relative to the box. In that case, dx,dy should be the top-
left corner of the box.
-Returns loc with x,y shifted by dx,dy
'''
def feature_shift(loc,dx,dy):
    for i in range(0,loc.shape[0]):
        loc[i,0] += dx
        loc[i,1] += dy
    return loc


'''
For each descriptor in the first set, select its match in the second set
-desc1 and desc2 are descriptors from feature_load()
-indx: if specified, only the indexes from desc1 that appear in indx will be matched
-dist_ratio is the ratio of distances between nearest and second-nearest
 neighbors that can result in a match
-two_way: if true, then ensures that matches go both ways. Slower, but returns
 fewer false matches
-returns a desc1 length x 1 list [desc2 matching feature index or 0]
'''
def match_find(desc1,desc2,indx=None,dist_ratio=0.6,two_way=False):
    #Did the call request a two-way match find?
    if two_way == True:
        #Get matches both ways
        matches_12 = match_find(desc1,desc2)
        matches_21 = match_find(desc2,desc1)
        #Get non-zero indexes of matches_12
        ndx_12 = matches_12.nonzero()[0]
        #remove matches that don't go both ways
        for n in ndx_12:
            if matches_21[int(matches_12[n])] != n:
                #Single match, but not double match
                matches_12[n] = 0
        #Return the result
        return matches_12

    desc1 = array([d/linalg.norm(d) for d in desc1])
    desc2 = array([d/linalg.norm(d) for d in desc2])
    #Precompute matrix transpose
    desc2t = desc2.T
    #Initialize a number-of-keypoints x 1 matrix filled with 0's for the match
    #matrix and loop through each keypoint to find its match, if any
    if indx == None: indx = range(desc1.shape[0])
    matchscores = zeros((desc1.shape[0],1),'int')
    for i in indx:
        #vector of dot products
        dotprods = dot(desc1[i,:],desc2t) * 0.9999
        #inverse cosine and sort, return index for features in second image
        indx = argsort(arccos(dotprods))
        #check if nearest neighbor has angle less than dist_ratio times 2nd nearest
        if arccos(dotprods)[indx[0]] < dist_ratio * arccos(dotprods)[indx[1]]:
            #We have a match - store the index of the second keypoint
            matchscores[i] = int(indx[0])
    return matchscores


'''
Opposite of match_find(). Returns a list of indexes from desc1 that do not
have a match in desc2
-desc1 and desc2 are descriptors from feature_load()
-returns a desc1 length x 1 list [desc1 feature index with no match or 0]
'''
def match_subtract(desc1,desc2):
    matches = match_find(desc1,desc2)
    unique = zeros((desc1.shape[0],1),'int')
    for i,m in enumerate(matches):
        if m == 0:
            unique[i] = i
    return unique


'''
Display an image with features drawn on
-im is a numpy array of the image
-locs is a numpy array from feature_load()
-indx: nx1 numpy array. If passed, only features whose index is in indx are drawn
-circ: True = circles size of features drawn, False = point circles
'''
def feature_plot(im,locs,indx = None,circle=False):
    #helper function to draw big circles
    def draw_circle(pos,radius):
        #Make an array of values from 0 to 2*pi
        t = arange(0,1.01,0.01)*2*pi
        #Make two arrays containing the x and y coordinates of points on a
        #circle of radius 'radius' and add the keypoint's position
        x = radius*cos(t) + pos[0]
        y = radius*sin(t) + pos[1]
        #Plot them all
        plot(x,y,'red',alpha='0.75')
    gray()
    imshow(im)
    if circle:
        if indx == None:
            for p in locs:
                draw_circle(p[:2],p[2])
        else:
            for p in indx:
                draw_circle((locs[p,0],locs[p,1]),locs[p,2])
    else:
        if indx == None:
            plot(locs[:,0],locs[:,1],'.b')
        else:
            for p in indx:
                plot(locs[p,0],locs[p,1],'.b')
    axis('off')


'''
Shows a figure with lines joining the accepted matches
-im1,im2 are numpy arrays of the images
-locs1, locs2 are feature location lists from feature_load()
-matches is output from match() or match2()
'''
def match_plot(im1,im2,locs1,locs2,matches):
    #Append the two images together and render the result
    im3 = imtools.img_append(im1,im2)
    gray()
    imshow(im3)
    #Value to add to x-coordinate of keypoint location on second image
    width1 = im1.shape[1]
    #Go through each match
    for i,m in enumerate(matches):
        #Does i have a match?
        if m != 0:
            x1 = locs1[i,0]
            x2 = locs2[m,0]
            y1 = locs1[i,1]
            y2 = locs2[m,1]
            plot([x1,x2+width1],[y1,y2],'red',alpha='0.75')
    axis('off')









