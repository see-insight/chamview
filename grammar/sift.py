from Grammar import Predictor
from numpy import *
import os, sys
from PIL import Image, ImageEnhance
from pylab import *


class Sift(Predictor):
    """Wrap multiple SiftObject's to predict points for a Chamview Chooser

    Attributes:
        contrastAdd:   (float) amount of contrast added to images before sending
                       sending them to SiftObject. Makes feature extraction
                       perform better, to an extent. Suggested value: around 3.5
        obj:           (1xn list of SiftObject's) holds a pointer to each
                       instance of SiftObject, one per ImageStack point kind
        prediction:    (numpy nxmx3 array) used to pass information between
                       prediction functions. Holds [pointkind,frame,x/y/conf]
    """

    def setup(self,stack):
        """Called before anything else. Create a SiftObject instances
        -stack:   properly initialized ImageStack
        returns:  numpy 0-array representing "no guess"
        """
        #Add contrast to image frames to make keypoint detection easier
        self.contrastAdd = 3.5
        #Create one SiftObject for each point kind in the stack
        self.obj = []
        for i in range(0,stack.point_kinds):
            self.obj.append(SiftObject())
        #Used to pass info from getPointPrediction() to predict()
        self.prediction = zeros([stack.total_frames,stack.point_kinds,3])
        #Don't return an initial guess (we can't make one)
        return array([0,0,0])

    def teardown(self):
        """Last function called before program termination. Do nothing
        returns:  nothing
        """
        pass

    def predict(self,stack):
        """Called on every image frame. SiftObjects predict point positions
        -stack:   properly initialized ImageStack using this Predictor
        returns:  numpy array [point kind,row/column/confidence]
        """
        #Pre-compute a contrast-enhanced numpy array from the current image
        #frame so every point prediction doesn't have to, saving time
        arr = img_contrast(img_toArr(stack.img_current),self.contrastAdd)
        try:
            #Get a prediction for each different point kind in this frame
            for pointKind in range(0,stack.point_kinds):
                self.getPointPrediction(stack,arr,pointKind)
            #Return the prediction for every point kind for this frame
            result = zeros([stack.point_kinds,3])
            for pointKind in range(0,stack.point_kinds):
                result[pointKind,0] = self.prediction[stack.current_frame,pointKind,0]
                result[pointKind,1] = self.prediction[stack.current_frame,pointKind,1]
                result[pointKind,2] = self.prediction[stack.current_frame,pointKind,2]
        except IndexError:
            result = self.setup(stack)
        return result

    def getPointPrediction(self,stack,arr,pointKind):
        """If there isn't a prediction for the current frame, calculate it
        -stack:      properly initialized ImageStack using this Predictor
        -arr:        numpy array representing the current image to analyze
        -pointKind:  the point kind to predict
        returns:     nothing
        """
        #Get the SiftObject that tracks this point kind
        obj = self.obj[pointKind]
        #Train the SiftObject if it hasn't already been so
        if obj.key_count == 0:
            #Look for the initial ground-truth point to reference
            x = stack.point[0,pointKind,0]
            y = stack.point[0,pointKind,1]
            if x == 0 and y == 0: return
            #Train the object with a 75x75 box surrounding this point
            size = 75
            obj.train(arr,[x-size/2.0,
                y-size/2.0,x+size/2.0,y+size/2.0])
            #Set the prediction to be this point since it's ground-truth
            self.prediction[stack.current_frame,pointKind,0] = x
            self.prediction[stack.current_frame,pointKind,1] = y
            self.prediction[stack.current_frame,pointKind,2] = 1.0
        #Go back one frame and correct our previous prediction
        if stack.current_frame >= 2:
            #x,y is ground-truth point
            x = stack.point[stack.current_frame-1,pointKind,0]
            y = stack.point[stack.current_frame-1,pointKind,1]
            if x != 0 or y != 0:
                #Find the error between this SiftObject and the ground truth
                #and adjust for it
                dx = x - obj.position[0]
                dy = y - obj.position[1]
                obj.shift(dx,dy)
                #Realign keypoint-to-bounding box vectors
                for i in range(0,obj.key_count):
                    if obj.key_match[i]:
                        obj.key_vector[i,0] = -1
                        obj.key_vector[i,1] = -1
                obj.relate_keypoints()
        #Perform a feature search and store the predicted position of the object
        if stack.current_frame >= 1:
            obj.update(arr)
            #SiftObject doesn't have a confidence calculation at the moment,
            #so just assume a 50% confidence level
            x = obj.position[0];y = obj.position[1];conf = 0.5
            self.prediction[stack.current_frame,pointKind,0] = x
            self.prediction[stack.current_frame,pointKind,1] = y
            self.prediction[stack.current_frame,pointKind,2] = conf


