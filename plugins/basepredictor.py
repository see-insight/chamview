class BasePredictor(object):

    def setup(self):
        #Called by ChamView before the plugin has to do anything. Optioanlly
        #perform initial analysis on the first frame and/or return a predicition
        #of a point that may be of interest to track. If it returns, it must be
        #in the format [row,column]
        raise NotImplementedError

    def teardown(self):
        #Called to allow the plugin to free any resources or delete temporary
        #files
        raise NotImplementedError

    def predict(self,stack):
        #Using the current and previous frame and previous ground-truth point
        #positions, predict and return the position of the point in the current
        #frame as well as a confidence. Confidence is a float 0.0-1.0. Must
        #return in the format [row,column],confidence
        raise NotImplementedError

