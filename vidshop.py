#
# Created by Aaron Beckett July 11, 2013
# Editted by:
#   Aaron Beckett
#
#
'''Provides video editing features for chamwrap by subprocessing ffmpeg.'''

import os, subprocess
from datetime import datetime as dt
from wrappers import customWidgets

try:
    DEVNULL = open(os.devnull, 'wb')
    subprocess.call(['ffmpeg'], stdout=DEVNULL, stderr=DEVNULL)
    FFMPEG = True
except OSError:
    FFMPEG = False

def ffmpeg_installed():
    return FFMPEG

def grab_frames(video, fps, start, end, save_dir):
    print 'video: ' + video
    print 'frames per second: ' + str(fps)
    print 'start time: ' + start
    print 'end time: ' + end
    print 'save directory: ' + save_dir
    diff = dt.strptime(end, '%H:%M:%S') - dt.strptime(start, '%H:%M:%S')
    durration = diff.total_seconds()

    if FFMPEG:
        command = 'ffmpeg '
        if start != '':
            command += '-ss ' + start + ' '
        command += '-i ' + video + ' -y -r ' + str(fps) + ' '
        if end != '':
            command += '-t ' + str(durration) + ' '
        command += '-f image2 ' + save_dir.rstrip('\/') + '/%6d.jpg'
        print command
        try:
            stream = customWidgets.WindowStream()
            subprocess.check_call(command.split(), stdout=stream, stderr=stream)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return False
