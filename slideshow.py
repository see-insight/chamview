# Test program written by Dirk 
# Trying to figure out basic functionality to view a slide show
# The following seems to almost work

import time
from imagestack import *
imst = ImageStack('./images/')
i = 0
while (i < imst.total_frames):
    im = imst.show()
    imst.advance_frame(1)
    time.sleep(1)

