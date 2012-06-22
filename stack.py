
import os
import dircache
from PIL import Image

class Stack:

    def __init__(self):
        self.point = [[]]
        self.point_filename = ''
        self.img_list = []
        self.img_current = None
        self.img_previous = None
        self.current_frame = 0
        self.total_frames = 0


    def get_img_list(self,directory):
        if os.path.isdir(directory) == False: return
        valid_extensions = ['png','jpg','bmp','gif']
        fileList = dircache.listdir(directory)
        for filename in fileList:
            extension = filename.split('.')[-1].lower()
            if extension in valid_extensions: self.img_list.append(filename)
        self.total_frames = len(self.img_list)


    def load_img(self):
        if self.total_frames == 0: return
        if self.current_frame < 0: self.current_frame = 0
        if self.current_frame >= self.total_frames: self.current_frame = \
            self.total_frames - 1
        self.img_current = Image.open(self.img_list[self.current_frame])
        if self.current_frame > 0:
            self.img_previous = Image.open(self.img_list[self.current_frame-1])
        else:
            self.img_previous = None


    def load_points(self):
        pass

    def save_points(self):
        pass