class SiftObject:
    """Use local feature matching and reinforcement learning to track an object

    Attributes:
        key_count:   (int) total number of features associated with this object,
                     trusted and untrusted
        key_loc:     (numpy nx2 array) x,y position of each feature relative to
                     the origin of the latest update image
        key_scale:   (numpy nx1 array) size of each feature
        key_origscale:(numpy nx1 array) size of each feature when it was first
                     learned
        key_angle:   (numpy nx1 array) angle in radians of each feature
        key_desc:    (numpy nx128 array) feature descriptors (used for matching)
        key_vector   (numpy nx2 array) radians, radius to original bounding box
                     upper left-hand corner. Used for box positioning
        key_match:   (numpy nx1 array) True/False did this feature match to the
                     latest update image
        key_trust:   (numpy nx1 array) value 0.0-1.0 determined by how often a
                     dynamically found feature has appeared. Once trust == 1.0,
                     the feature is marked as trusted and is kept
        visible:     (bool) True/False were any features matched in last update?
                     If False, the object is searched for and no new features
                     will be learned
        scale:       (float) size of object compared to the first frame
        position:    (1x2 list) x,y position of center of the object
        boundingBox: (1x4 list) x1,y1,x2,y2 of box surrounding every feature
                     in last update, used to estimate object's position
        origSize:    (1x2 list) width,height describing original bounding box
                     size
        frameSearches:(int) how many times the current update frame has been
                      searched for the object. If SiftObject.maxSearches is
                      reached, then searching will end for the current frame
        predict_pos: (numpy 3x2 array) Actual or predicted position of the
                     object for the past three frames
        predict_vel: (numpy 2x2 array) Actual velocity of object for the past
                     two frames
        predict_accel: (numpy 1x2 array) Actual acceleration of object
    """

    #SIFT algorithm parameters. Playing with these for a given video can improve
    #performance. Suggested: edge 10, peak 5, distratio 0.8, twoway = False
    #edge: edge rejection, higher value -> more features
    #peak: minimum contrast to accept a feature, higher value -> fewer features
    #distratio: max distance between feature descriptors to match, higher value
    #-> more (but sometimes more erroneous) matches
    #twoway: if True, matches will be made both from old to new and new to old
    #update images. True -> more trustworthy but fewer matches
    sift_params = "--edge-thresh 10 --peak-thresh 6"
    sift_distratio = 0.8
    sift_twoway = False
    #Maximum number of additional feature searches before giving up on a frame
    search_max = 3
    #Percentage larger in side length the search box is than the bounding box
    search_boxratio = 1.25
    #Change in trust when an untrusted feature is/is not matched
    reinforce_pos = 0.2
    reinforce_neg = 0.3
    #shot_plot() rendering options
    plotUnmatched = False
    plotMatched = True

    def add_keypoints(self,toAdd,location,scale,angle,descriptor):
        '''Gather information about unmatched features to be used in learning
        -toAdd:       list of feature ID's to add, or 0 if it shouldn't be added
        -location:    list [x,y] of coordinates of features to add
        -scale:       list of scale of features to add
        -angle:       list of angle of features to add
        -descriptor:  list of descriptors of features to add
        returns:      nothing
        '''
        for i in toAdd:
            if i != 0:
                #If it's outside of the bounding box, don't keep it
                if ((self.boundingBox[0]<=location[i,0]<=self.boundingBox[2] and
                    self.boundingBox[1]<=location[i,1]<=self.boundingBox[3]) ==
                    False): continue
                #Create a new feature and add it the object's collection of
                #features known to be on the object to track
                self.key_count += 1
                self.key_loc = concatenate((self.key_loc,array([[location[i,0],
                                                              location[i,1]]])))
                self.key_scale = concatenate((self.key_scale,array([scale[i]])))
                self.key_origscale = concatenate((self.key_origscale,
                                                             array([scale[i]])))
                self.key_angle = concatenate((self.key_angle,array([angle[i]])))
                self.key_desc = concatenate((self.key_desc,
                                                        array([descriptor[i]])))
                self.key_vector = concatenate((self.key_vector,array([[0,0]])))
                self.key_match = concatenate((self.key_match,array([True])))
                self.key_trust = concatenate((self.key_trust,array([0.0])))
                #Mark that this feature has yet to be related to the bounding
                #box for future box positioning (self.relate_keypoints())
                self.key_vector[self.key_count-1,0] = -1
                self.key_vector[self.key_count-1,1] = -1

    def __init__(self):
        """Initialize the numpy arrays, etc necessary for a SiftObject instance
        Instance attributes are described in detail at the top of the class
        returns:  nothing
        """
        self.key_count = 0
        self.key_loc = zeros((self.key_count,2))
        self.key_scale = zeros((self.key_count))
        self.key_origscale = zeros((self.key_count))
        self.key_angle = zeros((self.key_count))
        self.key_desc = zeros((self.key_count,128))
        self.key_vector = zeros((self.key_count,2))
        self.key_match = zeros((self.key_count),'bool')
        self.key_trust = zeros((self.key_count))
        self.visible = False
        self.scale = 1.0
        self.position = [0,0]
        self.boundingBox = [0,0,50,50]
        self.origSize = self.boundingBox
        self.frameSearches = 0
        self.predict_pos = zeros((3,2))
        self.predict_vel = zeros((2,2))
        self.predict_accel = zeros((1,2))

    def update(self,img):
        """Main update code to be called with every subsequent update image
        -img:     numpy array representing an image
        returns:  nothing
        """
        #Search the image where the object is expected to be
        self.frameSearches = 0
        self.update_keypoints(img)
        #If no features were found, continue to search a few more times with
        #a gradually expanding view of the image
        while(self.frameSearches != 0 and self.frameSearches <
                                                        SiftObject.search_max):
            self.update_keypoints(img)
        #Learning and bounding box calculation
        self.update_trust()
        self.update_boundingbox()
        #Relate newly found features to the bounding box and update kinematics
        self.relate_keypoints()
        self.update_prediction(img.shape)

    def update_boundingbox(self):
        """Determine the position and size of a box surrounding the object
        returns:  nothing
        """
        #If the object is hidden/lost, don't attempt to find the bounding box
        if not self.visible: return
        #Properties of the box
        minX = 0;minY = 0;maxX = 0;maxY = 0
        scale = 0.0
        matchedFeatures = 0
        #Position the bounding box using matched features' relations to it
        for i in range(0,self.key_count):
            if self.key_match[i] and self.key_trust[i]==1:
                matchedFeatures += 1
                minX += self.key_loc[i,0] + self.key_vector[i,1]*math.cos(self.key_vector[i,0])
                minY += self.key_loc[i,1] + self.key_vector[i,1]*math.sin(self.key_vector[i,0])
                scale += self.key_scale[i] / self.key_origscale[i]
        #Take the average
        if matchedFeatures > 0:
            minX /= float(matchedFeatures)
            minY /= float(matchedFeatures)
            scale /= float(matchedFeatures)
            maxX = minX + self.origSize[0] * scale
            maxY = minY + self.origSize[1] * scale
            self.boundingBox = [minX,minY,maxX,maxY]
            self.scale = scale
            self.position[0] = (self.boundingBox[0]+self.boundingBox[2])/2.0
            self.position[1] = (self.boundingBox[1]+self.boundingBox[3])/2.0

    def update_keypoints(self,img):
        """Match known features in the image and learn new ones
        -img:     numpy array representing the next frame of the video
        returns:  nothing
        """
        imgSize = img.shape
        #Convert the update image array to a PIL image
        img = img_fromArr(img)
        #Crop and save the proper area(s) to search for features in
        x,y,width,height,count = self.update_searchbox(imgSize,
                                                             self.frameSearches)
        #If our search box is larger than the image itself, quit searching
        if count == 0:
            self.frameSearches = 0
            return
        #Info about features coming in from the new image
        loc = zeros((0,4))
        desc = zeros((0,128))
        #Go through each region (search box) computed earlier, save SIFT info
        #to file, load it back in, and add it to our list of SIFT features
        for i in range(0,count):
            im = img.crop((int(x[i]),int(y[i]),int(x[i]+width[i]),
                                               int(y[i]+height[i])))
            try:
                im.save('tmp.pgm')
            except SystemError:
                #Something or other bad happened
                print 'SiftObject: error in processing update image'
                return
            #Create SIFT data from this region in the new image
            feature_save('tmp.pgm','tmp.key',params=SiftObject.sift_params)
            #Open the just-created SIFT feature file
            locTemp,descTemp = feature_load('tmp.key')
            os.remove('tmp.key')
            #Are there any features?
            try:
                locTemp[0,0] += 0
            except IndexError:
                #No features in this selected region
                continue
            #Make the features' locations respect to the image rather than with
            #respect of their search box
            for j in range(0,locTemp.shape[0]):
                locTemp[j,0] += x[i]
                locTemp[j,1] += y[i]
            #Add these features to our list of features to match
            loc = concatenate((loc,locTemp))
            desc = concatenate((desc,descTemp))
        #Split the information up into multiple lists
        try:
            location = loc[:,0:2]
        except IndexError:
            print 'SiftObject: no features found in update image'
            self.key_match[:] = False
            self.update_trust()
            return
        scale = loc[:,2]
        angle = loc[:,3]
        descriptor = array(desc)
        #Find matches between existing features and the update image
        matches = match_find(self.key_desc,descriptor,
            dist_ratio = SiftObject.sift_distratio,
            two_way = SiftObject.sift_twoway)
        #Start off with the object not being visible and us needing to add every
        #feature found in the update image
        toAdd = range(0,location.shape[0])
        self.visible = False
        #For every exising feature that has a match, update its position in the
        #new video frame. For every feature found (possibly) on the object that
        #isn't already known, mark it to be added for future learning/matching
        for i in range(0,self.key_count):
            if matches[i] != 0:
                self.key_match[i] = True
                #This feature isn't new, so we need not create it
                toAdd[matches[i]] = 0
                #If we matched a trusted feature, then the object is assumed to
                #be visible
                if self.key_trust[i]==1.0: self.visible = True
                #Update the position, scale, and orientation of this feature
                self.key_loc[i,0] = location[matches[i],0]
                self.key_loc[i,1] = location[matches[i],1]
                self.key_scale[i] = scale[matches[i]]
                self.key_angle[i] = angle[matches[i]]
            elif matches[i] == 0:
                self.key_match[i] = False
        #If the object is visible, collect information about new features
        if self.visible and self.frameSearches == 0:
            self.add_keypoints(toAdd,location,scale,angle,descriptor)
        #If the object is not visible, we need to search this frame again
        if self.visible:
            self.frameSearches = 0
        else:
            self.frameSearches += 1

    def update_prediction(self,imgSize):
        """Use kinematics to estimate the object's position if it's lost
        -imgSize:  1x2 list [height,width] of the last update image
        returns:   nothing
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
            #Extrapolate previous position and velocity
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

    def update_searchbox(self,imgSize,lost):
        """Determine which region(s) of the image to search for features
        -imgSize:  1x2 list [height,width] of the image to search
        -lost:     int specifying how many times this image has been searched
                   already with no success. As this number increases, the number
                   of and area covered by search boxes increases
        returns:   x[],y[],width[],height[],count of each region to search and
                   how many search boxes there are
        """
        #Get the position of current bounding box
        x = self.boundingBox[0]
        y = self.boundingBox[1]
        width = 0
        height = 0
        #Look in the last known position of the object and increase the size of
        #the searchbox by a bit. bx,by,bw,bh are lists containing the properties
        #of the boxes to use for searching
        bx = [];by = [];bw = [];bh = []
        width = self.boundingBox[2] - self.boundingBox[0]
        height = self.boundingBox[3] - self.boundingBox[1]
        bx.append(x - width*(SiftObject.search_boxratio-1)*0.5)
        by.append(y - height*(SiftObject.search_boxratio-1)*0.5)
        bw.append(width*SiftObject.search_boxratio)
        bh.append(height*SiftObject.search_boxratio)
        count = 1
        #If the object is occluded/lost, also search in the predicted position
        if not self.visible:
            x = self.predict_pos[0,0]
            y = self.predict_pos[0,1]
            width = self.origSize[0]
            height = self.origSize[1]
            #Check that we our search area isn't exceptionally large
            if (width*lost>imgSize[1]) or (height*lost>imgSize[0]):
                count = 0;bx = [];by = [];bw = [];bh = []
                return bx,by,bw,bh,count
            #Calculate boxes surrounding the previously searched region, but not
            #including it (incremental searching; see research poster)
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

    def update_trust(self):
        """Perform reinforcement learning on known features
        returns:  nothing
        """
        #Keep a list of features to discard of
        toDelete = []

        #For each untrusted feature, decrease its trust if it wasn't matched in
        #the last update image or increase it if it was. Mark any with
        #exceptional trust/lack of trust to be trusted/deleted
        for i in range(0,self.key_count):
            if self.key_trust[i] != 1.0:
                #Only reward matched features if the object's location is known
                if self.key_match[i] and self.visible:
                    self.key_trust[i] += SiftObject.reinforce_pos
                    if self.key_trust[i] >= 1:
                        self.key_trust[i] = 1.0
                else:
                    self.key_trust[i] -= SiftObject.reinforce_neg
                    if self.visible == False: self.key_trust[i] = 0
                    if self.key_trust[i] <= 0:
                        toDelete.append(i)

        #Remove features that have reached 0.0 trust
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

    def relate_keypoints(self):
        """Calculate vector from new features to the box for future positioning
        returns:  nothing
        """
        if not self.visible: return
        #Look for features previously marked as unrelated
        for i in range(0,self.key_count):
            if self.key_vector[i,0] == -1 and self.key_vector[i,1] == -1:
                #Calculate the angle and distance between this feature and the
                #top-left corner of the box for use in future box positioning
                dx = self.boundingBox[0] - self.key_loc[i,0]
                dy = self.boundingBox[1] - self.key_loc[i,1]
                radius = (dx**2 + dy**2)**0.5
                radians = math.atan2(dy,dx)
                self.key_vector[i] = [radians,radius]

    def shift(self,dx,dy):
        """Shift everything over by some number of pixels
        returns:  nothing
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

    def show_info(self):
        """Print diagnostic information about the object
        returns:  nothing
        """
        #Count the number of known features and trusted features
        i = 0;j = 0
        for k in range(0,self.key_count):
            if self.key_trust[k] == 1.0:
                i += 1
                if self.key_match[k]:
                    j += 1
        print('SiftObject diagnostics')
        print('  visible:    ',self.visible)
        print('  position:   [',int(self.position[0]),',',
                                int(self.position[1]),']')
        print('  scale:      ',self.scale)
        print('  features:  ',self.key_count,' (',i,' trusted)')
        print('  matches:    ',len(self.key_match.nonzero()[0]),
                                ' (',j,' trusted)')

    def show_plot(self,img):
        """Open a window and display the object's bounding box and features
        Red/yellow features are trusted/untrusted and the bounding box is
        blue/green if the object's location is known/lost
        -img:     numpy array representing the image used in the last update
        returns:  nothing (opens a Matplotlib figure)
        """
        #Show the image in a new plot window
        figure()
        gray()
        imshow(img)
        #Draw matched features
        for i in range(0,self.key_count):
            if self.key_match[i]:
                #Is the feature trusted?
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
        #Make the window pop up
        axis('off')
        show()

    def train(self,img,box):
        """Learn initial feature information about the object to track
        -img:     numpy array representing the image to train from
        -box:     4x1 list [x1,y1,x2,y2] forming a rectangle around the object
                  to track in the image
        returns:  nothing
        """
        #Convert, crop, and save the region to track
        img = img_fromArr(img).convert('L')
        img = img.crop((int(box[0]),int(box[1]),int(box[2]),int(box[3])))
        img.save('tmp.pgm')
        #Save SIFT data from the region
        feature_save('tmp.pgm','tmp.key',params=SiftObject.sift_params)
        #Open the just-created feature file and read SIFT data
        loc,desc = feature_load('tmp.key')
        os.remove('tmp.key')
        try:
            loc[0,0] += 0
        except IndexError:
            print 'SiftObject: no features found in training image'
            self.boundingBox = box
            return
        location = loc[:,0:2]
        scale = loc[:,2]
        angle = loc[:,3]
        descriptor = array(desc)
        #Give the feature data over to the instance
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
        #All features found on the original object image are trusted
        self.key_trust = ones((self.key_count))
        #Initialize the bounding box around the object
        self.boundingBox = box
        self.origSize = [box[2]-box[0],box[3]-box[1]]
        #Relate features to the initial bounding box
        self.key_vector[:] = [-1,-1]
        self.relate_keypoints()
        #Initialize position used in backup kinematic prediction
        self.predict_pos[:] = self.boundingBox[0:2]
        #Other info
        self.scale = 1.0
        self.position[0] = (self.boundingBox[0]+self.boundingBox[2])/2.0
        self.position[1] = (self.boundingBox[1]+self.boundingBox[3])/2.0


