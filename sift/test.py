from PIL import Image
from matplotlib import pyplot as plt
import os

import imtools
import sift


obj = sift.SiftObject()
arr = imtools.img_toArr(Image.open('ignore/cham/frame1.png'))
arr = imtools.img_contrast(arr,2.5)

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

for i in range(1,40):
    print '----- Frame ',i,' -----'
    arr = imtools.img_toArr(Image.open('ignore/cham/frame'+str(i)+'.png'))
    arr = imtools.img_contrast(arr,2.5)
    obj.update(arr)
    obj.showInfo()
    obj.plot(arr)

exit()
