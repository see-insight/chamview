import os
import dircache
from PIL import Image
from numpy import *


class ImageStack:

    #---- Instance variables ----
    #point             row,column of each point kind in a given frame. Format is
    #                  a numpy array [frame,point kind,row/column]
    #point_kind[]      list of string labels associated with each point kind
    #point_kinds       number of point kinds is use
    #img_list[]        list of paths to image files to load and use as frames
    #img_current       PIL image of current frame or None if no frames loaded
    #img_previous      PIL image of previous frame or None if current_frame == 0
    #current_frame     0-based index of which frame is being analyzed
    #total_frames      number of valid images to use in the image directory
    #exit              if set to True, main ChamView file will exit and save
    #                  the current point set

    def __init__(self,directory=''):
        #Called upon instance creation
        self.point = zeros((0,0,2))
        self.point_kind = []
        self.point_kinds = 0
        self.img_list = []
        self.img_current = None
        self.img_previous = None
        self.current_frame = 0
        self.total_frames = 0
        self.exit = False
        if directory != '':
            self.get_img_list(directory)
            self.load_img()

    def get_img_list(self,directory):
        #Creates a list of every image file that can be used in the specified
        #directory, and uses this to set self.img_list[] and self.total_frames.
        #Valid extensions include bmp,jpg,png,gif
        self.img_list = []
        self.current_frame = 0
        self.total_frames = 0
        if os.path.isdir(directory) == False: return
        valid_extensions = ['.bmp','.jpg','.png','.gif']
        file_list = dircache.listdir(directory)
        for filename in file_list:
            extension = os.path.splitext(filename)[1].lower()
            if extension in valid_extensions:
                self.img_list.append(directory+os.path.sep+filename)
        self.total_frames = len(self.img_list)
        self.point = zeros((self.total_frames,self.point_kinds,2))

    def get_point_kinds(self,filename=''):
        #Creates a list of valid point kinds read in from a file. Each line of
        #the file should have a point kind (i.e. Left back foot) with any
        #additional information separated by commas (which will be ignored). The
        #default point kind file will be used if no file is specified
        if filename == '': filename = 'defaultPointKinds.txt'
        if os.path.exists(filename) == False: return
        self.point_kinds = sum(1 for line in open(filename))
        self.point_kind = []
        self.point = zeros((self.total_frames,self.point_kinds,2))
        file_in = open(filename)
        for line in file_in:
            line_list = line.split(',')
            if len(line_list[0]) == 0: continue
            if line_list[0].endswith('\n'):
                line_list[0] = line_list[0][0:-1]
            self.point_kind.append(line_list[0])
        file_in.close()

    def load_points(self,filename):
        #Loads previous point data in from a file. Each line should be in the
        #format frame,point label,row,column
        self.point = [[0,0]*(self.point_kinds or 1)]*(self.total_frames or 1)
        if os.path.exists(filename) == False: return
        file_in = open(filename)
        for line in file_in:
            line_list = line.split(',')
            frame = int(line_list[0])
            kind = line_list[1]
            try:
                kind_index = self.point_kind.index(kind)
            except ValueError:
                kind_index = -1
            row = int(line_list[2])
            column = int(line_list[3])
            if frame > self.total_frames - 1 or frame < 0: continue
            if kind_index > self.pointKinds - 1 or kind_index == -1: continue
            self.point[frame,kind_index] = [row,column]
        file_in.close()

    def load_img(self):
        #Loads the correct self.img_current and self.img_previous into memory
        #based on self.current_frame.
        self.img_current = None
        self.img_previous = None
        if self.total_frames == 0: return
        if self.current_frame < 0: return
        if self.current_frame > self.total_frames - 1: return
        self.img_current = Image.open(self.img_list[self.current_frame])
        if self.current_frame > 0:
            self.img_previous = Image.open(self.img_list[self.current_frame-1])
        else:
            self.img_previous = None

    def save_points(self,filename):
        #Saves all points to a file in the format frame,point kind,row,column.
        #Note that this will overwrite any existing file without warning
        file_out = open(filename,'w')
        for frame in range(0,self.total_frames):
            for kind_index in range(0,self.point_kinds):
                kind = self.point_kind[kind_index]
                file_out.write(str(frame)+','+kind+','+
                    str(self.point[frame,kind_index,0])+','+
                    str(self.point[frame,kind_index,1])+'\n')
        file_out.close()

    def show(self):
        #A method for debugging. Displays the current frame
        if self.img_current != None:
            self.img_current.show()

    def set_frame(self,frame):
        #Sets the current frame and loads the corresponding image
        self.current_frame = frame
        if self.current_frame < 0:
            self.current_frame = 0
        if self.current_frame > self.total_frames - 1:
            self.current_frame = self.total_frames - 1
        self.load_img()

    def advance_frame(self,frames):
        #Advances the frame by a number and loads the correspending image
        self.set_frame(self.current_frame + frames)

    def next(self):
        #Advances the frame by one
        self.advance_frame(1)

    def prev(self):
        #Backs the frame up by one
        self.advance_frame(-1)

