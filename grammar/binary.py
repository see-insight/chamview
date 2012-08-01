import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import skimage.color as color
import numpy
from skimage.data import camera
from skimage.filter import threshold_otsu
from Grammar import Preprocessor
from PIL import Image

class Binary(Preprocessor):

    def setup(self,args):
        #We needn't initialize anything for this Preprocessor
        self.contrast_amount = 2.0
        pass

    def teardown(self):
        #We needn't rid of anything for this Preprocessor
        pass

    def process(self, image):
        #print image
        image = mpimg.pil_to_array(image)
        #image = color.rgb2gray(image)
        thresh = threshold_otsu(image)
        #thresh = thresh + 57
        binary = image > thresh
        binary = numpy.flipud(binary)
        binary = (binary*255).astype('uint8')
        binary = Image.fromarray(binary) # monochromatic image
        #binary = Image.merge('RGB', (im,im,im)) # color image
        #binary = mpimg.fromarray(binary)
        #binary = mpimg.fromarray(numpy.uint8(binary))

        #plt.figure(figsize=(8, 2.5))
        #plt.subplot(1, 3, 1)
        #plt.imshow(image, cmap=plt.cm.gray)
        #plt.title('Original')
        #plt.axis('off')

        #plt.subplot(1, 3, 2, aspect='equal')
        #plt.hist(image)
        #plt.title('Histogram')
        #plt.axvline(thresh, color='r')

        #plt.subplot(1, 3, 3)
        #plt.imshow(binary, cmap=plt.cm.gray)
        #plt.title('Thresholded')
        #plt.axis('off')

        #plt.show()
        return binary 
