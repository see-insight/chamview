import os
import dircache
from PIL import Image


class ImageStack:

    #---- Instance variables ----
    #point[[[]]]       row,column of each point kind in a given frame. Format is
    #                  self.point[frame][point kind][r,c]
    #point_kind[]      label associated with each point kind
    #point_kinds       number of point kinds is use
    #img_list[]        list of paths to image files to load and use as frames
    #img_current       PIL image of current frame or None if no frames loaded
    #img_previous      PIL image of previous frame or None if current_frame == 0
    #current_frame     0-based index of which frame is being analyzed
    #total_frames      number of valid images to use in the image directory

    def __init__(self):
        #Called upon instance creation
        self.point = [[0,0]]
        self.point_kind = []
        self.point_kinds = 0
        self.img_list = []
        self.img_current = None
        self.img_previous = None
        self.current_frame = 0
        self.total_frames = 0

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
            extension = lower(os.path.splitext(filename)[1])
            if extension in valid_extensions: self.img_list.append(filename)
        self.total_frames = len(self.img_list)
        self.point = [[0,0]*(self.point_kinds or 1)]*(self.total_frames or 1)

    def get_point_kinds(self,filename=''):
        #Creates a list of valid point kinds read in from a file. Each line of
        #the file should have a point kind (i.e. Left back foot) with any
        #additional information separated by commas (which will be ignored). The
        #default point kind file will be used if no file is specified
        self.point_kind = []
        self.point_kinds = 0
        if filename == '': filename = 'defaultPointKinds.txt'
        if os.path.exists(filename) == False: return
        file_in = open(filename)
        for line in file_in:
            line_list = line.split(',')
            if len(line_list[0]) == 0: continue
            self.point_kind.append(line_list[0])
        file_in.close()
        self.point_kinds = len(self.point_kind)
        self.point = [[0,0]*(self.point_kinds or 1)]*(self.total_frames or 1)

    def load_points(self,filename):
        #Loads previous point data in from a file. Each line should be in the
        #format frame,point kind,row,column
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
            self.point[frame][kind_index] = [row,column]
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
        for frame,kind_index,row,column in self.point:
            kind = self.point_kind[kind_index]
            file_out.write(str(frame)+','+kind+','+str(row)+','+str(column)+
                '\n')
        file_out.close()

