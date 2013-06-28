import os
from PIL import Image
from matplotlib import pyplot as plt
import numpy as npy

import imtools
import sift


fileMaster = 'wing006'
dirImg = 'ignore/wingscale/'
dirKey = 'ignore/wingscale/keys/'
numTop = 10


#Load the template wing key
locMaster,descMaster = sift.feature_load(dirKey+fileMaster+'.key')
arrMaster = imtools.img_toArr(Image.open(dirImg+fileMaster+'.tif'))

#Create an array to count how many times each feature appears
matchCount = npy.zeros((descMaster.shape[0],1),'int')


#Iterate over a list of every key file
files = imtools.get_filelist(dirKey,'.key')
count = len(files)
for f in files:
    #Load in the next key and match it with the master
    locChild,descChild = sift.feature_load(f)
    matches = sift.match_find(descMaster,descChild,two_way=True)
    #Add to the master counter array
    for indx,val in enumerate(matches):
        if val != 0: matchCount[indx,0] += 1
    #Update progress
    count -= 1
    print 'Remaining: '+str(count)


#Find the top n features that occur most often
top = npy.zeros([numTop,2],'int')
for indx,val in enumerate(matchCount):
    for j in xrange(numTop-1,0,-1):
        if val > top[j,1]:
            for k in xrange(0,j):
                top[k,0] = top[k+1,0] #keypoint index
                top[k,1] = top[k+1,1] #number of matches
            top[j,0] = indx
            top[j,1] = val
            break

#Remove all other features that aren't in the top n
for indx,val in enumerate(matchCount):
    if not (indx in top[:,0]):
        locMaster[indx] = 0
        descMaster[indx] = 0
        matchCount[indx] = 0


#Render the points on the master image
plt.figure()
plt.gray()
plt.title('Top matches in master')
sift.feature_plot(arrMaster,locMaster,top[:,0])

#Plot the feature frequencies on a histogram
x = npy.arange(0,descMaster.shape[0],1)
y = matchCount
fig = plt.figure()
plt.title('Keypoint match frequencies')
axis = fig.add_subplot(1,1,1)
axis.bar(x,y)
axis.set_xlabel('SIFT keypoint')
axis.set_ylabel('Frequency')

plt.show()


#Iterate over a list of every image/key file
files = imtools.get_filelist(dirImg,'.tif')
for f in files:
    fileChild= f.split('.')[0].split(os.path.sep)[-1]
    #Load in the image
    arrChild = imtools.img_toArr(Image.open(f))
    #Load in the key and match it with the master
    locChild,descChild = sift.feature_load(dirKey+fileChild+'.key')
    matches = sift.match_find(descMaster,descChild,two_way=True)
    #Draw the matches
    plt.figure()
    plt.gray()
    plt.title('Top matches in '+fileChild)
    plt.axis('off')
    sift.match_plot(arrMaster,arrChild,locMaster,locChild,matches)
    plt.show()







