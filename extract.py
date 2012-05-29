
import os
import pyglet

#Takes a video file and outputs every frame of it as a .png file in the
#specified destination folder
def exportVideoFrames(source,start=-1,end=-1):

    #Load in the video source file
    print "Loading video..."
    try:
        sourceVid = pyglet.media.load(source)
    except pyglet.media.MediaException:
        #The file format isn't supported
        print "Failure: input file format is not supported"
        return
    except IOError:
        #Error reading in the file
        print "Failure: could not read from input file"
        return
    except:
        #Pyglet screwed up
        print "Failure: Pyglet error"
        return
    
    try:
        #Is the file a video?
        if sourceVid.video_format == None:
            print "Failure: input file is not a video"
            return
            
        #Check input
        if start == -1: start = 0
        if end == -1: end = sourceVid.duration
        if start > end or end > sourceVid.duration or start < 0 or end < 0:
            print "Failure: please enter valid start and end times"
            return
        
        #Create the directory and rename it something else if it already exists
        destination = os.getcwd() + os.path.sep + os.path.basename(source).split('.')[0]
        try:
            os.mkdir(destination)
        except OSError:
            i = 1
            while os.path.isdir(destination+'('+str(i)+')'):
                i = i + 1
            destination = destination+'('+str(i)+')'
            os.mkdir(destination)
        print "Frames will be saved in '"+destination+"'"
        
        time = 0
        frame = None
        
        #If needed, skip ahead to the start time
        if start > 0:
            print "Seeking to first frame..."
            notify = start / 10.0
            while time < start:
                frame = sourceVid.get_next_video_frame()
                time = sourceVid.get_next_video_timestamp()
                if time > notify:
                    print str(int(notify*10.0/start)*10)+"%"
                    notify = notify + (start / 10.0)
        else:
            frame = sourceVid.get_next_video_frame()
        
        #Save the video's frames until we run out of them or reach the end time
        print "Saving frames..."
        frameCount = 1
        notify = (end-start) / 10.0
        while frame != None and time <= end:
            if time-start > notify:
                print str(int(notify*10.0/(end-start))*10)+"%"
                notify = notify + ((end-start) / 10.0)
            imageData = frame.get_image_data()
            pixels = imageData.get_data(imageData.format,imageData.pitch *-1)
            imageData.set_data(imageData.format,imageData.pitch,pixels)
            imageData.save(destination+os.path.sep+"frame"+str(frameCount)+".png")
            time = sourceVid.get_next_video_timestamp()
            frame = sourceVid.get_next_video_frame()
            frameCount += 1
        print "Success"
    except:
        print "Failure: Pyglet error"
        os.rmdir(destination)
        return

video = raw_input("Video: ")
print "Enter -1 for full-length video"
start = raw_input("Extraction start time (seconds): ")
end = raw_input("Extraction end time (seconds):   ")
exportVideoFrames(video,start,end)





