import os, string, dircache, time, shutil, sys
#GUI assets
from Tkinter import *
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
import ttk
#Saving images
import Image, ImageTk
from PIL import Image
#Extracting video frames
import pyglet


'''
Notes:
-button functions will run as soon as button is created if callback includes ()
-GUI span starts in top left
-An anchor is necessary or the image will not fit in the window correctly
-An event is a necessary argument for event-bound items
'''


#--- The second window, user clicks on points ---------------------------------#
class Window2:


    '''Called upon creation'''
    def __init__(self, master, directory, fps):
        #Tkinter screws up file path separators for some reason. Fix this depending on the OS
        directory = directory.replace('/',os.path.sep)
        directory = directory.replace('\\',os.path.sep)

        self.completePath = directory        #Full path to image files
        self.partialPath = self.completePath.split(os.path.sep)[-1] #Path from this script
        self.fileList = dircache.listdir(directory)                  #List of valid and invalid image files

        self.textfileName = self.completePath+os.path.sep+self.partialPath+'.txt'   #The text file to write to
        self.imageDirectory = self.completePath                                     #Directory holding images

        #Create a Dictionary to hold valid images
        self.fileDic = {}
        n = 1
        for image in self.fileList:
            if '.png' in image or '.PNG' in image  \
            or '.jpg'in image or '.JPG' in image   \
            or '.bmp' in image or '.BMP' in image  \
            or '.gif' in image or '.GIF' in image:
                self.fileDic[str(n)] = image
                n = n + 1

        #Create a file for reading/writing point coordinates
        fo = open(self.textfileName,'a')
        fo.close()

        self.fps = fps                      #Frames per second
        self.currentFrame = StringVar()     #Currently displayed frame
        self.currentFrame.set(1)
        self.totalFrames = len(self.fileDic)   #Total number of frames
        self.dotType = StringVar()          #Type of dot to be plotted
        self.comment = StringVar()          #Newest comment to be stored
        self.comment.set('comment')

        #Initialize the window and hotkeys
        self.createGUI(master)
        self.createHotkeys(master)
        self.dotType.set('LF')

        #Load the first frame
        self.setFrame(0)


    '''Initializes the window and creates all the gadgets'''
    def createGUI(self,master):
        #Set up the application window
        self.frame = Frame(master)
        master.title('ChamView')
        self.frame.grid(columnspan=8,rowspan=5)

        #Quit button
        self.quitB = Button(master,text='QUIT',command = master.quit)
        self.quitB.grid(column=8,row=1)
        #Previous button
        self.prevB = Button(master, text = 'PREV [A]',command = self.Prev)
        self.prevB.grid(column=4,row=5)
        self.prev10B = Button(master, text = 'PREV10',command = self.Prev10)
        self.prev10B.grid(column=3,row=5)
        self.prev100B = Button(master, text = 'PREV100',command = self.Prev100)
        self.prev100B.grid(column=2,row=5)
        #First button
        self.firstB = Button(master, text = 'FIRST',command = self.First)
        self.firstB.grid(column=1,row=5)
        #Next button
        self.nextB = Button(master,text='NEXT [D]',command = self.Nxt)
        self.nextB.grid(column=5,row=5)
        self.next10B = Button(master, text = 'NEXT10',command = self.Nxt10)
        self.next10B.grid(column=6,row=5)
        self.next100B = Button(master, text = 'NEXT100',command = self.Nxt100)
        self.next100B.grid(column=7,row=5)
        #Last button
        self.lastB = Button(master,text='LAST',command = self.Last)
        self.lastB.grid(row=5,column=8)
        #Clear all of points button
        self.clearB = Button(master,text='CLEAR ALL',command = self.ClearAll)
        self.clearB.grid(column=7,row=1,sticky=E)
        #Clear frame of points button
        self.clearFrameB = Button(master,text='CLEAR FRAME',command=self.ClearFrame)
        self.clearFrameB.grid(column=6,row=1,sticky=E)
        #Rewind button
        self.rewB = Button(master,text = 'REW. [I]',command = self.Rewind)
        self.rewB.grid(row=4,column=3)
        #Pause button
        self.pauseB = Button(master,text='PAUSE [O]',command=self.Pause)
        self.pauseB.grid(row=4,column=4,columnspan=2)
        #Play button
        self.playB = Button(master,text='PLAY [P]',command=self.Play)
        self.playB.grid(row=4,column=6)

        #Current frame label
        self.numLab = Label(master,textvariable = self.currentFrame)
        self.numLab.grid(column=1,row=1,sticky=W)
        #Shows what kind of label/point is currently selected
        self.dotLab = Label(master,textvariable=self.dotType)
        self.dotLab.grid(column=2,row=1)
        #Comment box
        self.commentInput = Entry(master, bd=5, textvariable=self.comment, width=40)
        self.commentInput.grid(column=3,row=1, columnspan=2)
        #Bind return key for comment box
        self.commentInput.bind('<KeyPress-Return>',self.saveComment)
        #Shows directory
        self.dirLab = Label(master,text=self.imageDirectory)
        self.dirLab.grid(row=4,column=1,sticky=W)
        #Shows file with point coords
        self.fileLab = Label(master,text = self.partialPath+'.txt')
        self.fileLab.grid(row=4,column=8,sticky=E)
        #To display the current frame image
        self.canv = Canvas(master)
        self.canv.grid(column=1,row=2,columnspan = 8, rowspan = 2)

        #allow window to resize properly
        #master.columnconfigure(0,weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=1)
        master.columnconfigure(3, weight=1)
        master.columnconfigure(4, weight=1)
        master.columnconfigure(5, weight=1)
        master.columnconfigure(6, weight=1)
        master.columnconfigure(7, weight=1)
        master.columnconfigure(8, weight=1)
        #master.rowconfigure(0,weight=1)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=3)
        master.rowconfigure(3, weight=3)
        master.rowconfigure(4, weight=1)
        master.rowconfigure(5, weight=1)


    '''Sets the function hotkeys'''
    def createHotkeys(self,master):
        #Playback hotkeys
        master.bind_all('<a>', self.Prev)
        master.bind_all('<A>', self.Prev)
        master.bind_all('<d>', self.Nxt)
        master.bind_all('<d>', self.Nxt)
        master.bind_all('<p>', self.Play)
        master.bind_all('<o>', self.Pause)
        master.bind_all('<i>',self.Rewind)
        master.bind_all('<s>',self.SaveAll)
        #Dot type hotkeys
        master.bind_all('1', self.changeDotType)
        master.bind_all('2', self.changeDotType)
        master.bind_all('3', self.changeDotType)
        master.bind_all('4', self.changeDotType)
        master.bind_all('5', self.changeDotType)
        master.bind_all('6', self.changeDotType)
        master.bind_all('7', self.changeDotType)
        master.bind_all('8', self.changeDotType)


    '''Changes the type of point to be plotted based on the key that was hit'''
    def changeDotType(self,event):
        if event.keysym == '1': self.dotType.set('LF')
        if event.keysym == '2': self.dotType.set('RF')
        if event.keysym == '3': self.dotType.set('LB')
        if event.keysym == '4': self.dotType.set('RB')
        if event.keysym == '5': self.dotType.set('GS')
        if event.keysym == '6': self.dotType.set('GE')
        if event.keysym == '7': self.dotType.set('S/V')
        if event.keysym == '8': self.dotType.set('Cm')


    '''Writes the current comment to file'''
    def saveComment(self,event=''):
        comment = self.comment.get()
        comment = comment.strip()
        fo = open(self.textfileName,'a')
        stri = 'COM:'+self.currentFrame.get()+':'+comment
        fo.write(stri+'\n')
        fo.close()


    '''Changes the main display image to a specified frame'''
    def setFrame(self,count):
        #Did we go before the first or after the last frame?
        self.currentFrame.set(count)
        if int(self.currentFrame.get()) < 1:
            self.currentFrame.set(1)
        elif int(self.currentFrame.get()) > self.totalFrames:
            self.currentFrame.set(self.totalFrames)
        #Load the image
        imageFile = self.imageDirectory+os.path.sep+self.fileDic[self.currentFrame.get()]
        self.photo = ImageTk.PhotoImage(Image.open(imageFile))
        #Fit the canvas to the image
        self.canv.config(width = self.photo.width(),height = self.photo.height())
        self.obj = self.canv.create_image((0,0),
                                          image = self.photo,
                                          tags = (self.currentFrame.get()+'n'),anchor = NW)
        #Bind the left mouse button to the canvas
        self.canv.tag_bind(self.obj,'<Button-1>',self.makeCircle)
        #If the frame has points already, draw them
        if self.CheckCircles(self.currentFrame.get()+'n'):
            self.DrawCircles(self.currentFrame.get()+'n')


    '''Change the current frame by a given number'''
    def advanceFrame(self,count):
        self.setFrame(int(self.currentFrame.get())+count)


    '''The buttons and shortcuts to change frame'''
    def Nxt(self,event=''):self.advanceFrame(1)
    def Nxt10(self):self.advanceFrame(10)
    def Nxt100(self):self.advanceFrame(100)
    def Prev(self,event=''):self.advanceFrame(-1)
    def Prev10(self):self.advanceFrame(-10)
    def Prev100(self):self.advanceFrame(-100)
    def First(self):self.setFrame(1)
    def Last(self):self.setFrame(self.totalFrames)


    '''Animates the video sequence normally'''
    def Play(self,event=''):
        #stop other play/pause
        self.go = False
        self.playing = False
        self.rewing = False
        #allow Play while loop to run
        self.go = True
        self.playing = True
        #will run while not at max frame number, self.go controlled by Pause
        while int(self.currentFrame.get()) < self.totalFrames and self.go == True and \
                            self.playing==True and self.rewing==False:
            #delay between frames according to fps
            time.sleep(1.0/self.fps)
            #Draw the next frame
            self.canv.update()
            self.advanceFrame(1)
        #Stop playback
        self.go = False
        self.playing = False


    '''Pauses the video sequence, stops play/rewind loops from running'''
    def Pause(self,event=''):
        self.go = False
        self.playing = False
        self.rewing = False


    '''Animates the video sequence in reverse'''
    def Rewind(self,event=''):
        #stop other play/pause
        self.go = False
        self.playing = False
        self.rewing = False
        #allow Rewind while loop to run
        self.go = True
        self.rewing = True
        #will run while not at min frame number, self.go controlled by Pause
        while int(self.currentFrame.get()) > 1 and self.go == True and \
                self.playing == False and self.rewing == True:
            #delay between frames according to fps
            time.sleep(1.0/self.fps)
            #Draw the next frame
            self.canv.update()
            self.advanceFrame(-1)
        #Stop playback
        self.go = False
        self.rewing = False


    '''Draw circle on click and record coordinates in file'''
    def makeCircle(self,event):
        label = self.dotType.get()
        if len(label) == 0: return

        #Get the cicle color
        circFill = ''
        if label == 'LF': circFill = 'yellow'
        if label == 'RF': circFill = 'orange'
        if label == 'LB': circFill = 'blue'
        if label == 'RB': circFill = 'turquoise'
        if label == 'GS': circFill = 'plum'
        if label == 'GE': circFill = 'purple'
        if label == 'S/V': circFill = 'red'
        if label == 'Cm': circFill = 'lime green'

        #Coordinates are two opposite corners of circle
        circId = self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                        fill = circFill)

        #Tag item so it can be used (deleted) later
        self.canv.itemconfigure(circId,tags=(str(circId)+label))

        #Bind item to unclick
        self.canv.tag_bind(str(circId)+label,'<Button-1>',self.deleteCircle)

        #Write coordinates and ID of circle to file
        fo = open(self.textfileName,'a')
        stri = (self.currentFrame.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                +':'+str(event.y+3)+':'+str(circId)+label)
        fo.write(stri+'\n')
        fo.close()


    '''Deletes circles when they are clicked'''
    def deleteCircle(self,event):
        #Mouse x/y coordinates
        x,y = self.canv.canvasx(event.x),self.canv.canvasy(event.y)
        #gets tag of the closest item
        closeItem = self.canv.find_closest(x,y)[0]
        tags = self.canv.gettags(closeItem)

        #open original file
        fin = open(self.textfileName,'r')
        #create temporary file to write new lines to
        fout = open('temp.txt','w')
        for line in fin:
            #last part of each line is circle tag(id)
            lineLst = line.split(':')
            if lineLst[-1][0:-1] == tags[0]:
                self.canv.delete(tags[0])
            else:
                #if item not deleted, line is written to temp file
                fout.write(line)
        fin.close()
        fout.close()

        #original file is wiped clean
        fin2 = open(self.textfileName,'w')
        #newly created temp file to read from
        fout2 = open('temp.txt','r')
        #Copy lines from temp file to original file
        for line2 in fout2:
            fin2.write(line2)
        fin2.close()
        fout2.close()


    '''Removes all points from the current frame'''
    def ClearFrame(self):
        #open original file
        fin = open(self.textfileName,'r')
        #create temporary file to write new lines to
        fout = open('temp.txt','w')

        for line in fin:
            lineLst = line.split(':')
            if lineLst[0] == (self.currentFrame.get()+'n'):
                self.canv.tag_raise((self.currentFrame.get()+'n'))
            else:
                #if item not deleted, line is written to temp file
                fout.write(line)
        fin.close()
        fout.close()

        #original file is wiped clean
        fin2 = open(self.textfileName,'w')
        #newly created temp file to read from
        fout2 = open('temp.txt','r')
        #Copy lines from temp file to original file
        for line2 in fout2:
            fin2.write(line2)

        fin2.close()
        fout2.close()


    '''Renders circles on the current frame'''
    def DrawCircles(self,tag):
        #Open the file and read each line
        fo = open(self.imageDirectory+os.path.sep+self.partialPath+'.txt','r')
        for line in fo:
            lineLst = line.split(':')
            if lineLst[0] == tag:
                #Get the circle color
                circFill = ''
                if 'LF'in lineLst[-1]: circFill = 'yellow'
                if 'RF'in lineLst[-1]: circFill = 'orange'
                if 'LB'in lineLst[-1]: circFill = 'blue'
                if 'RB'in lineLst[-1]: circFill = 'turquoise'
                if 'GS'in lineLst[-1]: circFill = 'plum'
                if 'GE'in lineLst[-1]: circFill = 'purple'
                if 'S/V'in lineLst[-1]: circFill = 'red'
                if 'Cm'in lineLst[-1]: circFill = 'lime green'
                if len(circFill) == 0:continue
                #tag item with ID of original circle so it can be used (deleted) later
                circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                fill = circFill)
                self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.deleteCircle)
        fo.close()


    '''Checks if current frame has any points in the file'''
    def CheckCircles(self,tag):
        fo = open(self.textfileName,'r')
        for line in fo:
            lineLst = line.split(':')
            if lineLst[0] == tag:
                fo.close()
                return True
        fo.close()
        return False


    '''Clears the file of all points'''
    def ClearAll(self):
        #Clear current frame so as to not confuse the user
        self.canv.tag_raise((self.currentFrame.get()+'n'))
        #Wipes file of all points
        fo = open(self.textfileName,'w')
        fo.close()


    '''Saves the current annotated frame as a png'''
    def SaveImg(self,event=''):
        #make a new directory to put dotted frames in
        dirName = self.imageDirectory+os.path.sep+'annotated'
        if not os.path.exists(dirName): os.mkdir(dirName)
        fileName = dirName+os.path.sep+self.fileDic[self.currentFrame.get()]
        #Render and capture the current frame
        self.canv.update()
        x0 = self.canv.winfo_rootx()
        y0 = self.canv.winfo_rooty()
        x1 = x0 + self.canv.winfo_width()
        y1 = y0 + self.canv.winfo_height()
        offset1 = 0
        offset2 = 0
        #Grab area of the screen and save is using PIL
        im = ImageGrab.grab((x0-offset1, y0-offset1, x1+offset2,y1+offset2))
        im.save(fileName)


    '''Saves all frames as pngs'''
    #This is currently not working, messes with text file somehow
    def SaveAll(self,event=''):
        pass
