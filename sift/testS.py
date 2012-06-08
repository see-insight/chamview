from PIL import Image
from matplotlib import pyplot as plt
import os

import imtools
import sift


#used to reference arrays (lists)
f1 = 0
f2 = 1
imgpath = [None] * 2
siftpath = [None] * 2
img = [None] * 2
arr = [None] * 2
loc = [None] * 2
desc = [None] * 2


imgpath[f1] = 'ignore/test/pop.jpg'
imgpath[f2] = 'ignore/test/pop2.jpg'


#Evaluate first image
print imgpath[f1]
siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
img[f1] = Image.open(imgpath[f1])
arr[f1] = imtools.img_toArr(img[f1])
if os.path.isfile(siftpath[f1]) == False:
    sift.feature_save(imgpath[f1],siftpath[f1])
loc[f1],desc[f1] = sift.feature_load(siftpath[f1])


#Evaluate second image
print imgpath[f2]
siftpath[f2] = imgpath[f2].split('.')[0]+'.key'
img[f2] = Image.open(imgpath[f2])
arr[f2] = imtools.img_toArr(img[f2])
if os.path.isfile(siftpath[f2]) == False:
    sift.feature_save(imgpath[f2],siftpath[f2])
loc[f2],desc[f2] = sift.feature_load(siftpath[f2])


#Find matches between the two images
print 'Matching'
matches = sift.match_find(desc[f1],desc[f2])


#Plot the matches
plt.figure(1)
plt.gray()
plt.title('SIFT feature matching')
plt.axis('off')
sift.match_plot(arr[f1],arr[f2],loc[f1],loc[f2],matches)

#Plot the two original images with keypoints
plt.figure(2)
plt.gray()
plt.title(imgpath[f1]+' features')
sift.feature_plot(arr[f1],loc[f1],circle=True)
plt.figure(3)
plt.title(imgpath[f2]+' features')
plt.gray()
sift.feature_plot(arr[f2],loc[f2],circle=True)

plt.show()









