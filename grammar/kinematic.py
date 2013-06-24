from Grammar import Predictor
from numpy import *
import random
from imagestack import ImageStack


class Kinematic(Predictor):
	#subclass of predictor, in base.py , to deactivate ( or to have it not predict anything) delete "Predictor" and it will no longer be a subclass
	# of Predictor. To make it predict again, insert "Predictor" within the parenthesis again.
	stack = ImageStack('./images/')
	def setup(self,stack):
		#p0 = [0,0] #not needed
		#p1 = [0,0] #not needed
		#p2 = [0,0] #not needed
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
		def veloc( p0, p1, p2):
			#this is the velocity function
			t = 1.0  #used to be 1
			v1=[0.0,0.0]
			v2=[0.0,0.0]
			v1[0] = (p1[0] - p0[0])/t   
			v1[1] = (p1[1] - p0[1])/t
					
			v2[0] = (p2[0] - p1[0])/t
			v2[1] = (p2[1] - p1[1])/t
					
			a= [0,0]
			a[0] = (v2[0] - v1[0])/t
			a[1] = (v2[1] - v1[1])/t
					
    
			pf= [0.0,0.0]

			pf[0] = (p2[0] + v2[0] * t + a[0] * (t**2))
			pf[1] = (p2[1] + v2[1] * t + a[1] * (t**2))
			return pf
			
		def getDistance(p, q):
                    return ((p[0] - q[0])**2 + (p[1] - q[1])**2)**0.5
			
		def getConfidence(pf):
	                '''After thinking further, not a correct way of measuring confidence.
                        Still needs revision.
                        '''
                     
                        #Get distance between p0, p1, p2, pf
                        dist01 = getDistance(self.p0, self.p1)
                        dist12 = getDistance(self.p1, self.p2)
                        dist2f = getDistance(self.p2, pf)
                        
                        #Compute ratios between one distance and the previous one
                        if dist01 == 0:
                            ratio1 = dist12
                        else:
                            ratio1 = dist12 / dist01
                            
                        if dist12 == 0:
                            ratio2 = dist2f
                        else:
                            ratio2 = dist2f / dist12

                        #Confidence increases if the ratios between
                        #the distances p1p2-p0p1 and p1p2-p2pf are the same
                        return 1 / (1 + abs(ratio2 - ratio1))
			
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
				#calls velocity function
				pf= veloc(self.p0,self.p1,self.p2)
				
				result[i,0] = pf[0]
				result[i,1] = pf[1]
				result[i,2] = getConfidence(pf)
				
			if ((stack.current_frame) < 2):
				for i in range(0,stack.current_frame):
					result[i,0] = 0.0
					result[i,1] = 0.0
					result[i,2] = 0.0
		#needs at least 3 frames of points to predict. after frames are 0(stack.current_frame is an array),1, 2 a prediction will be displayed on the 4th screen 
		if stack.current_frame > 2:	
			
			
			return result
			
		else:
			#Need at least 3 frames of points to predict
                        #Return zeros to avoid getting nan values
			return zeros([stack.point_kinds,3])

		

		
		
		
		
		
		
