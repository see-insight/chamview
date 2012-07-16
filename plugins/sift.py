from base import Predictor
from numpy import *
import os, sys
from PIL import Image, ImageEnhance
from pylab import *

#Note: Sift.setup(), Sift.teardown(), and Sift.predict() output info to a file,
#which is an unnecessary debugging hack (go ahead and remove it if you so wish)

class Sift(Predictor):

    def setup(self,stack):
        #Add contrast to image frames to make keypoint detection easier
        self.contrastAdd = 3.5
        #Create one SiftObject for each point kind in the stack
        self.obj = []
        for i in range(0,stack.point_kinds):
            self.obj.append(SiftObject())
        #Keep track of past predictions
        self.prediction = zeros([stack.total_frames,stack.point_kinds,3])
        #Hack: create a file to write debug info to
        self.fileOutA = open('plugins'+os.path.sep+'siftTrustedKeyCount.txt','w')
        self.fileOutB = open('plugins'+os.path.sep+'siftTrustedKeyMatch.txt','w')
        #Don't return an initial guess
        return array([0,0,0])

    def teardown(self):
        #Hack: close the debug info file
        self.fileOutA.close()
        self.fileOutB.close()
        pass

    def predict(self,stack):
        #Hack: output info to file
        trust = 0
        match = 0
        for i in range(0,self.obj[0].key_count):
            if self.obj[0].key_trust[i] == 1.0:
                trust += 1
                if self.obj[0].key_match[i]:
                    match += 1
        self.fileOutA.write(str(stack.current_frame).zfill(4)+','+str(trust)+'\n')
        self.fileOutB.write(str(stack.current_frame).zfill(4)+','+str(match)+'\n')
        #Create a contrast-enhanced numpy array from the current frame
        arr = img_contrast(img_toArr(stack.img_current),self.contrastAdd)
        #Get a prediction for each different point kind in this frame
        for pointKind in range(0,stack.point_kinds):
            self.getPointPrediction(stack,arr,pointKind)
        #Return the prediction for this frame
        result = zeros([stack.point_kinds,3])
        for pointKind in range(0,stack.point_kinds):
            result[pointKind,0] = self.prediction[stack.current_frame,pointKind,0]
            result[pointKind,1] = self.prediction[stack.current_frame,pointKind,1]
            result[pointKind,2] = self.prediction[stack.current_frame,pointKind,2]

        return result

    def getPointPrediction(self,stack,arr,pointKind):
        #Get the SiftObject that tracks this point kind
        obj = self.obj[pointKind]
        #Train Sift if this is the first frame. Otherwise, predict a point
        if stack.current_frame == 0:
            x = stack.point[0,pointKind,0]
            y = stack.point[0,pointKind,1]
            size = 75
            obj.train(arr,[x-size/2.0,
                y-size/2.0,x+size/2.0,y+size/2.0])
            self.prediction[stack.current_frame,pointKind,0] = x
            self.prediction[stack.current_frame,pointKind,1] = y
            self.prediction[stack.current_frame,pointKind,2] = 1.0
        else:
            if True:
                #Go back one frame and correct our previous prediction
                x = stack.point[stack.current_frame-1,pointKind,0]
                y = stack.point[stack.current_frame-1,pointKind,1]
                if x != 0 or y != 0:
                    #Find the error and adjust for it
                    dx = x - obj.position[0]
                    dy = y - obj.position[1]
                    obj.shift(dx,dy)

            if True:
                #Realign keypoint/bounding box vectors
                for i in range(0,obj.key_count):
                    if obj.key_match[i]:
                        obj.key_vector[i,0] = -1
                        obj.key_vector[i,1] = -1
                obj.relate_keypoints()

            #Perform a keypoint search and store the predicted position
            obj.update(arr)

            x = obj.position[0];y = obj.position[1];conf = 0.5
            self.prediction[stack.current_frame,pointKind,0] = x
            self.prediction[stack.current_frame,pointKind,1] = y
            self.prediction[stack.current_frame,pointKind,2] = conf
            dx = x - stack.point[stack.current_frame-1,pointKind,0]
            dy = y - stack.point[stack.current_frame-1,pointKind,1]


