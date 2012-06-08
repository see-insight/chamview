import os, sys
from PIL import Image
from pylab import *
import imtools


'''
Process an image and save the results in a file. Each row contains the
coordinates, scale, and rotation angle(radians) for each interest point as the
first four values, followed by the 128 values of the corresponding descriptor
'''
def feature_save(imagename,resultname,params="--edge-thresh 10 --peak-thresh 5"):
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
Process an image and save the results in a file. Similar to feature_save, but
only analyzes a portion of the image
-box is a 4x1 list [x,y,width,height]
-the top-left corner of the image is the origin
'''
def feature_save_box(imagename,resultname,box,params="--edge-thresh 10 --peak-thresh 5"):
    #grab a portion of the image
    im = Image.open(imagename).convert('L')
    grab = im.crop((box[0],box[1],box[0]+box[2],box[1]+box[3]))
    grab.save('tmp.pgm')
    feature_save('tmp.pgm',resultname,params)


'''
Runs SIFT on every image in a folder and saves the key in a folder called 'keys'
-output: True = outputs for every file saved, False = no output
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
    return f[:,:4],f[:,4:]


'''
Display an image with features drawn on
-im is a numpy array of the image
-locs is a numpy array from feature_load()
-circ: True = circles size of features drawn, False = point circles
'''
def feature_plot(im,locs,circle=False):
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
    imshow(im)
    if circle:
        for p in locs:
            draw_circle(p[:2],p[2])
    else:
        plot(locs[:,0],locs[:,1],'ob')
    axis('off')


'''
Display an image with only the specified features drawn on
-im is a numpy array of the image
-locs is a numpy array from feature_load()
-indx is a numpy array containing the indexes of the keypoints to draw
-circ: True = circles size of features drawn, False = point circles
'''
def feature_plot_subset(im,locs,indx,circle=False):
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
    imshow(im)
    if circle:
        for p in indx:
            draw_circle((locs[p,0],locs[p,1]),locs[p,2])
    else:
        for p in indx:
            plot(locs[p,0],locs[p,1],'ob')
    axis('off')


'''
For each descriptor in the first set, select its match in the second set
-desc1 and desc2 are descriptors from feature_load()
-returns a desc1 length x 2 list [desc1 feature index, desc2 matching feature index or 0]
'''
def match_find(desc1,desc2,dist_ratio=0.6):
    #Only keep matches in which the ratio of distances from the nearest
    #to the second nearest neighbor is less than distRatio
    desc1 = array([d/linalg.norm(d) for d in desc1])
    desc2 = array([d/linalg.norm(d) for d in desc2])
    desc1_size = desc1.shape
    #Precompute matrix transpose
    desc2t = desc2.T
    #Initialize a number-of-keypoints x 1 matrix filled with 0's for the match
    #matrix and loop through each keypoint to find its match, if any
    matchscores = zeros((desc1_size[0],1),'int')
    for i in range(desc1_size[0]):
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
Two-sided symmetric version of match(). Produces fewer false matches
-desc1 and desc2 are descriptors from feature_load()
-returns a desc1 length x 2 list [desc1 feature index, desc2 matching feature index or 0]
'''
def match_find2(desc1,desc2):
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
    return matches_12


'''
Opposite of match_find(). Returns a 1D list of indexes from desc1 that do not
have a match in desc2
'''
def match_subtract(desc1,desc2):
    matches = match_find(desc1,desc2)
    unique = zeros((desc1.shape[0],1),'int')
    for i,m in enumerate(matches):
        if m == 0:
            unique[i] = i
    return unique


'''
Shows a figure with lines joining the accepted matches
-im1,im2 are images as numpy arrays
-locs1, locs2 are feature locations from feature_load()
-matchscores is output from match() or match2()
'''
def match_plot(im1,im2,locs1,locs2,matchscores):
    #Append the two images together and render it
    im3 = imtools.img_append(im1,im2)
    imshow(im3)
    #Value to add to x-coordinate of keypoint location on second image
    width1 = im1.shape[1]
    #Go through each match
    for i,m in enumerate(matchscores):
        #Does i have a match?
        if m != 0:
            x1 = locs1[i,0]
            x2 = locs2[m,0]
            y1 = locs1[i,1]
            y2 = locs2[m,1]
            plot([x1,x2+width1],[y1,y2],'red',alpha='0.75')
    axis('off')









