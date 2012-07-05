from numpy import *


class Chooser(object):

    def setup(self):
        #Called by ChamView before the plugin has to do anything. Create GUI
        #elements, etc. here
        raise NotImplementedError

    def teardown(self):
        #Called to allow the plugin to free any resources or delete temporary
        #files
        raise NotImplementedError

    def choose(self,stack,predicted,predictor_name):
        #Determine which predicted point to use. 'predicted' is a numpy array
        #in the format [predictor, point kind, row/column/confidence].
        #'predictor_name' is a numpy array of strings that correlates with the
        #first dimension of the 'predicted' argument
        raise NotImplementedError


class Predictor(object):

    def setup(self,stack):
        #Called by ChamView before the plugin has to do anything. Optioanlly
        #perform initial analysis on the first frame and/or return a predicition
        #of a point that may be of interest to track. If it returns, it must be
        #a numpy array [row/column/confidence]
        raise NotImplementedError

    def teardown(self):
        #Called to allow the plugin to free any resources or delete temporary
        #files
        raise NotImplementedError

    def predict(self,stack):
        #Using the current and previous frame and previous ground-truth point
        #positions, predict and return the position of the points in the current
        #frame as well as a confidence. Confidence is a float 0.0-1.0. Must
        #return a numpy array [point kind,row/column/confidence]
        raise NotImplementedError