class SiftObject:

    """
    Use to track a particular object through a series of video frames.

    Attributes:
        key_count:   (int) total number of keypoints associated with this object
        key_loc:     (numpy nx2 array) x,y position of each keypoint relative to
                     the origin of the latest source image
        key_scale:   (numpy nx1 array) size of each keypoint
        key_origscale:
        key_angle:   (numpy nx1 array) angle in radians of each keypoint
        key_desc:    (numpy nx128 array) keypoint descriptors (used for matching)
        key_vector   (numpy nx2 array) radians, radius to original bounding box
                     upper left-hand corner
        key_match:   (numpy nx1 array) True/False did this keypoint match to the
                     source image last update
        key_trust:   (numpy nx1 array) value 0.0-1.0 determined by how often a
                     dynamically found keypoint has appeared. Once trust = 1.0,
                     the keypoint is marked as trusted and is kept
        visible:     (bool) True/False were any keypoints matched in last update?
                     If False, the object is briefly searched for. If False,
                     no new keypoints will be learned
        scale:
        position:
        boundingBox: (1x4 list) x1,y1,x2,y2 of box surrounding every keypoint
                     in last update, used to estimate object's position
        origSize:    (1x2 list) width,height describing original bounding box
                     size
        frameSearches:(int) how many times the current update frame has been
                      searched for the object. If SiftObject.maxSearches is
                      reached, then searching will end for the current frame
        predict_pos: (numpy 3x2 array) Actual or predicted position of bounding
                     box for the past three frames
        predict_vel: (numpy 2x2 array) Actual velocity of bounding box for the
                     past two frames
        predict_accel: (numpy 1x2 array) Actual acceleration of bounding box
    """

    #SIFT parameters (suggested: edge 10, peak 5, distratio 0.8)
    #edge: edge rejection, ^ -> more keypoints
    #peak: minimum contrast to accept a keypoint, ^ -> fewer keypoints
    #distratio: max distance between keypoint angles to match, ^ -> more matches
    sift_params = "--edge-thresh 10 --peak-thresh 6"
    sift_distratio = 1.0
    sift_twoway = False
    #Maximum number of additional keypoint searches before giving up on a frame
    search_max = 3
    #Percentage larger in side length the search box is than the bounding box
    search_boxratio = 1.25
    #Increase and decrease in trust when an untrusted keypoint is/is not matched
    reinforce_pos = 0.2
    reinforce_neg = 0.3
    #Smallest bounding box side length
    minBoxLength = 25
    #Rendering options
    plotUnmatched = False
    plotMatched = True

    def __init__(self):
        """
        Initialize a new empty SiftObject instance.
        -returns a new instance
        """
        self.key_count = 0
        self.key_loc = zeros((self.key_count,2))
        self.key_scale = zeros((self.key_count))
        self.key_origscale = zeros((self.key_count))
        self.key_angle = zeros((self.key_count))
        self.key_desc = zeros((self.key_count,128))
        self.key_vector = zeros((self.key_count,2))
        self.key_match = zeros((self.key_count),'bool')
        self.visible = False
        self.scale = 1.0
        self.position = [0,0]
        self.frameSearches = 0
        self.boundingBox = [0,0,SiftObject.minBoxLength,SiftObject.minBoxLength]
        self.origSize = self.boundingBox
        self.key_trust = zeros((self.key_count))
        self.predict_pos = zeros((3,2))
        self.predict_vel = zeros((2,2))
        self.predict_accel = zeros((1,2))

    def show_info(self):
        """
        Print diagnostic information about the object to the screen.
        -returns nothing
        """
        print 'SiftObject diagnostics'
        print '  visible:    ',self.visible
        print '  position:   [',int(self.position[0]),',',int(self.position[1]),']'
        print '  scale:      ',self.scale
        i = 0;j = 0
        for k in range(0,self.key_count):
            if self.key_trust[k] == 1.0:
                i += 1
                if self.key_match[k]:
                    j += 1
        print '  keypoints:  ',self.key_count,' (',i,' trusted)'
        print '  matches:    ',len(self.key_match.nonzero()[0]),' (',j,' trusted)'

    def train(self,img,box):
        """
        Learn initial keypoint information about the object to track.
        -img: numpy image array to train from
        -box: 1x4 list [x1,y1,x2,y2] forming a rectangle around object to track
        -returns nothing
        """
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
        img = img_fromArr(img).convert('L')
        img = img.crop((int(box[0]),int(box[1]),int(box[2]),int(box[3])))
        img.save('tmp.pgm')
        #Save SIFT data
        feature_save('tmp.pgm','tmp.key',params=SiftObject.sift_params)
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
        self.key_count = location.shape[0]
        self.key_loc = location
        self.key_loc[:,0] += box[0]
        self.key_loc[:,1] += box[1]
        self.key_scale = scale
        self.key_origscale = copy(scale)
        self.key_angle = angle
        self.key_desc = descriptor
        self.key_vector = zeros((self.key_count,2))
        self.key_match = ones((self.key_count),'bool')
        self.visible = True
        self.frameSearches = 0
        self.key_trust = ones((self.key_count))
        #Initialize the bounding box around the object
        self.boundingBox = box
        self.origSize = [box[2]-box[0],box[3]-box[1]]
        #Relate keypoints to the initial bounding box
        self.key_vector[:] = [-1,-1]
        self.relate_keypoints()
        #Initialize position used in backup prediction
        self.predict_pos[:] = self.boundingBox[0:2]
        #Other info
        self.scale = 1.0
        self.position[0] = (self.boundingBox[0]+self.boundingBox[2])/2.0
        self.position[1] = (self.boundingBox[1]+self.boundingBox[3])/2.0

    def update(self,img):
        """
        Main update code to be called with with subsequent video frame.
        -img: numpy image array
        -returns nothing
        """
        self.frameSearches = 0
        self.update_keypoints(img)
        while self.frameSearches != 0 and self.frameSearches < SiftObject.search_max:
            self.update_keypoints(img)
        self.update_trust()
        self.update_boundingbox()
        self.relate_keypoints()
        self.update_prediction(img.shape)

    def update_keypoints(self,img):
        """
        Match known keypoints to those found in the image and store their
        positions, as well as learn new keypoints in the bounding box.
        -img: numpy image array of the next frame in the video
        -returns nothing
        """
        imgSize = img.shape
        #Convert the update image array to a PIL image
        img = img_fromArr(img).convert('L')
        #Crop and save the proper area(s) to search for keypoints in
        x,y,width,height,count = self.update_searchbox(imgSize,self.frameSearches)
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
            feature_save('tmp.pgm','tmp.key',params=SiftObject.sift_params)
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
            self.key_match[:] = False
            self.update_trust()
            return
        scale = loc[:,2]
        angle = loc[:,3]
        descriptor = array(desc)
        #Find matches between existing keypoints and update image
        matches = match_find(self.key_desc,descriptor,
            dist_ratio = SiftObject.sift_distratio,
            two_way = SiftObject.sift_twoway)
        toAdd = range(0,location.shape[0])
        self.visible = False
        #For every exising keypoint that has a match, set its position to
        #the position of its new match in the search box. For every new
        #keypoint found within the bounding box, add it to the object for future
        #matching
        for i in range(0,self.key_count):
            if matches[i] != 0:
                if self.key_trust[i]==1.0: self.visible = True
                self.key_match[i] = True
                #Update the position of this keypoint
                self.key_loc[i,0] = location[matches[i],0]
                self.key_loc[i,1] = location[matches[i],1]
                self.key_scale[i] = scale[matches[i]]
                self.key_angle[i] = angle[matches[i]]
                #This keypoint isn't new, so we need not create it
                toAdd[matches[i]] = 0
            elif matches[i] == 0:
                self.key_match[i] = False
        #If the object is visible, gather new keypoints from the bounding box
        if self.visible and self.frameSearches == 0:
            self.add_keypoints(toAdd,location,scale,angle,descriptor)
        #Are we done or do we need to search this frame again?
        if self.visible:
            self.frameSearches = 0
        else:
            self.frameSearches += 1

    def add_keypoints(self,toAdd,location,scale,angle,descriptor):
        #For every keypoint within the bounding box discovered and not matched,
        #add it to the object's list of untrusted keypoints to track. But only
        #if the object is visible at this moment in time so we don't get bad
        #points that aren't actually on the object.
        for i in toAdd:
            if i != 0:
                #If it's outside of the bounding box, don't keep it
                if ((self.boundingBox[0] <= location[i,0] <= self.boundingBox[2] and
                    self.boundingBox[1] <= location[i,1] <= self.boundingBox[3]) ==
                    False): continue
                #Create new keypoint
                self.key_count += 1
                self.key_loc = concatenate((self.key_loc,array([[location[i,0],location[i,1]]])))
                self.key_scale = concatenate((self.key_scale,array([scale[i]])))
                self.key_origscale = concatenate((self.key_origscale,array([scale[i]])))
                self.key_angle = concatenate((self.key_angle,array([angle[i]])))
                self.key_desc = concatenate((self.key_desc,array([descriptor[i]])))
                self.key_vector = concatenate((self.key_vector,array([[0,0]])))
                self.key_match = concatenate((self.key_match,array([True])))
                self.key_trust = concatenate((self.key_trust,array([0.0])))
                #Mark that this keypoint has to be related to the bounding box
                self.key_vector[self.key_count-1,0] = -1
                self.key_vector[self.key_count-1,1] = -1

    def update_searchbox(self,imgSize,lost):
        """
        Calculate and return the position and size of each region in the image
        to search should the object be lost.
        -imgSize: 1x2 list [height,width] of the image to search
        -lost: int specifying how many times this image has been searched
         before with no success. Higher value -> more search boxes.
        -returns x[],y[],width[],height[],count of each region to search and
         how many there are. If the image has been entirely searched, count = 0.
        """
        #Get the size and position of current bounding box
        x = self.boundingBox[0]
        y = self.boundingBox[1]
        width = 0
        height = 0
        #Look in the last known position and expand the search box a bit
        bx = [];by = [];bw = [];bh = []
        width = self.boundingBox[2] - self.boundingBox[0]
        height = self.boundingBox[3] - self.boundingBox[1]
        bx.append(x - width*(SiftObject.search_boxratio-1)*0.5)
        by.append(y - height*(SiftObject.search_boxratio-1)*0.5)
        bw.append(width*SiftObject.search_boxratio)
        bh.append(height*SiftObject.search_boxratio)
        count = 1
        #If the box is lost, also search the predicted position
        if not self.visible:
            x = self.predict_pos[0,0]
            y = self.predict_pos[0,1]
            width = self.origSize[0]
            height = self.origSize[1]
            #If we're searching for the object, incrementally expand the search
            #area and never search area that's already been searched
            #Check that we haven't searched for too long
            if (width*lost>imgSize[1]) or (height*lost>imgSize[0]):
                count = 0;bx = [];by = [];bw = [];bh = []
                return bx,by,bw,bh,count
            #Make search boxes outlining the previously searched area
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
            if bx[i]+bw[i] > imgSize[1]: bx[i] = imgSize[1]-bw[i]
            if by[i]+bh[i] > imgSize[0]: by[i] = imgSize[0]-bh[i]
        return bx,by,bw,bh,count

    def update_boundingbox(self):
        """
        Determine the object's bounding box based on the previously calculated
        offset vectors of trusted keypoints.
        -returns: nothing
        """
        #Were there trusted keypoints that matched the last update image?
        if self.visible:
            minX = 0;minY = 0;maxX = 0;maxY = 0
            scale = 0.0
            count = 0
            #Position the bounding box using matched keypoints' relations to it
            for i in range(0,self.key_count):
                if self.key_match[i] and self.key_trust[i]==1:
                    count += 1
                    minX += self.key_loc[i,0] + self.key_vector[i,1]*math.cos(self.key_vector[i,0])
                    minY += self.key_loc[i,1] + self.key_vector[i,1]*math.sin(self.key_vector[i,0])
                    scale += self.key_scale[i] / self.key_origscale[i]
            #Take the average
            if count > 0:
                minX /= float(count)
                minY /= float(count)
                scale /= float(count)
                maxX = minX + self.origSize[0] * scale
                maxY = minY + self.origSize[1] * scale
                self.boundingBox = [minX,minY,maxX,maxY]
                self.scale = scale
                self.position[0] = (self.boundingBox[0]+self.boundingBox[2])/2.0
                self.position[1] = (self.boundingBox[1]+self.boundingBox[3])/2.0

    def shift(self,dx,dy):
        """
        Shift everything over by some number of pixels
        -returns: nothing
        """
        self.position[0] += dx
        self.position[1] += dy
        self.boundingBox[0] += dx
        self.boundingBox[1] += dy
        self.boundingBox[2] += dx
        self.boundingBox[3] += dy
        self.predict_pos[0] += array([dx,dy])
        self.predict_pos[1] += array([dx,dy])
        self.predict_pos[2] += array([dx,dy])

    def relate_keypoints(self):
        """
        Calculate the vector between new keypoints and the top-left corner of
        the bounding box for future box positioning.
        -returns nothing
        """
        if not self.visible: return
        #Look for keypoints previously marked as unrelated
        for i in range(0,self.key_count):
            if self.key_vector[i,0] == -1 and self.key_vector[i,1] == -1:
                #Calculate angle and distance, and store it
                dx = self.boundingBox[0] - self.key_loc[i,0]
                dy = self.boundingBox[1] - self.key_loc[i,1]
                radius = (dx**2 + dy**2)**0.5
                radians = math.atan2(dy,dx)
                self.key_vector[i] = [radians,radius]

    def update_trust(self):
        """
        Build trust in keypoints that appeared in this update and lose trust for
        those that didn't. Discard any with 0.0 trust and mark those that reach
        1.0 trust as usable for bounding box positioning.
        -returns nothing
        """
        toDelete = []
        #For each untrusted keypoint, decrease its trust if it wasn't matched in
        #the last update image or increase it if it was. Mark any with
        #exceptional trust/lack of trust to be trusted/deleted
        for i in range(0,self.key_count):
            if self.key_trust[i] != 1.0:
                if self.key_match[i] and self.visible:
                    self.key_trust[i] += SiftObject.reinforce_pos
                    if self.key_trust[i] >= 1:
                        self.key_trust[i] = 1.0
                else:
                    self.key_trust[i] -= SiftObject.reinforce_neg
                    if self.visible == False: self.key_trust[i] = 0
                    if self.key_trust[i] <= 0:
                        toDelete.append(i)
        #Delete keypoints that have reached 0.0 trust
        for i in reversed(toDelete):
            self.key_count -= 1
            self.key_loc = delete(self.key_loc,i,axis=0)
            self.key_scale = delete(self.key_scale,i,axis=0)
            self.key_origscale = delete(self.key_origscale,i,axis=0)
            self.key_angle = delete(self.key_angle,i,axis=0)
            self.key_desc = delete(self.key_desc,i,axis=0)
            self.key_vector = delete(self.key_vector,i,axis=0)
            self.key_match = delete(self.key_match,i,axis=0)
            self.key_trust = delete(self.key_trust,i,axis=0)

    def update_prediction(self,imgSize):
        """
        Use kinematics to estimate the object's position should it be lost.
        -imgSize: 1x2 list [height,width] of the last update image
        -returns nothing
        """
        if self.visible:
            #Calculate values from the current, matched bounding box
            self.predict_pos[2] = self.predict_pos[1]
            self.predict_pos[1] = self.predict_pos[0]
            self.predict_pos[0] = self.boundingBox[:2]
            self.predict_vel[1] = self.predict_vel[0]
            self.predict_vel[0] = self.predict_pos[0] - self.predict_pos[1]
            self.predict_accel = self.predict_vel[0] - self.predict_vel[1]
        else:
            #Extrapolate previous values
            self.predict_pos[0] += self.predict_vel[0]
            #self.predict_vel[0] += self.predict_accel
            self.predict_vel[0] *= 0.9 #hack: seems to work better
            #Ensure that the box didn't go off-screen
            if self.predict_pos[0,0] < 0:self.predict_pos[0,0] = 0
            if self.predict_pos[0,1] < 0:self.predict_pos[0,1] = 0
            if self.predict_pos[0,0]+self.origSize[0] > imgSize[1]:
                self.predict_pos[0,0] = imgSize[1]-self.origSize[0]
            if self.predict_pos[0,1]+self.origSize[1] > imgSize[0]:
                self.predict_pos[0,1] = imgSize[0]-self.origSize[1]

    def show_plot(self,img):
        """
        Open a figure and display the object's bounding box and keypoints. Red/
        yellow keypoints are trusted/untrusted, and the box is blue/green if
        visible/lost.
        -img: numpy image array used in last update
        -returns nothing
        """
        #Open the image in a new plot window
        figure()
        gray()
        imshow(img)
        #Draw matched keypoints
        for i in range(0,self.key_count):
            if self.key_match[i]:
                if self.key_trust[i] == 1.0:
                    if SiftObject.plotMatched:
                        plot(self.key_loc[i,0],self.key_loc[i,1],'.r')
                else:
                    if SiftObject.plotUnmatched:
                        plot(self.key_loc[i,0],self.key_loc[i,1],'.y')
        #Draw the bounding box
        x1 = self.boundingBox[0];y1 = self.boundingBox[1]
        x2 = self.boundingBox[2];y2 = self.boundingBox[3]
        color = 'b'
        if self.visible == False: color = 'g'
        plot([x1,x2],[y1,y1],color)
        plot([x1,x2],[y2,y2],color)
        plot([x1,x1],[y1,y2],color)
        plot([x2,x2],[y1,y2],color)
        #Draw the estimated center
        if self.visible: plot(self.position[0],self.position[1],'xb')
        axis('off')
        show()


