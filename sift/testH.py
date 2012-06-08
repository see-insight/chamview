from PIL import Image
from pylab import *

import imtools
import harris

imgname = 'ignore/test/empire.jpg'

img = Image.open(imgname)
arr = array(img.convert('L'))
response = harris.compute_response(arr)
points = harris.get_points(response,threshold=0.05)
harris.plot_points(arr,points)
show()



