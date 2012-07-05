from PIL import Image
from matplotlib import pyplot as plt
import os

import imtools
import sift

directory = '../ignore/cham/'
frameStart = 1
frameEnd = 100
histeq = False
contrast = True
contrastAmount = 2.5

display = True
output = False

obj = sift.SiftObject()
arr = imtools.img_toArr(Image.open(directory+'frame'+
    str(frameStart).zfill(3)+'.png'))
if contrast: arr = imtools.img_contrast(arr,contrastAmount)
if histeq: arr = imtools.img_histeq(arr)

fig = plt.figure()
plt.gray()
plt.imshow(arr)
plt.axis('off')
try:
    pick = plt.ginput(1)
    plt.close()
    x0 = pick[0][0]
    y0 = pick[0][1]
except:
    #This is executed if the user closed the window without choosing points
    exit()

print 'Training'
size = 75
x0 = x0 - size/2.0
y0 = y0 - size/2.0
x1 = x0 + size
y1 = y0 + size
obj.train(arr,[x0,y0,x1,y1])
obj.show_info()

fileOut = None
if output:
    fileOut = open('siftPoints.txt','w')
    fileOut.write(str(int(obj.position[0])).zfill(4)+','+
        str(int(obj.position[1])).zfill(4)+'\n')

obj.show_plot(arr)

for i in range(frameStart+1,frameEnd+1):
    print '----- Frame ',i,' -----'
    arr = imtools.img_toArr(Image.open(directory+'frame'+str(i).zfill(3)+'.png'))
    if contrast: arr = imtools.img_contrast(arr,contrastAmount)
    if histeq: arr = imtools.img_histeq(arr)
    obj.update(arr)
    obj.show_info()
    if display:
        obj.show_plot(arr)
    if output:
        fileOut.write(str(int(obj.position[0])).zfill(4)+','+
            str(int(obj.position[1])).zfill(4)+'\n')

if output:
    fileOut.close()

exit()
