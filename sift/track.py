from PIL import Image
from matplotlib import pyplot as plt
import os

import imtools
import sift

directory = 'ignore/ball/'
frameStart = 400
frameEnd = 500
histeq = True
contrast = False
contrastAmount = 3.0

obj = sift.SiftObject()
arr = imtools.img_toArr(Image.open(directory+'frame'+str(frameStart).zfill(3)+'.png'))
if contrast: arr = imtools.img_contrast(arr,contrastAmount)
if histeq: arr = imtools.img_histeq(arr)

fig = plt.figure()
plt.gray()
plt.imshow(arr)
plt.axis('off')
try:
    pick = plt.ginput(2)
    plt.close()
except:
    #This is executed if the user closed the window without choosing points
    exit()

print 'Training'
obj.train(arr,[pick[0][0],pick[0][1],pick[1][0],pick[1][1]])
obj.showInfo()
obj.plot(arr)

for i in range(frameStart+1,frameEnd):
    print '----- Frame ',i,' -----'
    arr = imtools.img_toArr(Image.open(directory+'frame'+str(i).zfill(3)+'.png'))
    if contrast: arr = imtools.img_contrast(arr,contrastAmount)
    if histeq: arr = imtools.img_histeq(arr)
    obj.update(arr)
    obj.showInfo()
    obj.plot(arr)

exit()
