import numpy 
import matplotlib.image as mpimg
import skimage.color as color
from Grammar import Preprocessor
from PIL import Image

class HSV(Preprocessor):

    def setup(self,args):
        #We needn't initialize anything for this Preprocessor
        self.contrast_amount = 2.0
        pass

    def teardown(self):
        #We needn't rid of anything for this Preprocessor
        pass

    def process(self,image,channel=2):
        rgb = mpimg.pil_to_array(image)
        hsv = color.rgb2hsv(rgb)
        hsv = numpy.flipud(256 *hsv[:,:,channel])
        hsv = Image.fromarray(hsv)
        return hsv 

class RGB(Preprocessor):

    def setup(self,args):
        #We needn't initialize anything for this Preprocessor
        self.contrast_amount = 2.0
        pass

    def teardown(self):
        #We needn't rid of anything for this Preprocessor
        pass

    def process(self,image,channel=2):
        rgb = mpimg.pil_to_array(image)
        rgb = numpy.flipud(rgb[:,:,channel])
        rgb = Image.fromarray(rgb)
        return rgb 

