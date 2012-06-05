from PIL import Image
from matplotlib import pyplot as plt

import imtools
import sift


imgname1 = 'images/pop.jpg'
imgname2 = 'images/pop7.jpg'


#Evaluate first image
print 'Training'
siftname1 = imgname1.split('.')[0]+'.sift'
img1 = Image.open(imgname1)
arr1 = imtools.img_toArr(img1)
sift.process_image(imgname1,siftname1)
loc1,desc1 = sift.read_features_from_file(siftname1)

#Evaluate second image
print 'Evaluating new scene'
siftname2 = imgname2.split('.')[0]+'.sift'
img2 = Image.open(imgname2)
arr2 = imtools.img_toArr(img2)
sift.process_image(imgname2,siftname2)
loc2,desc2 = sift.read_features_from_file(siftname2)


#Find matches between the two images
print 'Matching'
matches = sift.match2(desc1,desc2)


#Plot the matches
plt.figure(1)
plt.gray()
plt.title('SIFT feature matching')
plt.axis('off')
sift.plot_matches(arr1,arr2,loc1,loc2,matches)

#Plot the two original images with keypoints
plt.figure(2)
plt.gray()
plt.title(imgname1+' features')
sift.plot_features(imtools.img_toArr(img1),loc1,circle=True)
plt.figure(3)
plt.title(imgname2+' features')
plt.gray()
sift.plot_features(imtools.img_toArr(img2),loc2,circle=True)

plt.show()









