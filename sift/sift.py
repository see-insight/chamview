import os
from PIL import Image
from pylab import *
from scipy.ndimage import filters
import imtools


'''
Process an image and save the results in a file. Each row contains the
coordinates, scale, and rotation angle(radians) for each interest point as the
first four values, followed by the 128 values of the corresponding descriptor
'''
def process_image(imagename,resultname,params="--edge-thresh 10 --peak-thresh 5"):
    #convert to a pgm file
    im = Image.open(imagename).convert('L')
    im.save('tmp.pgm')
    imagename = 'tmp.pgm'
    #Hand it over to sift
    cmmd = str("sift "+imagename+" --output="+resultname+" "+params)
    os.system(cmmd)
    #Delete the temporary file
    os.remove(imagename)


'''
Read feature properties from a file and return a numpy array
-Returns [x,y,scale,orientation in radians], [descriptors]
'''
def read_features_from_file(filename):
    f = loadtxt(filename)
    return f[:,:4],f[:,4:]


'''
Display an image with features drawn on
-im is a numpy array of the image
-locs is a numpy array from read_features_from_file()
-circ: True = circles size of features drawn, False = point circles
'''
def plot_features(im,locs,circle=False):
    #helper function to draw big circles
    def draw_circle(c,r):
        t = arange(0,1.01,.01)*2*pi
        x = r*cos(t) + c[0]
        y = r*sin(t) + c[1]
        plot(x,y,'b',linewidth=2)
    imshow(im)
    if circle:
        for p in locs:
            draw_circle(p[:2],p[2])
    else:
        plot(locs[:,0],locs[:,1],'ob')
    axis('off')


'''
For each descriptor in the first set, select its match in the second set
-desc1 and desc2 are descriptors from read_features_from_file()
-returns a list of matching descriptor ID's
'''
def match(desc1,desc2):
    #Only keep matches in which the ratio of distances from the nearest
    #to the second nearest neighbor is less than distRatio
    dist_ratio=0.6
    #Do something
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
            #We have a match - store the ID of the second keypoint
            matchscores[i] = int(indx[0])
    return matchscores


'''
Two-sided symmetric version of match(). Produces fewer false matches
-desc1 and desc2 are descriptors from read_features_from_file()
-returns a list of matching descriptor ID's
'''
def match2(desc1,desc2):
    #Get matches both ways
    matches_12 = match(desc1,desc2)
    matches_21 = match(desc2,desc1)
    ndx_12 = matches_12.nonzero()[0]
    #remove matches that don't go both ways
    for n in ndx_12:
        if matches_21[int(matches_12[n])] != n:
            #Single match, but not double match
            matches_12[n] = 0
    return matches_12


'''
Shows a figure with lines joining the accepted matches
-im1,im2 are images as numpy arrays
-locs1, locs2 are feature locations from read_features_from_file()
-matchscores is output from match() or match2()
'''
def plot_matches(im1,im2,locs1,locs2,matchscores):
    #Append the two images together and render it
    im3 = imtools.appendimages(im1,im2)
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
            plot([x1,x2+width1],[y1,y2],'red',alpha='0.5')
    axis('off')









