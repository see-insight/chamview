# Test program written by Dirk
# Trying to figure out basic functionality to view a slide show
# The following seems to almost work

import time
from imagestack import *
imst = ImageStack('./images/')
while (imst.current_frame < imst.total_frames):
    im = imst.show()
    time.sleep(1)
    imst.next()
