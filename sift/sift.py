import os, sys
from PIL import Image
from pylab import *
import imtools


class SiftObject:

    #Instance data members
    #keyCount:     (int) total number of keypoints associated with this object
    #location:     (numpy nx2 array) x,y position of each keypoint relative to
    #              the origin of the latest source image
    #scale:        (numpy nx1 array) size of each keypoint
    #angle:        (numpy nx1 array) angle in radians of each keypoint
    #descriptor:   (numpy nx128 array) keypoint descriptors (used for matching)
    #boxVector     (numpy nx2 array) radians, radius to original bounding box
    #              upper left-hand corner
    #matched:      (numpy nx1 array) True/False did this keypoint match to the
    #              source image last update
    #isVisible:    (bool) True/False were any keypoints matched in last update?
    #              If False, the object is briefly searched for. If False,
    #              no new keypoints will be learned
    #frameSearches:(int) how many times the current update frame has been
    #              searched for the object. If SiftObject.maxSearches is
    #              reached, then searching will end for the current frame
    #boundingBox:  (Python 1x4 list) x1,y1,x2,y2 of box surrounding every
    #              keypoint in last update, used to estimate object's position
    #origBox:      (Python 1x2 list) width,height describing original bounding
    #              box size
    #trust:        (numpy nx1 array) value 0.0-1.0 determined by how often a
    #              dynamically found keypoint has appeared. Once trust = 1.0,
    #              the keypoint is marked as trusted and is kept
    #trusted       (numpy nx1 array) True/False has this keypoint been matched
    #              enough times to be considered a stable part of the object

    #Percentage larger in side length the search box is than the bounding box
    searchBoxRatio = 1.25
    #Smallest bounding box side length
    minBoxLength = 20
    #SIFT parameters (suggested: edge 10, peak 5, ratio 0.7)
    siftParams = "--edge-thresh 10 --peak-thresh 5"
    distRatio = 0.7
    #Increase and decrease in trust when an untrusted keypoint is/is not matched
    trustMatch = 0.25
    trustNoMatch = 0.5
    #Maximum number of additional keypoint searches before giving up on a frame
    maxSearches = 4


    '''
    Initialize an empty instance. Used in object creation
    returns: new SiftObject instance
    '''
    def __init__(self):
        #Initialize it as empty with no trusted keypoints
        self.keyCount = 0
        self.location = zeros((self.keyCount,2))
        self.scale = zeros((self.keyCount))
        self.angle = zeros((self.keyCount))
        self.descriptor = zeros((self.keyCount,128))
        self.boxVector = zeros((self.keyCount,2))
        self.matched = zeros((self.keyCount),'bool')
        self.isVisible = False
        self.frameSearches = 0
        self.boundingBox = [0,0,SiftObject.minBoxLength,SiftObject.minBoxLength]
        self.origBox = self.boundingBox
        self.trust = zeros((self.keyCount))
        self.trusted = zeros((self.keyCount),'bool')
        self.position = zeros((3,2))
        self.velocity = zeros((2,2))
        self.acceleration = zeros((1,2))


    '''
    Print out diagnostic information about the instance
    returns: nothing
    '''
    def showInfo(self):
        print 'SiftObject diagnostics'
        print '  visible:    ',self.isVisible
        print '  position:   [',int(self.boundingBox[0]),',',int(self.boundingBox[1]),']'
        print '  keypoints:  ',self.keyCount,' (',len(self.trusted.nonzero()[0]),' trusted)'
        print '  matches:    ',len(self.matched.nonzero()[0]),' (',len((self.matched*self.trusted).nonzero()[0]),' trusted)'

    '''
    Empty the instance of all keypoint data
    returns: nothing
    '''
    def empty(self):
        #Empty out old data
        self.keyCount = 0
        self.location = zeros((self.keyCount,2))
        self.scale = zeros((self.keyCount))
        self.angle = zeros((self.keyCount))
        self.descriptor = zeros((self.keyCount,128))
        self.boxVector = zeros((self.keyCount,2))
        self.matched = zeros((self.keyCount),'bool')
        self.trusted = []
        self.isVisible = False
        self.frameSearches = 0
        self.boundingBox = [0,0,SiftObject.minBoxLength,SiftObject.minBoxLength]
        self.origBox = self.boundingBox
        self.trust = zeros((self.keyCount))
        self.trusted = zeros((self.keyCount),'bool')
        self.position = zeros((3,2))
        self.velocity = zeros((2,2))
        self.acceleration = zeros((1,2))


    '''
    Load in training keypoints. Any existing keypoints will be erased. All new
    keypoints are marked as trusted
    img: a numpy image array
    box: a Python list [x1,y1,x2,y2]. Forms a rectangle around the object to
    track
    returns: nothing
    '''
    def train(self,img,box):
        self.empty()
        #Ensure the box isn't too small
        if box[2]-box[0] < SiftObject.minBoxLength:
            diff = SiftObject.minBoxLength-(box[2]-box[0])
            box[0] -= diff/2.0
            box[2] += diff/2.0
        if box[3]-box[1] < SiftObject.minBoxLength:
            diff = SiftObject.minBoxLength-(box[3]-box[1])
            box[1] -= diff/2.0
            box[3] += diff/2.0
        #Convert, crop, and save the image
        img = imtools.img_fromArr(img).convert('L')
        img = img.crop((int(box[0]),int(box[1]),int(box[2]),int(box[3])))
        img.save('tmp.pgm')
        #Save SIFT data
        feature_save('tmp.pgm','tmp.key',params=SiftObject.siftParams)
        #Open the just-created key file and read SIFT data
        loc,desc = feature_load('tmp.key')
        os.remove('tmp.key')
        try:
            location = loc[:,0:2]
        except:
            print 'SiftObject: no keypoints found in training image'
            self.boundingBox = box
            return
        scale = loc[:,2]
        angle = loc[:,3]
        descriptor = array(desc)
        #Give the keypoint data over to the instance
        self.keyCount = location.shape[0]
        self.location = location
        self.location[:,0] += box[0]
        self.location[:,1] += box[1]
        self.scale = scale
        self.angle = angle
        self.descriptor = descriptor
        self.boxVector = zeros((self.keyCount,2))
        self.matched = ones((self.keyCount),'bool')
        self.isVisible = True
        self.frameSearches = 0
        self.trust = ones((self.keyCount))
        self.trusted = ones((self.keyCount),'bool')
        #Initialize the bounding box around the object
        self.boundingBox = box
        self.origBox = [box[2]-box[0],box[3]-box[1]]
        #Relate keypoints to the initial bounding box
        self.boxVector[:] = [-1,-1]
        self.relateKeypoints()
        #Initialize position used in backup prediction
        self.position[:] = self.boundingBox[0:2]


    '''
    Updates keypoint positions and trust and object's estimated position given
    an image, typically the next frame in a video sequence
    img: a numpy image array
    returns: nothing
    '''
    def update(self,img):
        self.frameSearches = 0
        self.updateKeypoints(img)
        while self.frameSearches != 0 and self.frameSearches < SiftObject.maxSearches:
            self.updateKeypoints(img)
        self.updateTrust()
        self.updateBoundingBox()
        self.relateKeypoints()
        self.updatePrediction(img.shape)


    '''
    Update the positions of keypoints according to the passed image. Matches
    existing keypoints to keypoints found in the specified image and creates
    new keypoints for those not matched
    img: a numpy image array
    returns: nothing
    '''
    def updateKeypoints(self,img):
        imgSize = img.shape
        #Convert the update image array to a PIL image
        img = imtools.img_fromArr(img).convert('L')
        #Crop and save the proper area(s) to search for keypoints in
        x,y,width,height,count = self.computeSearchBox(imgSize,self.frameSearches)
        #Have we searched the entire image?
        if count == 0:
            self.frameSearches = 0
            return
        loc = zeros((0,4))
        desc = zeros((0,128))
        for i in range(0,count):
            im = img.crop((int(x[i]),int(y[i]),int(x[i]+width[i]),int(y[i]+height[i])))
            im.save('tmp.pgm')
            #Create SIFT data from the new image file
            feature_save('tmp.pgm','tmp.key',params=SiftObject.siftParams)
            #Open the just-created key file
            locTemp,descTemp = feature_load('tmp.key')
            os.remove('tmp.key')
            #Are there any keypoints?
            try:
                locTemp[0,0] += 0
            except:
                #No keypoints in this area
                continue
            #Correct the position of keypoints
            for j in range(0,locTemp.shape[0]):
                locTemp[j,0] += x[i]
                locTemp[j,1] += y[i]
            loc = concatenate((loc,locTemp))
            desc = concatenate((desc,descTemp))
        #Format the SIFT data
        try:
            location = loc[:,0:2]
        except:
            print 'SiftObject: no keypoints found in update image'
            self.matched[:] = False
            self.updateTrust()
            return
        scale = loc[:,2]
        angle = loc[:,3]
        descriptor = array(desc)
        #Find matches between existing keypoints and update image
        matches = match_find(self.descriptor,descriptor,dist_ratio=SiftObject.distRatio)
        toAdd = range(0,location.shape[0])
        self.isVisible = False
        #For every exising keypoint that has a match, set its position to
        #the position of its new match in the search box. For every new
        #keypoint found within the search box, add it to the object for future
        #matching
        for i in range(0,self.keyCount):
            if matches[i] != 0:
                if self.trusted[i]: self.isVisible = True
                self.matched[i] = True
                #Update the position of this keypoint
                self.location[i,0] = location[matches[i],0]
                self.location[i,1] = location[matches[i],1]
                self.scale[i] = scale[matches[i]]
                self.angle[i] = angle[matches[i]]
                #This keypoint isn't new, so we need not create it
                toAdd[matches[i]] = 0
            elif matches[i] == 0:
                self.matched[i] = False
        #For every keypoint discovered and not matched, add it to the object's
        #list of untrusted keypoints to track. But only if the object is visible
        #so we know that the bounding box location is good
        if self.isVisible and self.frameSearches == 0:
            for i in toAdd:
                if i != 0:
                    #Create new keypoint
                    self.keyCount += 1
                    self.location = concatenate((self.location,array([[location[i,0],location[i,1]]])))
                    self.scale = concatenate((self.scale,array([scale[i]])))
                    self.angle = concatenate((self.angle,array([angle[i]])))
                    self.descriptor = concatenate((self.descriptor,array([descriptor[i]])))
                    self.boxVector = concatenate((self.boxVector,array([[0,0]])))
                    self.matched = concatenate((self.matched,array([True])))
                    self.trust = concatenate((self.trust,array([0.0])))
                    self.trusted = concatenate((self.trusted,array([False])))
                    #Mark that this keypoint has to be related to the bounding box
                    self.boxVector[self.keyCount-1,0] = -1
                    self.boxVector[self.keyCount-1,1] = -1
        #Are we done or do we need to search this frame again?
        if self.isVisible:
            self.frameSearches = 0
        else:
            self.frameSearches += 1


    '''
    Calculate the position and size of a bounding box surrounding and slightly
    larger than the current one to be used to search the newest update image.
    imgSize: Python 1x2 list [height,width] of update image
    lost: int specifying how many times the update image has been searched
    for keypoints to no avail (higher value -> more search boxes)
    returns: x[],y[],width[],height[],count of each box to crop and search for
    keypoints in. If the image has been entirely searched, count = 0
    '''
    def computeSearchBox(self,imgSize,lost):
        #Get the size and position of current bounding box
        x = self.boundingBox[0]
        y = self.boundingBox[1]
        width = self.boundingBox[2] - self.boundingBox[0]
        height = self.boundingBox[3] - self.boundingBox[1]
        #Calculate search box(es)
        bx = [];by = [];bw = [];bh = []
        count = 0
        if lost == 0:
            #Simply expand the current bounding box by a bit
            bx = [x - width*(SiftObject.searchBoxRatio-1)*0.5]
            by = [y - height*(SiftObject.searchBoxRatio-1)*0.5]
            bw = [width*SiftObject.searchBoxRatio]
            bh = [height*SiftObject.searchBoxRatio]
            count = 1
        else:
            #If we're searching for the object, incrementally expand the search
            #area and never search area that's already been searched
            #Check that we haven't searched for too long
            if (width*lost>imgSize[1]) or (height*lost>imgSize[0]):
                count = 0
                return bx,by,bw,bh,count
            #Make search boxes outlining the previosuly searched area
            for i in range(0,lost*2+1):
                #Top edge
                ix = x - width*lost + width*i;iy = y - height*lost
                bx.append(ix);by.append(iy);bw.append(width);bh.append(height)
                #Bottom edge
                ix = x - width*lost + width*i;iy = y + height*lost
                bx.append(ix);by.append(iy);bw.append(width);bh.append(height)
                count += 2
            for i in range(1,lost*2):
                #Left edge
                ix = x - width*lost;iy = y - height*lost + height*i
                bx.append(ix);by.append(iy);bw.append(width);bh.append(height)
                #Right edge
                ix = x + width*lost;iy = y - height*lost + height*i
                bx.append(ix);by.append(iy);bw.append(width);bh.append(height)
                count += 2
        #Ensure that the search box(es) is (are) within the image bounds
        for i in range(0,count):
            if bx[i] < 0: bx[i] = 0
            if by[i] < 0: by[i] = 0
            if bx[i]+bw[i] > imgSize[1]: bw[i] = imgSize[1]-bx[i]
            if by[i]+bh[i] > imgSize[0]: bh[i] = imgSize[0]-by[i]
        #Ensure that the search box(es) isn't (aren't) too small
        for i in range(0,count):
            if bw[i] < SiftObject.minBoxLength: bw[i] = SiftObject.minBoxLength
            if bh[i] < SiftObject.minBoxLength: bh[i] = SiftObject.minBoxLength
        return bx,by,bw,bh,count


    '''
    Determines where the bounding box should be positioned based on the position
    offset vectors of every trusted, matched keypoint
    returns: nothing
    '''
    def updateBoundingBox(self):
        #Were there trusted keypoints that matched the last update image?
        if self.isVisible:
            minX = 0;minY = 0;maxX = 0;maxY = 0
            count = 0
            #Position the bounding box using matched keypoints' relations to it
            for i in range(0,self.keyCount):
                if self.matched[i] and self.trusted[i]:
                    count += 1
                    minX += self.location[i,0] + self.boxVector[i,1]*math.cos(self.boxVector[i,0])
                    minY += self.location[i,1] + self.boxVector[i,1]*math.sin(self.boxVector[i,0])
            #Take the average
            if count > 0:
                minX /= float(count)
                minY /= float(count)
                maxX = minX + self.origBox[0]
                maxY = minY + self.origBox[1]
                self.boundingBox = [minX,minY,maxX,maxY]


    '''
    Calculates the offset vector from every new keypoint to the top-left corner
    of the bounding box for future bounding box positioning
    returns: nothing
    '''
    def relateKeypoints(self):
        if not self.isVisible: return
        #Look for keypoints previously marked as unrelated
        for i in range(0,self.keyCount):
            if self.boxVector[i,0] == -1 and self.boxVector[i,1] == -1:
                dx = self.boundingBox[0] - self.location[i,0]
                dy = self.boundingBox[1] - self.location[i,1]
                radius = (dx**2 + dy**2)**0.5
                radians = math.atan2(dy,dx)
                self.boxVector[i] = [radians,radius]


    '''
    Determines the trust level of keypoints based on the last update image, and
    handles any deleting or trusting of keypoints
    returns: nothing
    '''
    def updateTrust(self):
        toDelete = []
        #For each untrusted keypoint, decrease its trust if it wasn't matched in
        #the past update image or increase it if it was. Mark any with
        #exceptional trust/lack of trust to be trusted/deleted
        for i in range(0,self.keyCount):
            if not self.trusted[i]:
                if self.matched[i] and self.isVisible:
                    self.trust[i] += SiftObject.trustMatch
                    if self.trust[i] >= 1:
                        self.trusted[i] = True
                        self.trust[i] = 1.0
                else:
                    self.trust[i] -= SiftObject.trustNoMatch
                    if self.trust[i] <= 0:
                        toDelete.append(i)
        #Delete keypoints that have reached 0.0 trust
        for i in reversed(toDelete):
            self.keyCount -= 1
            self.location = delete(self.location,i,axis=0)
            self.scale = delete(self.scale,i,axis=0)
            self.angle = delete(self.angle,i,axis=0)
            self.descriptor = delete(self.descriptor,i,axis=0)
            self.boxVector = delete(self.boxVector,i,axis=0)
            self.matched = delete(self.matched,i,axis=0)
            self.trust = delete(self.trust,i,axis=0)
            self.trusted = delete(self.trusted,i,axis=0)


    def updatePrediction(self,imgSize):
        if self.isVisible:
            #Calculate from bounding box
            self.position[2] = self.position[1]
            self.position[1] = self.position[0]
            self.position[0] = self.boundingBox[:2]
            self.velocity[1] = self.velocity[0]
            self.velocity[0] = self.position[0] - self.position[1]
            self.acceleration = self.velocity[0] - self.velocity[1]
        else:
            #Extrapolate previous measurements
            self.position[2] = self.position[1]
            self.position[1] = self.position[0]
            self.position[0] += self.velocity[0]
            self.velocity[1] = self.velocity[0]
            #self.velocity[0] += self.acceleration
            self.velocity[0] *= 0.9
            #Ensure box didn't go off-screen
            if self.position[0,0] < 0:self.position[0,0] = 0
            if self.position[0,1] < 0:self.position[0,1] = 0
            if self.position[0,0] > imgSize[1]:self.position[0,0] = imgSize[1]
            if self.position[0,1] > imgSize[0]:self.position[0,1] = imgSize[0]
            #Use to move bounding box in hopes of finding object again
            self.boundingBox[0] += self.velocity[0,0]
            self.boundingBox[1] += self.velocity[0,1]
            self.boundingBox[2] += self.velocity[0,0]
            self.boundingBox[3] += self.velocity[0,1]


    '''
    Open a figure and show the object's bounding box and visible keypoints.
    Keypoints are red/yellow for trusted/untrusted, and the bounding box is
    blue/green for visible/searching
    img: a numpy image array
    returns: nothing
    '''
    def plot(self,img):
        #Show the image
        figure()
        gray()
        imshow(img)
        #Plot matched keypoints
        for i in range(0,self.keyCount):
            if self.matched[i]:
                if self.trusted[i]:
                    plot(self.location[i,0],self.location[i,1],'.r')
                else:
                    plot(self.location[i,0],self.location[i,1],'.y')
        #Plot the bounding box
        x1 = self.boundingBox[0];y1 = self.boundingBox[1]
        x2 = self.boundingBox[2];y2 = self.boundingBox[3]
        color = 'b'
        if self.isVisible == False: color = 'g'
        plot([x1,x2],[y1,y1],color)
        plot([x1,x2],[y2,y2],color)
        plot([x1,x1],[y1,y2],color)
        plot([x2,x2],[y1,y2],color)
        axis('off')
        show()




