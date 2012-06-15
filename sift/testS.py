from PIL import Image
from matplotlib import pyplot as plt
import os

import imtools
import sift


obj = sift.SiftObject()
arr = imtools.img_toArr(Image.open('ignore/cham/frame30.png'))

fig = plt.figure()
plt.gray()
plt.imshow(arr)
plt.axis('off')
pick = plt.ginput(2)
plt.close()

print 'Training'
obj.train(arr,[pick[0][0],pick[0][1],pick[1][0],pick[1][1]])
obj.showInfo()
obj.plot(arr)

for i in range(31,35):
    print 'Frame ',i
    arr = imtools.img_toArr(Image.open('ignore/cham/frame'+str(i)+'.png'))
    obj.update(arr)
    obj.showInfo()
    obj.plot(arr)

exit()
