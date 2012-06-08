from PIL import Image
from PIL import ImageChops
import matplotlib.pyplot as plt
from pylab import ginput

import datetime

# Crop a template to match by choosing an upper left and lower right boundary
def template_crop(im1):
    print "Pick the upper left and lower right corners of the template \
to be matched"
    im = Image.open(im1)
    pic_plt = plt.imread(im1)
    y = pic_plt[:,0,0].size
    plt.imshow(pic_plt,origin='lower')
    LOffset = ginput(1)
    ROffset = ginput(1)
    plt.close()
    # Have to change the column boundary due to the y-axis being flipped
    crop_b = (int(round(LOffset[0][0])),int(round(y-LOffset[0][1])),\
              int(round(ROffset[0][0])),int(round(y-ROffset[0][1])))
    print 'coordinates (origin in upper left):',crop_b
    crop_im = im.crop(crop_b)
    crop_im.load()
    #crop_im.save('crop.jpg')
    return crop_im

'''
Example code taken from:
http://www.daniweb.com/software-development/python/threads/252384/python-pil-template-matching
'''
def matchTemplate(searchImage, templateImage):
    minScore = -1000
    matching_xs = 0
    matching_ys = 0
    # convert images to "L" to reduce computation by factor 3 "RGB"->"L"
    searchImage = searchImage.convert(mode="L")
    templateImage = templateImage.convert(mode="L")
    searchWidth, searchHeight = searchImage.size
    templateWidth, templateHeight = templateImage.size
    # make a copy of templateImage and fill with color=1
    templateMask = Image.new(mode="L", size=templateImage.size, color=1)
    # loop over each pixel in the search image
    for xs in range(searchWidth-templateWidth+1):
        for ys in range(searchHeight-templateHeight+1):
            score = templateWidth*templateHeight
            # crop the part from searchImage
            searchCrop = searchImage.crop((xs,ys,xs+templateWidth,ys+templateHeight))
            diff = ImageChops.difference(templateImage, searchCrop)
            notequal = ImageChops.darker(diff,templateMask)
            countnotequal = sum(notequal.getdata())
            score -= countnotequal

        if minScore < score:
            minScore = score
            matching_xs = xs
            matching_ys = ys

    print "Location=",(matching_ys, matching_xs), "Score=",minScore
    im1 = Image.new('RGB', (searchWidth, searchHeight))
    im1.paste(templateImage, (matching_ys, matching_xs))
    # Saves only the matched template to the coordinates of where it was located
    #im1.save('template_matched_in_search.png')
    # Boundaries of matched template within the searchImage
    print (matching_ys, matching_xs, matching_ys+templateWidth,matching_xs+templateHeight)
    return (matching_ys, matching_xs, matching_ts+templateWidth,matching_xs+templateHeight)

# Opens the image to be searched
searchImage = Image.open("test_file")
# Opens image to find template from
templateImage = template_crop('test_file')


# Calculates the amount of time the computation took
t1=datetime.datetime.now()
matchTemplate(searchImage, templateImage)
delta=datetime.datetime.now()-t1
print "Time=%d.%d"%(delta.seconds,delta.microseconds)
print "end"