'''
Wrapper combining several functions into one. Use this to get the SIFT features
from a numpy image array.
-im: a numpy image array
-box: a list [x,y,width,height] of the image to crop out and analyze. If this is
specified, the x,y positions will be relative to the corner of the box and you
should use feature_shift() if you want global coordinates. If not specified, the
 whole image is used
-returns [x,y,scale,orientation in radians], [descriptors]
'''
def feature_getFromArr(im,box=None):
    imtools.img_fromArr(im).save('tmp.pgm')
    return feature_getFromImg('tmp.pgm',box)


'''
Wrapper combining several functions into one. Use this to get the SIFT features
from an image file.
-im: path to the image file
-box: a list [x,y,width,height] of the image to crop out and analyze. If this is
specified, the x,y positions will be relative to the corner of the box and you
should use feature_shift() if you want global coordinates. If not specified, the
 whole image is used
-returns [x,y,scale,orientation in radians], [descriptors]
'''
def feature_getFromImg(im,box=None):
    feature_save(im,'tmp.key',box)
    loc,desc = feature_load('tmp.key')
    os.remove('tmp.key')
    return loc,desc


'''
Process an image and save the results in a file. Each row contains the
coordinates, scale, and rotation angle(radians) for each interest point as the
first four values, followed by the 128 values of the corresponding descriptor
-box: if specified, the image is first cropped before being fed into SIFT.
 Box is a 4x1 list [x,y,width,height] describing the crop and the top-left
 corner of the image is the origin. Note that the saved x,y coordinates will
 be relative to the box, not the whole image.
'''
def feature_save(imagename,resultname,box=None,params="--edge-thresh 10 --peak-thresh 5"):
    #Did the call request the image to be cropped first?
    if box != None:
        im = Image.open(imagename).convert('L')
        grab = im.crop((box[0],box[1],box[0]+box[2],box[1]+box[3]))
        grab.save('tmp.pgm')
        imagename = 'tmp.pgm'
    #convert to a pgm file if it isn't already
    if os.path.splitext(imagename)[1] != '.pgm':
        im = Image.open(imagename).convert('L')
        im.save('tmp.pgm')
        imagename = 'tmp.pgm'
    #Hand it over to the OS-specific SIFT binary for processing
    command = os.getcwd()+os.path.sep+'vlfeat'+os.path.sep
    if sys.platform.startswith('linux'):
        command += 'glnx86'
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        command += 'win32'
    elif sys.platform == 'darwin':
        command += 'maci'
    else:
        print 'sift.py error: cannot identify your platform'
        return()
    command += os.path.sep
    os.system(command+'sift '+imagename+' --output='+resultname+' '+params)
    #Delete the temporary file we created
    if imagename == 'tmp.pgm': os.remove(imagename)


