from PIL import Image
from matplotlib import pyplot as plt
import os

import imtools
import sift


#used to reference arrays (lists)
scene = 0
f1 = 1
f2 = 2
imgpath = [None] * 3
siftpath = [None] * 3
img = [None] * 3
arr = [None] * 3
loc = [None] * 3
desc = [None] * 3


imgpath[scene] = 'ignore/chamscale/scene.png'
imgpath[f1] = 'ignore/chamscale/frame01.png'


#Evaluate empty scene
print 'Training'
siftpath[scene] = imgpath[scene].split('.')[0]+'.key'
img[scene] = Image.open(imgpath[scene])
arr[scene] = imtools.img_toArr(img[scene])
if os.path.isfile(siftpath[scene]) == False:
    sift.feature_save(imgpath[scene],siftpath[scene])
loc[scene],desc[scene] = sift.feature_load(siftpath[scene])

#Evaluate first frame
print 'First frame'
siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
img[f1] = Image.open(imgpath[f1])
arr[f1] = imtools.img_toArr(img[f1])
if os.path.isfile(siftpath[f1]) == False:
    sift.feature_save(imgpath[f1],siftpath[f1])
loc[f1],desc[f1] = sift.feature_load(siftpath[f1])


diff = sift.match_subtract(desc[f1],desc[scene])


#Plot features unique to f1
plt.figure(1)
plt.gray()
plt.title('Unique f1 features')
sift.diff_plot(arr[f1],loc[f1],diff)
#Plot the scene
plt.figure(2)
plt.gray()
plt.title('F1 features')
sift.feature_plot(arr[f1],loc[f1])
#Plot f1 features
plt.figure(3)
plt.title('Scene features')
plt.gray()
sift.feature_plot(arr[scene],loc[scene])

plt.show()










