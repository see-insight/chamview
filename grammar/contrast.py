from Grammar import Preprocessor
from PIL import ImageEnhance

class Contrast(Preprocessor):

    def setup(self,args):
        #We needn't initialize anything for this Preprocessor
        self.contrast_amount = 2.0
        pass

    def teardown(self):
        #We needn't rid of anything for this Preprocessor
        pass

    def process(self,image):
        #Add contrast to the image and return the modified version
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(self.contrast_amount)