def feature_load(filename):
    '''Read feature descriptors in from a file
    -filename:  string of path to file that was output by feature_save()
    returns:    numpy arrays [x,y,scale,orientation in radians], [descriptor]
    '''
    f = loadtxt(filename)
    try:
        return f[:,:4],f[:,4:]
    except IndexError:
        #Occurs when there are only 0 or 1 lines in the file
        if len(f) == 0:
            return zeros((2,132),'int')
        return zeros((2,132),'int') + f


def feature_save(imagename,resultname,box=None,params="--edge-thresh 10 --peak-thresh 5"):
    '''Process an image and save its features to file
    -imagename:   string of path to image file to read
    -resultname:  string of path to file to save results in
    -box:         if specified, a 4x1 list [x,y,width,height] to crop the image
                  to before processing. Top-left corner of image is the origin.
                  Note that saved x,y values will be relative to box, not image
    -params:      edge-thresh rejcts edges; higher value -> more features
                  peak is min contrast for feature; lower value -> more features
    returns:      Nothing
    '''
    #Did the call request the image to be cropped first? If so, crop it
    if box != None:
        im = Image.open(imagename).convert('L')
        grab = im.crop((box[0],box[1],box[0]+box[2],box[1]+box[3]))
        grab.save('tmp.pgm')
        imagename = 'tmp.pgm'
    #Convert the image to a pgm file if it isn't already
    if os.path.splitext(imagename)[1] != '.pgm':
        im = Image.open(imagename).convert('L')
        im.save('tmp.pgm')
        imagename = 'tmp.pgm'
    #Hand it over to the OS-specific SIFT binary for processing
    command = os.getcwd()+os.path.sep+'grammar'+os.path.sep+'vlfeat'+os.path.sep
    if sys.platform.startswith('linux'):
        command += 'glnx86'
    elif sys.platform == 'win32' or sys.platform == 'cygwin':
        command += 'win32'
    elif sys.platform == 'darwin':
        command += 'maci'
    else:
        #We're on an unsupported system
        print 'sift.py error: cannot identify your platform'
        return()
    command += os.path.sep
    os.system(command+'sift '+imagename+' --output='+resultname+' '+params)
    #Delete the temporary file we created
    if imagename == 'tmp.pgm': os.remove(imagename)