'''
Runs SIFT on every image in a folder and saves the key in a folder called 'keys'
-output: True = outputs a message for every file saved, False = no output
'''
def feature_save_all(folder,extension,output = False):
    #Make a 'keys' folder to save keys in
    if folder.endswith(os.path.sep): folder = folder[:-1]
    destination = folder+os.path.sep+'keys'+os.path.sep
    if os.path.isdir(destination) == False: os.mkdir(destination)
    #Iterate over a list of every desired image
    files = imtools.get_filelist(folder,extension)
    count = len(files)
    for f in files:
        #If the key doesn't already exist, compute and save it
        fname = os.path.basename(f).split('.')[0]+'.key'
        if os.path.isfile(destination+fname) == False:
            feature_save(f,destination+fname)
        if output:
            count = count - 1
            print 'Remaining: '+str(count)


'''
Read feature properties from a file and return a numpy array
-Returns [x,y,scale,orientation in radians], [descriptors]
'''
def feature_load(filename):
    f = loadtxt(filename)
    try:
        return f[:,:4],f[:,4:]
    except:
        #Are there no lines at all?
        if len(f) == 0:
            return zeros((2,132),'int')
        #Is there only one line?
        return zeros((2,132),'int') + f


'''
Shifts a location array over by a certain amount. Use this after getting SIFT
features from a cropped portion of an image and you want the x,y coordinates
to be global, not relative to the box. In that case, dx,dy should be the top-
left corner of the box.
-Returns loc with x,y shifted by dx,dy
'''
def feature_shift(loc,dx,dy):
    for i in range(0,loc.shape[0]):
        loc[i,0] += dx
        loc[i,1] += dy
    return loc


