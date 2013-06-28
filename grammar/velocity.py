from Grammar import Predictor
from numpy import *
from imagestack import ImageStack


class Velocity(Predictor):
	
    stack = ImageStack('./images/')
    def setup(self,stack):
        # set up variables self.p0, self.p1, self.p2
        self.p0 = [0,0]
        self.p1 = [0,0]
        self.p2 = [0,0] # not for predicting
	
    def teardown(self) :
	
        pass 
	
    def predict(self,stack,pointsEdited=False) :
		
        #initialize "results". Will be a two dimensional array of zeros with the number of rows dependent on the size of "stack.pointkind", and 3 columns
	result = zeros([stack.point_kinds,3])
			
	def getConfidence():
	    '''After thinking further, not a correct way of measuring confidence.
            Still needs revision.
            '''
	    return 0.5
	    
			
	for i in range(0,stack.point_kinds):
	# this loop runs for every point kind.
			
            if stack.current_frame >= 1:
	    #gets points on previous 3 frames, then predicts a point on the current frame
				
                self.p2 = [0,0]
		self.p2[0] = stack.point[ stack.current_frame,i,0 ]
		self.p2[1] = stack.point[ stack.current_frame,i,1 ]
				
		self.p1 =[0,0]
		self.p1[0]= stack.point[((stack.current_frame) - 1 ),i,0]
		self.p1[1]= stack.point[((stack.current_frame) - 1 ),i,1]
				
		#deleted: stack.advance_frame(-1)
		self.p0 = [0,0]
		self.p0[0]= stack.point[((stack.current_frame) - 2 ),i,0]
		self.p0[1]= stack.point[((stack.current_frame) - 2 ),i,1]
		
		result[i,0] = 2 * self.p1[0] - self.p0[0] 
		result[i,1] = 2 * self.p1[1] - self.p0[1]
		result[i,2] = getConfidence()
				
	    else:
	        
                for i in range(0,stack.current_frame):
                    result[i,0] = 0.0
                    result[i,1] = 0.0
                    result[i,2] = 0.0
                        
        #needs at least 3 frames of points to predict. after frames are 0(stack.current_frame is an array),1, 2 a prediction will be displayed on the 4th screen 
        if stack.current_frame > 1:	
			
            return result
			
        else:
            #Need at least 3 frames of points to predict
            #Return zeros to avoid getting nan values
	    return zeros([stack.point_kinds,3])

		

		
		
		
		
		