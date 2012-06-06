from PIL import Image
from matplotlib import pyplot as plt

import imtools
import sift


imgname1 = 'images/pop.jpg'
imgname2 = 'images/pop2.jpg'


#Evaluate first image
print 'Training'
siftname1 = imgname1.split('.')[0]+'.key'
img1 = Image.open(imgname1)
arr1 = imtools.img_toArr(img1)
sift.feature_save(imgname1,siftname1)
loc1,desc1 = sift.feature_load(siftname1)

#Evaluate second image
print 'Evaluating new scene'
siftname2 = imgname2.split('.')[0]+'.key'
img2 = Image.open(imgname2)
arr2 = imtools.img_toArr(img2)
sift.feature_save(imgname2,siftname2)
loc2,desc2 = sift.feature_load(siftname2)


#Find matches between the two images
print 'Matching'
matches = sift.match_find2(desc1,desc2)


#Plot the matches
plt.figure(1)
plt.gray()
plt.title('SIFT feature matching')
plt.axis('off')
sift.match_plot(arr1,arr2,loc1,loc2,matches)

#Plot the two original images with keypoints
plt.figure(2)
plt.gray()
plt.title(imgname1+' features')
sift.feature_plot(imtools.img_toArr(img1),loc1,circle=True)
plt.figure(3)
plt.title(imgname2+' features')
plt.gray()
sift.feature_plot(imtools.img_toArr(img2),loc2,circle=True)

plt.show()