'''
For each descriptor in the first set, select its match in the second set
-desc1 and desc2 are descriptors from feature_load()
-indx: if specified, only the indexes from desc1 that appear in indx will be matched
-dist_ratio is the ratio of distances between nearest and second-nearest
 neighbors that can result in a match
-two_way: if true, then ensures that matches go both ways. Slower, but returns
 fewer false matches
-returns a desc1 length x 1 list [desc2 matching feature index or 0]
'''
def match_find(desc1,desc2,indx=None,dist_ratio=0.6,two_way=False):
    #Did the call request a two-way match find?
    if two_way == True:
        #Get matches both ways
        matches_12 = match_find(desc1,desc2)
        matches_21 = match_find(desc2,desc1)
        #Get non-zero indexes of matches_12
        ndx_12 = matches_12.nonzero()[0]
        #remove matches that don't go both ways
        for n in ndx_12:
            if matches_21[int(matches_12[n])] != n:
                #Single match, but not double match
                matches_12[n] = 0
        #Return the result
        return matches_12

    desc1 = array([d/linalg.norm(d) for d in desc1])
    desc2 = array([d/linalg.norm(d) for d in desc2])
    #Precompute matrix transpose
    desc2t = desc2.T
    #Initialize a number-of-keypoints x 1 matrix filled with 0's for the match
    #matrix and loop through each keypoint to find its match, if any
    if indx == None: indx = range(desc1.shape[0])
    matchscores = zeros((desc1.shape[0],1),'int')
    for i in indx:
        #vector of dot products
        try:
            dotprods = dot(desc1[i,:],desc2t) * 0.9999
        except:
            continue
        #inverse cosine and sort, return index for features in second image
        indx = argsort(arccos(dotprods))
        #check if nearest neighbor has angle less than dist_ratio times 2nd nearest
        if arccos(dotprods)[indx[0]] < dist_ratio * arccos(dotprods)[indx[1]]:
            #We have a match - store the index of the second keypoint
            matchscores[i] = int(indx[0])
    return matchscores


