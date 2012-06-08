import os
from PIL import Image
from matplotlib import pyplot as plt
import numpy as npy

import imtools
import sift


wing = 'wing006'
numTop = 10


#Load the template wing key
stdLoc,stdDesc = sift.feature_load('ignore/wingscale/keys/'+wing+'.key')


#Create an array to count how many times each feature appears
featureCount = stdDesc.shape[0]
stdMatches = npy.zeros((featureCount,1),'int')


#Iterate over a list of every key file
files = imtools.get_filelist('ignore/wingscale/keys/','.key')
count = len(files)
for f in files:
    #Load in the next key and match it with the template
    loc,desc = sift.feature_load(f)
    matches = sift.match_find(stdDesc,desc)
    #Add to the template counter array
    for indx,val in enumerate(matches):
        if val != 0: stdMatches[indx,0] += 1
    #Update progress
    count -= 1
    print 'Remaining: '+str(count)


#Find the features that occur most often
top = npy.zeros([numTop,2],'int')
for indx,val in enumerate(stdMatches):
    for j in xrange(numTop-1,0,-1):
        if val > top[j,1]:
            for k in xrange(0,j):
                top[k,0] = top[k+1,0] #keypoint index
                top[k,1] = top[k+1,1] #number of matches
            top[j,0] = indx
            top[j,1] = val
            break


#print out the top n features
top = top[::-1]
print 'ID | matches'
for i,j in top: print str(i)+' | '+str(j)


#Plot the feature frequencies on a histogram
x = npy.arange(0,featureCount,1)
y = stdMatches
fig = plt.figure()
plt.title("Keypoint matches")
axis = fig.add_subplot(1,1,1)
axis.bar(x,y)
axis.set_xlabel('SIFT feature')
axis.set_ylabel('Frequency')


#Render the points on the master image
plt.figure()
plt.gray()
img = imtools.img_toArr(Image.open('ignore/wingscale/'+wing+'.tif'))
sift.feature_plot_subset(img,stdLoc,top[:,0])

plt.show()




