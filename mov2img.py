import os
import sys
try:
    import pyglet
except ImportError:
    print 'ERROR: you must install AVBin to use mov2img'
    exit()


#Opens a video and outputs every frame of it as a .png file
def mov2img(source,destination='',start=-1,end=-1,output = False):

    #Load in the video source file
    if output: sys.stdout.write('Loading video [')
    try:
        sourceVid = pyglet.media.load(source)
    except pyglet.media.MediaException:
        #The file format isn't supported
        if output:
            sys.stdout.write(']\n')
            print 'ERROR: input file format is not supported'
        return
    except IOError:
        #Error reading in the file
        if output:
            sys.stdout.write(']\n')
            print 'ERROR: could not read from input file'
        return
    except:
        #Pyglet screwed up somehow
        if output:
            sys.stdout.write(']\n')
            print 'ERROR: internal Pyglet error'
        return

    try:
        #Finish 'loading' output from above
        sys.stdout.write('--------------------]\n')

        #Is the file a video?
        if sourceVid.video_format == None:
            if output: print 'ERROR: input file is not a video'
            return

        #Check input
        if start == -1: start = 0
        if end == -1: end = sourceVid.duration
        if start > end or end > sourceVid.duration or start < 0 or end < 0:
            if output: print 'ERROR: invalid start or end time'
            return

        #If a directory wasn't specified, use the video's filename
        if destination == '':
            destination = os.getcwd() + os.path.sep + \
                os.path.basename(source).split('.')[0]

        time = 0
        frame = None

        #If requested, skip ahead to the start time
        if start > 0:
            if output:
                sys.stdout.write('Seeking to first frame [')
                sys.stdout.flush()
            notify = start / 20.0
            while time < start:
                frame = sourceVid.get_next_video_frame()
                time = sourceVid.get_next_video_timestamp()
                if time > notify:
                    if output:
                        sys.stdout.write('-')
                        sys.stdout.flush()
                    notify = notify + (start / 20.0)
            if output: sys.stdout.write(']\n');sys.stdout.flush()
        else:
            frame = sourceVid.get_next_video_frame()

        #Create the directory. If it already exists, use a different name
        try:
            os.mkdir(destination)
        except OSError:
            i = 1
            while os.path.isdir(destination+'('+str(i)+')'):
                i = i + 1
            destination = destination+'('+str(i)+')'
            os.mkdir(destination)
        if output: print "Frames will be saved in '"+destination+"'"

        #Save the video's frames until we run out of them or reach the end time
        if output: sys.stdout.write('Saving frames [');sys.stdout.flush()
        frameCount = 1
        notify = (end-start) / 20.0
        while frame != None and time <= end:
            if time-start > notify:
                if output: sys.stdout.write('-');sys.stdout.flush()
                notify = notify + ((end-start) / 20.0)
            imageData = frame.get_image_data()
            pixels = imageData.get_data(imageData.format,imageData.pitch *-1)
            imageData.set_data(imageData.format,imageData.pitch,pixels)
            imageData.save(destination+os.path.sep+"frame"+str(frameCount)+
                ".png")
            time = sourceVid.get_next_video_timestamp()
            frame = sourceVid.get_next_video_frame()
            frameCount += 1
        if output: sys.stdout.write(']\n');sys.stdout.flush();print 'Success'
    except:
        if output:
            sys.stdout.write(']\n')
            print 'ERROR: internal Pyglet error'
        return


#If this file is being run from the commandline, get input arguments and run
if __name__ == '__main__':
    argc = len(sys.argv)
    argv = sys.argv
    if argc < 2:
        print "ERROR: specify a movie to convert. See 'mov2img --help'."
        exit()
    if argv[1] == '--help':
        print 'usage: mov2img source [destination] [start time] [end time]'
        exit()
    dest = ''
    start = -1
    end = -1
    src = argv[1]
    if argc >= 3: dest = argv[2]
    if argc >= 4: start = int(argv[3])
    if argc >= 5: end = int(argv[4])
    mov2img(src,dest,start,end,True)