'''
Opposite of match_find(). Returns a list of indexes from desc1 that do not
have a match in desc2
-desc1 and desc2 are descriptors from feature_load()
-returns a desc1 length x 1 list [desc1 feature index with no match or 0]
'''
def match_subtract(desc1,desc2):
    matches = match_find(desc1,desc2)
    unique = zeros((desc1.shape[0],1),'int')
    for i,m in enumerate(matches):
        if m == 0:
            unique[i] = i
    return unique


'''
Display an image with features drawn on
-im is a numpy array of the image
-locs is a numpy array from feature_load()
-indx: nx1 numpy array. If passed, only features whose index is in indx are drawn
-circ: True = circles size of features drawn, False = point circles
'''
def feature_plot(im,locs,indx = None,circle=False):
    #helper function to draw big circles
    def draw_circle(pos,radius):
        #Make an array of values from 0 to 2*pi
        t = arange(0,1.01,0.01)*2*pi
        #Make two arrays containing the x and y coordinates of points on a
        #circle of radius 'radius' and add the keypoint's position
        x = radius*cos(t) + pos[0]
        y = radius*sin(t) + pos[1]
        #Plot them all
        plot(x,y,'red',alpha='0.75')
    gray()
    imshow(im)
    if circle:
        if indx == None:
            for p in locs:
                draw_circle(p[:2],p[2])
        else:
            for p in indx:
                draw_circle((locs[p,0],locs[p,1]),locs[p,2])
    else:
        if indx == None:
            plot(locs[:,0],locs[:,1],'.b')
        else:
            for p in indx:
                plot(locs[p,0],locs[p,1],'.b')
    axis('off')


'''
Shows a figure with lines joining the accepted matches
-im1,im2 are numpy arrays of the images
-locs1, locs2 are feature location lists from feature_load()
-matches is output from match() or match2()
'''
def match_plot(im1,im2,locs1,locs2,matches):
    #Append the two images together and render the result
    im3 = imtools.img_append(im1,im2)
    gray()
    imshow(im3)
    #Value to add to x-coordinate of keypoint location on second image
    width1 = im1.shape[1]
    #Go through each match
    for i,m in enumerate(matches):
        #Does i have a match?
        if m != 0:
            x1 = locs1[i,0]
            x2 = locs2[m,0]
            y1 = locs1[i,1]
            y2 = locs2[m,1]
            plot([x1,x2+width1],[y1,y2],'red',alpha='0.75')
    axis('off')









