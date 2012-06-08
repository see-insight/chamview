import os
from PIL import Image
from matplotlib import pyplot as plt
import numpy as npy

import imtools
import sift


#Load the template wing key
stdLoc,stdDesc = sift.feature_load('ignore/wingscale/keys/wing005.key')
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
    matches = matches.nonzero()
    for i in matches:
        stdMatches[i,0] += 1
    #Update progress
    count -= 1
    print 'Remaining: '+str(count)

#Plot the feature frequencies
x = npy.arange(0,featureCount,1)
y = stdMatches

fig = plt.figure()
plt.title("Keypoint matches")
axis = fig.add_subplot(1,1,1)
axis.bar(x,y)
axis.set_xlabel('SIFT feature')
axis.set_ylabel('Frequency')
plt.show()