def feature_save(imagename,resultname,box=None,params="--edge-thresh 10 --peak-thresh 5"):
    '''
    Process an image and save the results in a file. Each row contains the
    coordinates, scale, and rotation angle(radians) for each interest point as
    the first four values, followed by the 128 values of the corresponding
    descriptor
    -box: if specified, the image is first cropped before being fed into SIFT.
     Box is a 4x1 list [x,y,width,height] describing the crop and the top-left
     corner of the image is the origin. Note that the saved x,y coordinates will
     be relative to the box, not the whole image.
    '''
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
    command = os.getcwd()+os.path.sep+'plugins'+os.path.sep+'vlfeat'+os.path.sep
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


def feature_load(filename):
    '''
    Read feature properties from a file and return a numpy array
    -Returns [x,y,scale,orientation in radians], [descriptors]
    '''
    f = loadtxt(filename)
    try:
        return f[:,:4],f[:,4:]
    except:
        #Are there no lines at all?
        if len(f) == 0:
            return zeros((2,132),'int')
        #Is there only one line?
        return zeros((2,132),'int') + f


def match_find(desc1,desc2,indx=None,dist_ratio=0.6,two_way=False):
    '''
    For each descriptor in the first set, select its match in the second set
    -desc1 and desc2 are descriptors from feature_load()
    -indx: if specified, only the indexes from desc1 that appear in indx will be
     matched
    -dist_ratio is the ratio of distances between nearest and second-nearest
     neighbors that can result in a match
    -two_way: if true, then ensures that matches go both ways. Slower, but
     returns fewer false matches
    -returns a desc1 length x 1 list [desc2 matching feature index or 0]
    '''
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


def match_subtract(desc1,desc2):
    '''
    Opposite of match_find(). Returns a list of indexes from desc1 that do not
    have a match in desc2
    -desc1 and desc2 are descriptors from feature_load()
    -returns a desc1 length x 1 list [desc1 feature index with no match or 0]
    '''
    matches = match_find(desc1,desc2)
    unique = zeros((desc1.shape[0],1),'int')
    for i,m in enumerate(matches):
        if m == 0:
            unique[i] = i
    return unique


def img_toArr(img):
    return array(img.convert('L'))


def img_fromArr(arr):
    return Image.fromarray(arr)


def img_contrast(img,value):
    enhancer = ImageEnhance.Contrast(img_fromArr(img))
    return img_toArr(enhancer.enhance(value))
