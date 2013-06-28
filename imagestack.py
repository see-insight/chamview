import os
import dircache
from PIL import Image
from numpy import *
from decimal import *


class ImageStack:

    """    #---- Instance variables ----
    point             column,row of each point kind in a given frame. Format is
                      a numpy array [frame,point kind,column/row]
    point_kind_list[] list of string labels associated with each point kind
    point_kinds       number of point kinds in use
    point_sources     array with indices of which predictor provided the point
                      with -1 = user; format: [frame,point kind,source]
    img_list[]        list of paths to image files to load and use as frames
    img_current       PIL image of current frame or None if no frames loaded
    img_previous      PIL image of previous frame or None if current_frame == 0
    name_current      Current File name
    current_frame     0-based index of which frame is being analyzed
    total_frames      number of valid images to use in the image directory
    exit              if set to True, main ChamView file will exit and save
                      the current point set
    """
    
    def __init__(self,directory=''):
        #Called upon instance creation
        self.point = zeros((0,0,2))
        self.predictions = zeros((0,0,0,3))
        self.point_kind_list = []
        self.point_kinds = 0
        self.point_sources = []
        self.img_list = []
        self.img_current = None
        self.img_previous = None
        self.current_frame = 0
        self.total_frames = 0
        self.single_img = False
        self.exit = False
        if directory != '':
            self.get_img_list(directory)
            self.load_img()

    def __str__(self):
        #Called when an instance is used as a string, i.e. "print myImStack"
        result = '['
        if self.img_list:
            result += 'Image ' + str(self.current_frame+1) + '/'
            result += str(self.total_frames) + ' is '
            result += '"' + self.img_list[self.current_frame] + '", '
        else:
            result += 'No valid image files, '
        result += str(self.point_kinds) + ' point kinds'
        result += ']'
        return result

    def get_img_list(self,directory):
        #Creates a list of every image file that can be used in the specified
        #directory, and uses this to set self.img_list[] and self.total_frames.
        #Valid extensions include bmp,jpg,png,gif
        for sep in ['/','\\']:
            directory = directory.replace(sep,os.path.sep)
        self.img_list = []
        self.current_frame = 0
        self.total_frames = 0
        valid_extensions = ['.ppm','.bmp','.jpg','.png','.gif']
        if os.path.isdir(directory) == False: 
            file_list = [ directory ]
            directory = './'
        else:
            file_list = dircache.listdir(directory)
        #print file_list
        for filename in file_list:
            extension = os.path.splitext(filename)[1].lower()
            if extension in valid_extensions:
                self.img_list.append(directory+os.path.sep+filename)
        self.total_frames = len(self.img_list)
        if self.total_frames == 1:
            self.single_img = True
        self.point = zeros((self.total_frames,self.point_kinds,2))
        self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]

    def get_point_kinds(self,filename='',List=[]):
        #Creates a list of valid point kinds read in from a file or a list of
        #string names of point kinds. Each line of the file should have a point 
        #kind (i.e. Left back foot) with any additional information separated by 
        #commas (which will be ignored). The default point kind file will be 
        #used if no file is specified and no list is provided. If the file is 
        #legacy from the old Chamview, it will be loaded appropriately.
        if List == []:
            if filename == '': filename = 'defaultPointKinds.txt'   
            if os.path.exists(filename) == False: return
            self.point_kinds = sum(1 for line in open(filename))
            self.point_kind_list = []
            self.point = zeros((self.total_frames,self.point_kinds,2))
            self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]
            file_in = open(filename)
            for line in file_in:
                #If it's an old point kind file, switch over to the legacy loader
                try:
                    if int(line) == self.point_kinds-1:
                        file_in.close()
                        self.get_point_kinds_legacy(filename)
                        return
                except ValueError:
                    pass
                line_list = line.split(',')
                if len(line_list[0]) == 0: continue
                if line_list[0].endswith('\n'):
                    line_list[0] = line_list[0][0:-1]
                self.point_kind_list.append(line_list[0])
            file_in.close()
        else:
            self.point_kinds = len(List)
            self.point_kind_list = List
            if self.point == zeros((0,0,2)):
                self.point = zeros((self.total_frames,self.point_kinds,2))
                self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]

    def get_point_kinds_legacy(self,filename=''):
        #Loads point kinds from a file in the legacy format. The first line of
        #the file contains the number of point kinds and each line thereafter
        #is in the format buttonToHit label color
        self.point_kinds = sum(1 for line in open(filename)) - 1
        self.point_kind_list = []
        self.point = zeros((self.total_frames,self.point_kinds,2))
        self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]
        file_in = open(filename)
        for line in file_in:
            line_list = line.split(' ')
            if len(line_list) == 1:continue
            if len(line_list[0]) == 0: continue
            self.point_kind_list.append(line_list[1])
        file_in.close()

    def load_points(self,filename):
        #Loads previous point data in from a file. Each line should be in the
        #format frame,point label,row,column. If the input file is legacy from
        #the old Chamview, it will be loaded appropriately
        self.point = zeros((self.total_frames,self.point_kinds,2))
        self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]
        if os.path.exists(filename) == False: return False
        file_in = open(filename)
        
        for line in file_in:
            #If the line begins with a # skip it and move on
            if line[0] == '#':
                continue
            #If it's an old point file, switch over to the legacy point loader
            if len(line.split(',')) == 1 and len(line.split(':')) == 6:
                file_in.close()
                self.load_points_legacy(filename)
                return False
            line_list = line.split(',')
            frame = int(line_list[0])
            kind = line_list[1]
            try:
                kind_index = self.point_kind_list.index(kind)
            except ValueError:
                kind_index = -1
            column = int(line_list[2])
            if line_list[3].endswith('\n'): line_list[3] = line_list[3][0:-1]
            row = int(line_list[3])
            point_source = -1 
            if frame > self.total_frames - 1 or frame < 0: continue
            if kind_index > self.point_kinds - 1 or kind_index == -1: continue
            if point_source < -1: continue
            self.point[frame,kind_index,0] = column
            self.point[frame,kind_index,1] = row
            self.point_sources[frame][kind_index] = point_source
        file_in.close()
        return True

    def load_points_legacy(self,filename):
        #Loads previous point data in from a file. Each line should be in the
        #old format of frame+n:row0:column0:row1:column1:circleID+label
        self.point = zeros((self.total_frames,self.point_kinds,2))
        self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]
        if os.path.exists(filename) == False: return
        file_in = open(filename)
        for line in file_in:
            line_list = line.split(':')
            frame = int(line_list[0][:-1]) - 1 #old ChamView is 1-based
            if line_list[5].endswith('\n'): line_list[5] = line_list[5][0:-1]
            kind = line_list[5][1:-1]
            #Take the average of each set of points describing the circle to get
            #the center
            column = int((int(line_list[1])+int(line_list[3]))/2)
            row = int((int(line_list[2])+int(line_list[4]))/2)
            try:
                kind_index = self.point_kind_list.index(kind)
            except ValueError:
                kind_index = -1
            if frame > self.total_frames - 1 or frame < 0: continue
            if kind_index > self.point_kinds - 1 or kind_index == -1: continue
            self.point[frame,kind_index,0] = column
            self.point[frame,kind_index,1] = row
            self.point_sources[frame][kind_index] = -1
        file_in.close()
        
    def load_predictions(self, filename):  
        
        if os.path.exists(filename) == False: return False
        file_in = open(filename) #Open file

        fileArr = file_in.readlines() #Copy lines to an array
        
        for i in range(0, len(fileArr)):
            if fileArr[i].startswith('#'):
                continue
            elif fileArr[i].startswith('frames'):
                numFrames = int(fileArr[i].split()[-1])
            elif fileArr[i].startswith('predictors'):
                numPredictors = int(fileArr[i].split()[-1])
            elif fileArr[i].startswith('point_kinds'):
                numPointK = int(fileArr[i].split()[-1])
            else:
                fileArr = fileArr[i:]
                break
        
        #Define array
        self.predictions = zeros((numFrames, numPredictors, numPointK, 3))
        
        #Get predictors
        predictors = []
        for i in range(0, numPredictors):
            if fileArr[i].startswith('#'): continue
            predictors.append(fileArr[i])
        
        fileArr = fileArr[numPredictors:]
        
        for i in range(0, len(fileArr)):
            if fileArr[i].startswith('#'): continue
            line = fileArr[i].split(',')
            self.predictions[int(line[0])][int(line[1])][int(line[2])][0] = int(line[3])
            self.predictions[int(line[0])][int(line[1])][int(line[2])][1] = int(line[4])
            self.predictions[int(line[0])][int(line[1])][int(line[2])][2] = float(line[5])
        
        return True
            
    def point_empty(self, frame, point_kind):
        '''Return true if the x,y coordinates for the given point kind on the 
        given frame are (0,0).'''
        return (self.point[frame,point_kind,0] == 0 and 
                    self.point[frame,point_kind,1] == 0)
        
    def addPointKinds(self,n):
        '''Add n new Point Kinds to the image stack's numpy array of point information.'''
        temp = self.point.tolist()
        for i in range(n):
            for frame in range(self.total_frames):
                temp[frame].append([0,0])
                self.point_sources[frame].append(-1)
        self.point = array(temp)
        
    def deletePointKinds(self,indices):
        '''Delete Point information in the image stack's numpy array of point 
        information for each index provided.'''
        temp = self.point.tolist()
        new_point = []
        new_sources = []
        for frame in range(self.total_frames):
            new_point_frame = []
            new_sources_frame = []
            for kind in range(self.point_kinds):
                if kind not in indices:
                    new_point_frame.append(temp[frame][kind])
                    new_sources_frame.append(self.point_sources[frame][kind])
            new_point.append(new_point_frame)
            new_sources.append(new_sources_frame)
        self.point = array(new_point)
        self.point_sources = new_sources   
        
        
    def clearFrame(self):
        pass
        
    def clearAll(self):
        pass

    def load_img(self):
        #Loads the correct self.img_current and self.img_previous into memory
        #based on self.current_frame.
        self.img_current = None
        self.img_previous = None
        if self.single_img == True:
            self.name_current = self.img_list[0]
            self.img_current = Image.open(self.name_current) 
            return
        if self.total_frames == 0: return
        #if self.total_frames == 1: return
        if self.current_frame < 0: return
        if self.current_frame > self.total_frames - 1: return
        self.name_current = self.img_list[self.current_frame]
        self.img_current = Image.open(self.name_current)
        #print "Loading Image = ", self.name_current
        if self.current_frame > 0:
            self.img_previous = Image.open(self.img_list[self.current_frame-1])
        else:
            self.img_previous = None
    
    def save_points(self,filename):
        #Saves all points to a file in the format:
        #        frame,point kind,column,row,point_source.
        #Note that this will overwrite any existing file without warning
        file_out = open(filename,'w')
        file_out.write("# frame,point_kind,column,row,point_source\n")
        for frame in range(self.total_frames):
            for kind_index in range(self.point_kinds):
                kind = self.point_kind_list[kind_index]
                file_out.write(str(frame)+','+kind+','+
                    str(int(self.point[frame,kind_index,0]))+','+
                    str(int(self.point[frame,kind_index,1]))+','+'\n')
        file_out.close()
        print "points saved to "+filename
        
    def build_predictionsArray(self, numPredictors):
        self.predictions = zeros((self.total_frames, numPredictors, self.point_kinds, 3))
        
    def save_predictions(self, filename, predictor_name):
        #Save all predictions computed when running Chamview
        #The format is the following: frame number, predictor, point kind, row, column
        #Note that this will overwrite any existing file without warning
        
        #Open a new text file to save predictions
        predPoints = open(filename, 'w')  
        predPoints.write('#PREDICTED POINTS\n')
        predPoints.write('frames: ' + str(self.total_frames) + '\n')
        predPoints.write('predictors: ' + str(len(predictor_name)) + '\n')
        predPoints.write('point_kinds: ' + str(self.point_kinds) + '\n')
        
        #Save predictors name
        for i in range(0,len(predictor_name)):
            predPoints.write(predictor_name[i] + '\n')
    
        predPoints.write('#frame, predictor, pointKind, row, column, confidence\n')
    
        #Save predictions
        for frame in range(0, self.total_frames):
            for pred in range(0, len(predictor_name)):
                for pointK in range(0, self.point_kinds):
                    predPoints.write(str(frame) + ',' + str(pred) + ',' + str(pointK) + ',' +
                        str(int(self.predictions[frame][pred][pointK][0])) + ',' +
                        str(int(self.predictions[frame][pred][pointK][1])) + ',' +
                        str(self.predictions[frame][pred][pointK][2]) + '\n')
                        
        predPoints.close()
        print 'Predictions have been saved to ', filename

    def show(self):
        #A method for debugging. Displays the current frame
        if self.img_current != None:
            self.img_current.show()

    def set_frame(self,frame):
        #Sets the current frame and loads the corresponding image
        #The bounds allow looping through each image to work better
        self.current_frame = frame
        if self.current_frame < 0:
            self.current_frame = 0 
        if self.current_frame > self.total_frames-1:
            if self.single_img == True:
                self.total_frames = self.current_frame+1
                self.point.resize((self.total_frames,self.point_kinds,2))
                self.point_sources = [[-1 for i in range(self.point_kinds)] for i in range(self.total_frames)]
            else:
                self.current_frame = self.total_frames-1
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
        
    #Method that computes the number of points predicted given numpy array point
    def pointsModified(self):        
        count = 0
        for frame in range(self.total_frames):
            for kind_index in range(self.point_kinds):
                if self.point[frame][kind_index][0] > 0 or self.point[frame][kind_index][1] >0:
                    count += 1
        return count
        
    #Method that computes the number of frames modified
    def framesModified(self):
        count = 0
        for frame in range(0,self.total_frames):
            for kind_index in range(0,self.point_kinds):
                if self.point[frame][kind_index][0] > 0 or self.point[frame][kind_index][1] >0:
                    count += 1
                    break
        return count
