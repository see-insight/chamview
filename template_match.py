import numpy as np
import matplotlib.pyplot as plt
from skimage import data
from skimage.feature import match_template
import skimage.io as io
from matplotlib.mlab import *
from PIL import Image
import matplotlib.image as mpimg
from pylab import ginput


def template_crop(im1):
    im = Image.open(im1)
    pic_plt = mpimg.pil_to_array(im)[:,:,0]
    fig = plt.imshow(pic_plt, origin='lower')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    offset = ginput(1)
    plt.close()
    # Creates a box around the point clicked
    Left = int(round(offset[0][0]-25))
    Upper = int(round(offset[0][1]-25))
    Right = int(round(offset[0][0]+25))
    Lower = int(round(offset[0][1]+25))
    return Left, Upper, Right, Lower

'''
Example code taken from:
http://scikits-image.org/docs/dev/auto_examples/plot_template.html#example-plot-template-py
'''
# Image for template to be matched to
image = 'img_file'
image = Image.open(image)
img_array = mpimg.pil_to_array(image)
image = img_array[:,:,0]
# Image that will have template cut out
image2 = 'template_file'
bounds = template_crop(image2)
im2 = Image.open(image2)
im2_array = mpimg.pil_to_array(im2)
image2 = im2_array[:,:,0]

template = image2[bounds[1]:bounds[3], bounds[0]:bounds[2]]

# Values from 0 to 1, measuring contrast intensity
conf = np.double(template)/255.
# Uses contrast difference within picture to come up with a
#  confidence percentage that it can match it correctly
#  (Looks like (conf.max()-conf.min()) at the bottom)

result = match_template(image, template)
ij = np.unravel_index(np.argmax(result), result.shape)
x, y = ij[::-1]

fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(8, 2))
ax1.imshow(template, origin='lower')
ax1.set_axis_off()
ax1.set_title('template')

ax2.imshow(image, origin='lower')
ax2.set_axis_off()
ax2.set_title('image')
# highlight matched region
htmplt, wtmplt = template.shape
rect = plt.Rectangle((x, y), wtmplt, htmplt, edgecolor='r', facecolor='none')
ax2.add_patch(rect)

# Section of image template was matched to
pic_match = image[y:y+htmplt,x:x+wtmplt]
# Subtracts pic_match from template (value of 0 means it was matched perfectly)
conf_match = abs(np.double(template)/255.-np.double(pic_match)/255.)
# Confidence your template was matched correctly
conf_match_avg = 1-conf_match.sum()/conf_match.size

plt.show()

# Multiplies the confidence percentages together for the percent chance
#  your template was matched correctly
print 'total confidence: ', (conf.max()-conf.min())*conf_match_avg*100, '%'
# As an estimate, 70% or above is a safe choice for a proper match

