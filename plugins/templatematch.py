from base import Predictor
from numpy import *
from skimage.feature import match_template

class TemplateMatch(Predictor):

    def setup(self,stack):
        #Create a Template instance for each point kind in the stack
        self.obj = []
        for i in range(0,stack.point_kinds):
            self.obj.append(Template())
        #Don't return an initial guess (X,Y,confidence)
        return array([0,0,0])

    def teardown(self):
        pass

    def predict(self,stack):
        #Convert the PIL image to a numpy array
        img = array(stack.img_current.convert('L'))
        #Get a prediction for each different point kind in this frame
        result = zeros([stack.point_kinds,3])
        for pointKind in range(0,stack.point_kinds):
            prediction = self.getPointPrediction(stack,img,pointKind)
            result[pointKind,0] = prediction[0] #X
            result[pointKind,1] = prediction[1] #Y
            result[pointKind,2] = prediction[2] #confidence
        #Return all the predictions for this frame
        return result

    def getPointPrediction(self,stack,img,pointKind):
        #Get the Template instance that tracks this point kind
        obj = self.obj[pointKind]
        #Have we looked at the image near the initial point yet?
        if obj.hasInitialPoint == False:
            x = stack.point[0,pointKind,0]
            y = stack.point[0,pointKind,1]
            #If the chooser hasn't selected an initial point yet, then we can't
            #do anything. Return no point with no confidence
            if x == 0 and y == 0:
                return [0,0,0]
            #Otherwise, tell this Template instance to search for this part
            #of the image in future predictions
            obj.train(img,x,y)
        #Find the point in the current image
        return obj.findPoint(img)


class Template:
    def __init__(self):
        self.hasInitialPoint = False

    def findPoint(self,img):
        #Find the XY coordinates of the point to track in img (a numpy array)
        result = match_template(img, self.template)
        ij = unravel_index(argmax(result), result.shape)
        x, y = ij[::-1]
        confidence = self.confidence(self.template)
        return [x,y,confidence]

    def train(self,img,x,y):
        #Look at the image at the specified position and grab the template there
        #to be used in future predictions. img is a numpy array
        size = 50
        bounds = [x-size/2, y-size/2, x+size/2, y+size/2]
        self.template = img[bounds[1]:bounds[3], bounds[0]:bounds[2]]
        
    def confidence(self, template):
        '''After thinking further, not a correct way of measuring confidence.
        Still needs revision.
        '''
        #Takes the sum of all pixel values, divides it by the area to find
        #average pixel value
        avg_val = sum(template)/template.size
        #Converts array into essentially 1 dimension so that 2 while loops
        #are not needed
        tmp_reshape = template.reshape(template.size)
        i = 0
        dev_sum = 0
        while i < template.size:
            #Sum of how much the pixel values deviate from the average
            dev_sum += abs(tmp_reshape[i]-avg_val)
            i+=1
        std_dev = float(dev_sum)/template.size/100
        #Confidence value from 0-1
        return 1-std_dev
