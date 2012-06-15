import numpy as np
import matplotlib.pyplot as plt
from skimage import data
from skimage.feature import match_template
import skimage.io as io
from matplotlib.mlab import *
from PIL import Image
import matplotlib.image as mpimg
from pylab import ginput


def template(im1):
    im = Image.open(im1)
    pic_plt = mpimg.pil_to_array(im)
    y = pic_plt[:,0,0].size
    fig = plt.imshow(pic_plt, origin='lower')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    offset = ginput(1)
    plt.close()
    Left = int(round(offset[0][0]-25))
    Upper = int(round(offset[0][1]-25))
    Right = int(round(offset[0][0]+25))
    Lower = int(round(offset[0][1]+25))
    return Left, Upper, Right, Lower

'''
Example code taken from:
http://scikits-image.org/docs/dev/auto_examples/plot_template.html#example-plot-template-py
'''
image = 'test_file'
image = mpimg.imread(image)
image = image[:,:,0]
bounds = template('template_file')
coin = image[bounds[1]:bounds[3], bounds[0]:bounds[2]]

result = match_template(image, coin)
ij = np.unravel_index(np.argmax(result), result.shape)
x, y = ij[::-1]

fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(8, 3))

ax1.imshow(coin, origin='lower')
ax1.set_axis_off()
ax1.set_title('template')

ax2.imshow(image, origin='lower')
ax2.set_axis_off()
ax2.set_title('image')
# highlight matched region
hcoin, wcoin = coin.shape
rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
ax2.add_patch(rect)

ax3.imshow(result, origin='lower')
ax3.set_axis_off()
ax3.set_title('`match_template`\nresult')
# highlight matched region
ax3.autoscale(False)
ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)

plt.show()