def img_contrast(img,value):
    '''Adjust the contrast in an image
    -img:     numpy array representing an image, from img_toArr()
    -value:   number > 0, a value of 1.0 does nothing
    returns:  numpy array representing an image
    '''
    enhancer = ImageEnhance.Contrast(img_fromArr(img))
    return img_toArr(enhancer.enhance(value))


def img_fromArr(arr):
    '''Convert a numpy array to a PIL image
    -arr:     numpy array representing an image
    returns:  PIL image
    '''
    return Image.fromarray(arr)


def img_toArr(img):
    '''Convert a PIL image to a numpy array
    -arr:     PIL image
    returns:  numpy array representing an image
    '''
    return array(img.convert('L'))


def match_find(desc1,desc2,indx=None,dist_ratio=0.6,two_way=False):
    '''For each feature in desc1, find its match in desc2
    -desc1:       numpy array of feature descriptors, feature_load() or similar
    -desc2:       numpy array of feature descriptors, feature_load() or similar
    -indx:        if specified, a numpy array desc1.length x 1. Only features
                  of desc1 whose index is marked as 1 in indx will be used in
                  the matching. Example: zeros() won't use any desc1 features
    -dist_ratio:  number, the max ratio between nearest and second-nearest
                  neighbors that results in a match. Larger value->more matches
    -two_way:     if specified, bool that determines if matches are made both
                  ways (slower and fewer matches, but more confidence)
    returns:      numpy array desc1.length x 1, each element containing either
                  the index of the matching desc2 feature or a 0
    '''
    #Did the call request a two-way match search?
    if two_way == True:
        #Get matches both ways
        matches_12 = match_find(desc1,desc2,indx=indx,dist_ratio=dist_ratio)
        matches_21 = match_find(desc2,desc1)
        #Remove matches that don't go both ways
        for i in matches_12:
            if i == 0: continue
            if matches_21[int(i)] != i:
                #Match in desc2 from desc1 but not the same in desc1 from desc2,
                #so we don't have a two-way match
                matches_12[i] = 0
        return matches_12

    #Preliminary math on feature descriptors
    desc1 = array([d/linalg.norm(d) for d in desc1])
    desc2 = array([d/linalg.norm(d) for d in desc2])
    desc2t = desc2.T
    #Initialize a desc1.length x 1 array filled with 0's for the match
    #matrix and loop through each feature to find its match, if any
    matchscores = zeros((desc1.shape[0],1),'int')
    if indx == None: indx = ones((desc1.shape[0],1),'int')
    for i in range(0,desc1.shape[0]):
        #Bug: somehow an index error sometimes slips in here
        try:
            if indx[i] == 0: continue
        except IndexError:
            continue
        #Bug: somehow desc1 and desc2 are sometimes not alligned
        try:
            dotprods = dot(desc1[i,:],desc2t) * 0.9999
        except ValueError:
            continue
        #Nearest-neighbor matching based on descriptor dot products
        ac = arccos(dotprods)
        indx = argsort(ac)
        if ac[indx[0]] < dist_ratio * ac[indx[1]]:
            #We have a match - store the index of the feature from desc2
            matchscores[i] = int(indx[0])
    return matchscores


def match_subtract(desc1,desc2):
    '''Find features that are present in desc1 but not in desc2
    -desc1:   numpy array of feature descriptors from feature_load() or similar
    -desc2:   numpy array of feature descriptors from feature_load() or similar
    returns:  numpy array desc1.length x 1, each index containing either a 1
              if the feature is unique or a 0 if a match was found in desc2
    '''
    #Create an array the length of desc1
    unique = zeros((desc1.shape[0],1),'int')
    matches = match_find(desc1,desc2)
    for i,m in enumerate(matches):
        if m == 0:
            #This feature index of desc1 (i) didn't match with any features in
            #desc2 so mark it as unique in our results
            unique[i] = 1
    return unique

