from PIL import Image
from PIL import ImageEnhance
from matplotlib import pyplot as plt
import os
import numpy as npy

import imtools
import sift

directory = 'ignore/cham/'
filezeros = 2
frameStart = 2
frameEnd = 63

#Load the first image
print 'Loading master frame '+str(frameStart)
img1 = imtools.img_toArr(Image.open(directory+'frame'+str(frameStart).zfill(filezeros)+'.png'))
enhancer = ImageEnhance.Contrast(imtools.img_fromArr(img1))
img1 = imtools.img_toArr(enhancer.enhance(2.5))
loc1,desc1 = sift.feature_getFromArr(img1)

#Plot image+keypoints and get user input (one click)
fig = plt.figure(1)
plt.gray()
sift.feature_plot(img1,loc1)
plt.title('Click on a keypoint to track')
plt.axis('image')
plt.axis('off')
pick = fig.ginput(1)
plt.close()
pickX = pick[0][0]
pickY = pick[0][1]

#Find keypoint closest to user's click
featureID = -1
featureDist = float('inf') #infinity
for i in range(0,loc1.shape[0]):
    dx = loc1[i,0]-pickX
    dy = loc1[i,1]-pickY
    if abs(dx) < 100 and abs(dy) < 100: #only look at close ones to save time
        dist = (dx**2 + dy**2)**0.5 #square root of squares
        if dist < featureDist:
            featureID = i
            featureDist = dist
if featureID == -1:
    print 'Error: please click closer to your desired keypoint'
    exit()
print 'You chose keypoint ['+str(featureID)+']'

#Update latest position
pointX = loc1[featureID,0]
pointY = loc1[featureID,1]
indx = [featureID]

#Track the point through subsequent frames
for i in range(frameStart+1,frameEnd):

    #Load in the next image
    img2 = imtools.img_toArr(Image.open(directory+'frame'+str(i).zfill(filezeros)+'.png'))
    enhancer = ImageEnhance.Contrast(imtools.img_fromArr(img2))
    img2 = imtools.img_toArr(enhancer.enhance(2.5))
    loc2,desc2 = sift.feature_getFromArr(img2,[int(pointX-100),int(pointY-100),200,200])
    loc2 = sift.feature_shift(loc2,pointX-100,pointY-100)

    #Find the next match
    match = sift.match_find(desc1,desc2,indx)

    #Update latest point info
    oldIndx = indx
    foundMatch = False
    try:
        matchID = match[match.nonzero()[0][0]]
        indx = [matchID[0]]
        pointX = loc2[matchID,0][0]
        pointY = loc2[matchID,1][0]
        print 'Match: '+str(matchID)+' - '+str(int(pointX))+','+str(int(pointY))
        foundMatch = True
        img1 = img2
        loc1 = loc2
        desc1 = desc2
    except:
        print 'No match found. Will use last known match as master'
        indx = oldIndx

    #Plot the point
    fig = plt.figure()
    if foundMatch: sift.feature_plot(img2,loc2,indx)
    if not foundMatch: sift.feature_plot(img2,loc2,[])
    plt.title('Frame ['+str(i)+']')
    plt.show()


















"""
#easier variable management
f1 = 0
f2 = 1
imgpath = [None] * 2
siftpath = [None] * 2
img = [None] * 2
arr = [None] * 2
loc = [None] * 2
desc = [None] * 2
"""

#Demo function displaying a simple match
def demoBasicMatch():
    imgpath[f1] = 'ignore/cham/cham.png'
    imgpath[f2] = 'ignore/cham/frame30.png'

    #Evaluate f1
    print 'Reading F1'
    siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
    img[f1] = Image.open(imgpath[f1])
    arr[f1] = imtools.img_toArr(img[f1])
    if True:#os.path.isfile(siftpath[f1]) == False:
        sift.feature_save(imgpath[f1],siftpath[f1])
    loc[f1],desc[f1] = sift.feature_load(siftpath[f1])

    #Evaluate f2
    print 'Reading F2'
    siftpath[f2] = imgpath[f2].split('.')[0]+'.key'
    img[f2] = Image.open(imgpath[f2])
    arr[f2] = imtools.img_toArr(img[f2])
    if True:#os.path.isfile(siftpath[f2]) == False:
        sift.feature_save(imgpath[f2],siftpath[f2])
    loc[f2],desc[f2] = sift.feature_load(siftpath[f2])

    print 'Matching'
    indx = sift.match_find(desc[f1],desc[f2])

    #Plot f1 features
    plt.figure(2)
    plt.gray()
    plt.title('F1 keypoints')
    sift.feature_plot(arr[f1],loc[f1],circle=True)
    #Plot f2 features
    plt.figure(3)
    plt.title('F2 keypoints')
    plt.gray()
    sift.feature_plot(arr[f2],loc[f2],circle=True)
    #Plot matching features
    plt.figure(1)
    plt.gray()
    plt.title('Keypoint matches')
    sift.match_plot(arr[f1],arr[f2],loc[f1],loc[f2],indx)

    plt.show()


