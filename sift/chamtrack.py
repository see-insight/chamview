from PIL import Image
from PIL import ImageEnhance
from matplotlib import pyplot as plt
import os
import numpy as npy

import imtools
import sift


#easier variable management
f1 = 0
f2 = 1
imgpath = [None] * 2
siftpath = [None] * 2
img = [None] * 2
arr = [None] * 2
loc = [None] * 2
desc = [None] * 2


imgpath[f1] = 'ignore/chamfull/cham.png'
imgpath[f2] = 'ignore/chamfull/frame30.png'


#Evaluate f1
print 'Training'
siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
img[f1] = Image.open(imgpath[f1])
arr[f1] = imtools.img_toArr(img[f1])
if os.path.isfile(siftpath[f1]) == False:
    sift.feature_save(imgpath[f1],siftpath[f1])
loc[f1],desc[f1] = sift.feature_load(siftpath[f1])


#Evaluate f2
print 'New frame'
siftpath[f2] = imgpath[f2].split('.')[0]+'.key'
img[f2] = Image.open(imgpath[f2])
arr[f2] = imtools.img_toArr(img[f2])
if os.path.isfile(siftpath[f2]) == False:
    sift.feature_save(imgpath[f2],siftpath[f2])
loc[f2],desc[f2] = sift.feature_load(siftpath[f2])


print "Matching"
indx = sift.match_find(desc[f1],desc[f2])


#Plot f1 features
plt.figure(2)
plt.gray()
plt.title('F1 features')
sift.feature_plot(arr[f1],loc[f1],circle=True)
#Plot f2 features
plt.figure(3)
plt.title('F2 features')
plt.gray()
sift.feature_plot(arr[f2],loc[f2],circle=True)


#Plot matching features
plt.figure(1)
plt.gray()
plt.title('Matching keypoints')
sift.match_plot(arr[f1],arr[f2],loc[f1],loc[f2],indx)


plt.show()



#Basic matching. Place after f2 evaluation
"""
print "Matching"
indx = sift.match_find(desc[f1],desc[f2])
#Plot matching features
plt.figure(1)
plt.gray()
plt.title('Matching keypoints')
sift.match_plot(arr[f1],arr[f2],loc[f1],loc[f2],indx)
"""


#Subtraction. Place after f2 evaluation. f1 is empty, f2 is with chameleon
"""
print "Subtracting"
indx = sift.match_subtract(desc[f2],desc[f1])
#Plot features unique to f2
plt.figure(1)
plt.gray()
plt.title('Unique features')
sift.feature_plot_subset(arr[f2],loc[f2],indx,circle=True)
"""


#Boxing test. Insert into f1 evaluation and set the box coordinates. The
#current coordinates are for frame30.png
"""
img[f1] = imtools.img_crop(img[f1],1220,120,800,440)
sift.feature_save_box(imgpath[f1],siftpath[f1],(1220,120,800,440))
"""


#Increase contrast. Insert into f1 evaluation
"""
enhancer = ImageEnhance.Contrast(img[f1])
img[f1] = enhancer.enhance(2.5)
arr[f1] = imtools.img_toArr(img[f1])
plt.figure()
plt.gray()
plt.imshow(arr[f1])
plt.axis('off')
plt.show()
exit()
"""


#Threshold test. Place between f1 and f2 evaluation
"""
im = img[f1].convert('RGBA')
data = npy.array(im)  #height x width x 4 numpy array
theshold = 0.8
for x in range(data.shape[0]):
    for y in range(data.shape[1]):
        pix = data[x,y]
        if (int(pix[0])+int(pix[1])+int(pix[2]))/3 > int(pix[1]) * theshold:
            pix[0] = 0
            pix[1] = 0
            pix[2] = 0
        data[x,y] = pix

plt.figure()
plt.imshow(data)
plt.axis('off')
plt.show()
exit()
"""