#        #stop other play/pause
#        self.go = False
#        dirName = self.imageDirectory+os.path.sep+'annotated'
#        #make a new directory to put dotted frames in
#        if not os.path.exists(dirName): os.mkdir(dirName)
#        #allow saveAll while loop to run
#        self.go = True
#        #will run while not at max frame number, self.go controlled by Pause
#        while int(self.currentFrame.get()) < self.totalFrames and self.go == True:
#            fileName = dirName+os.path.sep+self.fileDic[self.currentFrame.get()]
#            self.canv.update()
#            x0 = self.canv.winfo_rootx()
#            y0 = self.canv.winfo_rooty()
#            x1 = x0 + self.canv.winfo_width()
#            y1 = y0 + self.canv.winfo_height()
#            offset1 = 0
#            offset2 = 0
#            im = ImageGrab.grab((x0-offset1, y0-offset1, x1+offset2,y1+offset2))
#            im.save(fileName)
#        self.go = False


#--- The first window, user prompted for directory ----------------------------#
class Window1:

    '''Called upon creation, creates GUI'''
    def __init__(self,master):
        self.openSecondWindow = False       #Whether to continue after this window closes
        self.video = StringVar()            #Chosen video
        self.video.set('')
        self.fps = IntVar()                 #FPS of video
        self.fps.set(30)
        self.directory = StringVar()        #Directory to load images from
        self.directory.set(os.getcwd())

        #Create the window
        self.master = master
        self.master.geometry('410x150+200+200')
        self.frame = Frame(master)
        self.master.title('ChamView')
        self.frame.grid(rowspan=5,columnspan=3)

        #Label for the video to convert
        self.vidLabel1 = Label(self.frame,text='Convert video:')
        self.vidLabel1.grid(row=1,column=1)
        self.vidLabel2 = Entry(self.frame,textvariable=self.video)
        self.vidLabel2.grid(row=1,column=2)

        #Label for current directory
        self.dirLabel1 = Label(self.frame,text='Load images from:')
        self.dirLabel1.grid(row=4,column=1)
        self.dirLabel2 = Entry(self.frame,textvariable=self.directory)
        self.dirLabel2.grid(row=4,column=2)

        #Label for FPS
        self.fpsLabel1 = Label(self.frame,text='Video FPS:')
        self.fpsLabel1.grid(row=5,column=1)
        self.fpsLabel2 = Entry(self.frame,textvariable=self.fps)
        self.fpsLabel2.grid(row=5,column=2)

        #A dummy label to act as a spacer
        self.dummyLabel = Label(self.frame)
        self.dummyLabel.grid(row=3,column=1)

        #Browse and Proceed buttons for video and frames
        self.buttonChooseVid = Button(self.frame,text = 'Browse',command=self.chooseVideo)
        self.buttonChooseVid.grid(row=1,column=3)
        self.buttonLoadVid = Button(self.frame,text = 'Extract Frames',command=self.extract)
        self.buttonLoadVid.grid(row=2,column=3)
        self.buttonChooseDir = Button(self.frame,text = 'Browse',command=self.chooseDir)
        self.buttonChooseDir.grid(row=4,column=3)
        self.buttonLoadDir = Button(self.frame,text = 'Select Points',command=self.proceed)
        self.buttonLoadDir.grid(row=5,column=3)


    '''Opens a window to allow the user to select a video to process'''
    def chooseVideo(self):
        myFile = tkFileDialog.askopenfilename(parent = root,initialdir=os.getcwd(),title='Open video')
        if len(myFile) > 0: self.video.set(myFile)


    '''Opens a window to allow the user to select a directory to load image files from'''
    def chooseDir(self):
        myDir = tkFileDialog.askdirectory(parent = root,
            initialdir=self.directory.get(),title='Select a folder')
        if len(myDir) > 0: self.directory.set(myDir)


    ''' Determines whether or not the current directory is valid
        -Returns 'bad dir' if the directory doesn't exist
        -Returns 'no img' if no valid images were found in the directory
        -Otherwise, returns 'good'
    '''
    def checkDir(self):
        directory = self.directory.get().strip()
        goodDirectory = False
        #Does the directory exist?
        if not os.path.isdir(directory): return 'bad dir'
        #Check if there's a valid picture file
        self.picList = dircache.listdir(directory)
        for pic in self.picList:
            if '.png' in pic or '.PNG' in pic  \
            or '.jpg'in pic or '.JPG' in pic   \
            or '.bmp' in pic or '.BMP' in pic  \
            or '.gif' in pic or '.GIF' in pic:
                goodDirectory = True
        if goodDirectory == True: return 'good'
        return 'no img'


    '''Determines whether the inputted FPS is valid, returns True or False'''
    def checkFPS(self):
        if self.fps.get() > 0:
            return True
        else:
            return False


    ''' Extracts frames from the specified video file and saves them in a
        directory of the same name
    '''
    def extract(self, source):
        extractStart = 0    #Frame extraction start and end time
        extractEnd = 0
        vframe = None       #The current frame
        time = 0            #Timestamp of the current frame
        destination = os.getcwd()+os.path.sep\
                      +os.path.basename(source).split('.')[0]#Name of folder to save frames in

        #Load in the video file
        try:
            sourceVid = pyglet.media.load(source)
        except pyglet.media.MediaException:
            #The file format isn't supported
            tkMessageBox.showerror('ChamView', 'Error: video format not supported')
            return
        except IOError:
            #Error reading in the file
            tkMessageBox.showerror('ChamView', 'Error: file not found')
            return
        except:
            #Some other Pyglet error
            tkMessageBox.showerror('ChamView','Error: Pyglet failure')
            return

        #Is the file a video?
        if sourceVid.video_format == None:
            tkMessageBox.showerror('ChamView', 'Error: invalid video file')
            return

        #Prompt for extraction start and end time
        extractStart = tkSimpleDialog.askfloat('ChamView','Extraction start time (seconds)',
                        initialvalue=0.0,minvalue=0,maxvalue=sourceVid.duration)
        extractEnd = tkSimpleDialog.askfloat('ChamView','Extraction end time (seconds)',
                    initialvalue=sourceVid.duration,minvalue=extractStart,maxvalue=sourceVid.duration)

        #Create a directory to save frames in
        try:
            os.mkdir(destination)
        except OSError:
            #Directory already exists. Apend a number on the back and retry
            i = 1
            while os.path.isdir(destination+'('+str(i)+')'):
                i = i + 1
            destination = destination+'('+str(i)+')'
            os.mkdir(destination)

        tkMessageBox.showinfo('ChamView','Frames will be saved in ['+destination+']')

        try:
            #Skip ahead to the start time. Otherwise, start at the first frame
            if extractStart > 0:
                while time < extractStart:
                    vframe = sourceVid.get_next_video_frame()
                    time = sourceVid.get_next_video_timestamp()
            else:
                vframe = sourceVid.get_next_video_frame()

            #Save each frame until we run out of frames or reach the end time
            frameCount = 1
            while vframe != None and time <= extractEnd:
                imageData = vframe.get_image_data()
                pixels = imageData.get_data(imageData.format,imageData.pitch*-1)
                imageData.set_data(imageData.format,imageData.pitch,pixels)
                imageData.save(destination+os.path.sep+'frame'+str(frameCount)+'.png')
                time = sourceVid.get_next_video_timestamp()
                vframe = sourceVid.get_next_video_frame()
                frameCount += 1

            tkMessageBox.showinfo('ChamView','     Success      ')
        except:
            tkMessageBox.showerror('ChamView','Error: Pyglet failure')
            #Rid of the empty directory that we created
            os.rmdir(destination)


    ''' Called when the 'Select Points' button is clicked. Proceeds to the next
        window to select points or shows an error message if something's wrong.
    '''
    def proceed(self):
        if self.checkDir() == 'bad dir':
            tkMessageBox.showerror('ChamView', 'Error: directory not found')
        elif self.checkDir() == 'no img':
            tkMessageBox.showerror('ChamView', 'Error: no valid images found')
        elif self.checkFPS() == False:
            tkMessageBox.showerror('ChamView', 'Error: FPS must be at least 1')
        else:
            #Mark that the second window should be opened
            self.openSecondWindow = True
            self.master.destroy()


#--- The code that runs upon execution ----------------------------------------#

#Open the first window to choose a directory
root = Tk()
app1 = Window1(root)
root.mainloop()

#Get image directory and video FPS from the first window
directory = app1.directory.get().strip()
fps = app1.fps.get()

#Open the second window, which is ChamView, if the 'Select Points' button was clicked
if app1.openSecondWindow:
    root2 = Tk()
    app2 = Window2(root2,directory,fps)
    root2.mainloop()