#Demo function that tries to subtract the background from a new frame
def demoSubtractBackground():
    imgpath[f1] = 'ignore/cham/empty.png'
    imgpath[f2] = 'ignore/cham/frame30.png'

    #Evaluate f1
    print 'Reading F1'
    siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
    img[f1] = Image.open(imgpath[f1])
    arr[f1] = imtools.img_toArr(img[f1])
    if True:#os.path.isfile(siftpath[f1]) == False:
        sift.feature_save(imgpath[f1],siftpath[f1])
    loc[f1],desc[f1] = sift.feature_load(siftpath[f1])

    #Evaluate f2
    print 'Reading F2'
    siftpath[f2] = imgpath[f2].split('.')[0]+'.key'
    img[f2] = Image.open(imgpath[f2])
    arr[f2] = imtools.img_toArr(img[f2])
    if True:#os.path.isfile(siftpath[f2]) == False:
        sift.feature_save(imgpath[f2],siftpath[f2])
    loc[f2],desc[f2] = sift.feature_load(siftpath[f2])

    print "Subtracting"
    indx = sift.match_subtract(desc[f2],desc[f1])

    #Plot f1 features
    plt.figure(2)
    plt.gray()
    plt.title('F1 keypoints')
    sift.feature_plot(arr[f1],loc[f1],circle=True)
    #Plot f2 features
    plt.figure(3)
    plt.title('F2 keypoints')
    plt.gray()
    sift.feature_plot(arr[f2],loc[f2],circle=True)
    #Plot features unique to f2
    plt.figure(1)
    plt.gray()
    plt.title('F2 minus F1')
    sift.feature_plot(arr[f2],loc[f2],indx,circle=True)

    plt.show()


#Demo function that increases contrast then does basic matching
def demoContrastMatch():
    imgpath[f1] = 'ignore/cham/contrast1.png'
    imgpath[f2] = 'ignore/cham/contrast2.png'
    amount = 2.5

    #Evaluate f1
    print 'Reading F1'
    siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
    img[f1] = Image.open(imgpath[f1])
    arr[f1] = imtools.img_toArr(img[f1])
#    enhancer = ImageEnhance.Contrast(img[f1])
#     img[f1] = enhancer.enhance(amount)
#     arr[f1] = imtools.img_toArr(img[f1])
    if True:#os.path.isfile(siftpath[f1]) == False:
        sift.feature_save(imgpath[f1],siftpath[f1])
    loc[f1],desc[f1] = sift.feature_load(siftpath[f1])

    #Evaluate f2
    print 'Reading F2'
    siftpath[f2] = imgpath[f2].split('.')[0]+'.key'
    img[f2] = Image.open(imgpath[f2])
    arr[f2] = imtools.img_toArr(img[f2])
#    enhancer = ImageEnhance.Contrast(img[f2])
#    img[f2] = enhancer.enhance(amount)
#    arr[f2] = imtools.img_toArr(img[f2])
    if True:#os.path.isfile(siftpath[f2]) == False:
        sift.feature_save(imgpath[f2],siftpath[f2])
    loc[f2],desc[f2] = sift.feature_load(siftpath[f2])

    print 'Matching'
    indx = sift.match_find(desc[f1],desc[f2])

    #Plot f1 features
    plt.figure(2)
    plt.gray()
    plt.title('F1 keypoints')
    sift.feature_plot(arr[f1],loc[f1],circle=True)
    #Plot f2 features
    plt.figure(3)
    plt.title('F2 keypoints')
    plt.gray()
    sift.feature_plot(arr[f2],loc[f2],circle=True)
    #Plot matching features
    plt.figure(1)
    plt.gray()
    plt.title('Keypoint matches with '+str(int(amount*100))+'% increased contrast')
    sift.match_plot(arr[f1],arr[f2],loc[f1],loc[f2],indx)

    plt.show()


#Demo displaying a cropped cham image run through a threshold test
def demoThreshold():
    print 'Filtering'
    imgpath[f1] = 'ignore/cham/frame30.png'
    img[f1] = Image.open(imgpath[f1])
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
    plt.title('Threshold test')
    plt.axis('off')
    plt.show()


#Crop a box out of an image and match it
def demoBoxMatch():
    imgpath[f1] = 'ignore/cham/frame30.png'
    imgpath[f2] = 'ignore/cham/cham.png'

    #Evaluate f1
    print 'Reading F1'
    siftpath[f1] = imgpath[f1].split('.')[0]+'.key'
    img[f1] = Image.open(imgpath[f1])
    img[f1] = imtools.img_crop(img[f1],1220,120,800,440)
    arr[f1] = imtools.img_toArr(img[f1])
    if True:#os.path.isfile(siftpath[f1]) == False:
        sift.feature_save(imgpath[f1],siftpath[f1],(1220,120,800,440))
    loc[f1],desc[f1] = sift.feature_load(siftpath[f1])

    #Evaluate f2
    print 'Reading F2'
    siftpath[f2] = imgpath[f2].split('.')[0]+'.key'
    img[f2] = Image.open(imgpath[f2])
    arr[f2] = imtools.img_toArr(img[f2])
    if True:#os.path.isfile(siftpath[f2]) == False:
        sift.feature_save(imgpath[f2],siftpath[f2])
    loc[f2],desc[f2] = sift.feature_load(siftpath[f2])

    print 'Matching'
    indx = sift.match_find(desc[f1],desc[f2])

    #Plot f1 features
    plt.figure(2)
    plt.gray()
    plt.title('F1 keypoints')
    sift.feature_plot(arr[f1],loc[f1],circle=True)
    #Plot f2 features
    plt.figure(3)
    plt.title('F2 keypoints')
    plt.gray()
    sift.feature_plot(arr[f2],loc[f2],circle=True)
    #Plot matching features
    plt.figure(1)
    plt.gray()
    plt.title('Keypoint matches')
    sift.match_plot(arr[f1],arr[f2],loc[f1],loc[f2],indx)

    plt.show()






