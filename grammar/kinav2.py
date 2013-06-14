#This class implements kinematic predictor with some modifications
#June 14, 2013
from Grammar import Predictor
from numpy import *
import random
from imagestack import ImageStack


class Kinav2(Predictor):
	#subclass of predictor, in base.py , to deactivate ( or to have it not predict anything) delete "Predictor" and it will no longer be a subclass
	# of Predictor. To make it predict again, insert "Predictor" within the parenthesis again.
	stack = ImageStack('./images/')
	def setup(self,stack):
		# set up variables self.p0, self.p1, self.p2
		self.p0 = [0,0]
		self.p1 = [0,0]
		self.p2 = [0,0]
		self.p3 = [0,0] # not for predicting
		self.f = 1
		self.z = 1
	
	def teardown(self) :
	
		pass
	
	def predict(self,stack,pointsEdited=False) :
		
	
		#initialize "results". Will be a two dimensional array of zeros with the number of rows dependent on the size of "stack.pointkind", and 3 columns
		result = zeros([stack.point_kinds,3])
		#point_hold = open( 'pointHold.txt'  , 'a')
		
		def pred( p0, p1, p2):
		    
		    pf = [0.0, 0.0] #Define return array of length 2
		    pf[0] = decide(p0[0], p1[0], p2[0])
		    pf[1] = decide(p0[1], p1[1], p2[1])
		    return pf
		    
		#This method decides if the new point has to follow the kinematic method
		#or it can be computed by average of the previous point to avoid points
		#far away
		def decide(p0, p1, p2):
		    
		    if (p0 <= p1 and p1 <= p2) or (p0 >= p1 and p1 >= p2):
		        #Case when points are in order
		        pf = veloc(p0, p1, p2)
		    else:
		        #Case when points are not in order, better take average
		        #of last two points
		        pf = (p1 + p2) / 2
		    return pf
		        
		def veloc(p0, p1, p2):

                    #this is the velocity function
		    t = 1.0  #used to be 1
		    v1 = (p1 - p0)/t   					
		    v2 = (p2 - p1)/t				
		    a = (v2 - v1)/t
		    pf = p2 + v2 * t + a * (t**2)
		    return pf
		  
		for i in range(0,stack.point_kinds):
			# this loop runs for every point kind. ex: snout, left front leg, etc.
			
			if stack.current_frame >= 2:
				#gets points on previous 3 frames, then predicts a point on the current frame
				self.p3 = [0,0]
				self.p3[0] = stack.point[ stack.current_frame,i,0 ]
				self.p3[1] = stack.point[ stack.current_frame,i,1 ]
				self.p2 =[0,0]
				self.p2[0]= stack.point[((stack.current_frame) - 1 ),i,0]
				self.p2[1]= stack.point[((stack.current_frame) - 1 ),i,1]
				#deleted: stack.advance_frame(-1)
				self.p1 = [0,0]
				self.p1[0]= stack.point[((stack.current_frame) - 2 ),i,0]
				self.p1[1]= stack.point[((stack.current_frame) - 2 ),i,1]
				#deleted: stack.advance_frame(-1)
				self.p0[0]= stack.point[((stack.current_frame) - 3 ),i,0]
				self.p0[1]= stack.point[((stack.current_frame) - 3 ),i,1]
				current = [0,0]
				current[0] = self.p3[0]
				current[1] = self.p3[1]
				#calls pred function
				pf= pred(self.p0,self.p1,self.p2)
				confidence = 0.0
				result[i,0] = pf[0]
				result[i,1] = pf[1]
				result[i,2] = confidence
				
			if ((stack.current_frame) < 2):
				for i in range(0,stack.current_frame):
					result[i,0] = 0.0
					result[i,1] = 0.0
					result[i,2] = 0.0
		#needs at least 3 frames of points to predict. after frames are 0(stack.current_frame is an array),1, 2 a prediction will be displayed on the 4th screen 
		if stack.current_frame > 2:	
			return result
		else:
			return zeros([stack.point_kinds,3])
		
		
		
		
		
		
