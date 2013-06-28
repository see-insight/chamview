#
# Editted by Aaron Beckett
#
#

import os
from Grammar import Chooser
from numpy import *
from Tkinter import *
import Tix
import tkMessageBox, tkFileDialog
import ttk
from PIL import Image, ImageTk
import basicgui_supportclasses as support


class BasicGui(Chooser):

    '''----- Instance Variables ----
    master                |
    imstack               |
    predicted             |
    predictor_name        |
    currentFrame          |
    totalFrame            |
    photo                 |
    pointKind             |
    added                 |
    deleted[]             |
    editedPointKinds      |
    showPredictions       |
    selectedPredictions[] |
    activePoint[]         |
    madePointkindList     |
    madePredictorList     |
    filledSelectedPredList|
    '''

    #Size of circles drawn onscreen
    circle_radius = 3
    #How large each frame should be scaled to
    canvas_width = 800
    canvas_height = 600

    def setup(self):
        '''Set instance variables and create the GUI.'''
        self.master = Tix.Tk()
#        self.master = Tk()  # use if Tix is not available
        #Frame and point info
        self.currentFrame = StringVar()
        self.totalFrame = StringVar()
        self.currentTag = StringVar()
        self.photo = None
        self.pointKind = 0
        self.added = 0      # number of new point types added during cycle
        self.deleted = []   # indices of point types deleted during cycle
        self.editedPointKinds = False   # true if point kinds were edited in the update loop
        self.saveFile = ''    # name of file to save to
        self.zoom_factor = 3
        #Choosing a prediction to use
        self.showPredictions = True     # yes or no to automatically show point predictions
        self.selectedPredictions = []    # store where point came from last frame for each point kind (-1:user, 0 to # of predictors: predictor index)
        self.activePoint = [-1,0,0] # [predictor index, x, y] of selected predictor (to be stored in imstack.point if frame/point type is changed)
        #Intitialize GUI, but don't show it yet
        self.madePointkindList = False
        self.madePredictorList = False
        self.filledSelectedPredList = False
        self.setActivePredictors = False
        self.createGui()
        self.createKeyBindings()

    def teardown(self):
        '''Close the GUI window.'''
        self.imstack.exit = True
#        self.save()
        self.end_update_loop()

    def choose(self,stack,predicted,predictor_name):
        '''Enter a new GUI update loop.'''
        #Get the imagestack and predicted points
        self.imstack = stack
        self.predicted = predicted
        self.predictor_name = predictor_name
        if not self.setActivePredictors:
            self.activePredictors = predictor_name[:]
            self.displayedPredictors = predictor_name[:]
            self.setActivePredictors = True
        self.predictedFrame = self.imstack.current_frame
        #Fill the pointlist with point kinds available for use if it hasn't been
        if not self.madePointkindList:self.fillPointkindList()
        if not self.madePredictorList:self.fillPredictorList()
        if self.editedPointKinds:
            self.added = 0
            self.deleted = []
            self.editedPointKinds = False

        #set activePoint[]
        self.activePoint[0] = self.imstack.point_sources[self.imstack.current_frame][self.pointKind]
        self.activePoint[1] = self.imstack.point[self.imstack.current_frame,self.pointKind,0]
        self.activePoint[2] = self.imstack.point[self.imstack.current_frame,self.pointKind,1]
#        print self.imstack.point[self.imstack.current_frame,self.pointKind,0], ',', self.imstack.point[self.imstack.current_frame,self.pointKind,1]
#        print '****ACTIVE POINT after choose:****\n', self.activePoint

        #Draw new frame and predictions
        self.drawCanvas()
        #Show the window and get user input
        self.master.mainloop()

    def fillPointkindList(self):
        '''List each point kind in the point kind Listbox'''
        #We don't have to fill the list again after this
        self.madePointkindList = True
        #For every point kind in our imagestack, create an entry in the list
        #and bind the first 9 to the number keys on the keyboard
        for i in range(0,self.imstack.point_kinds):
            self.pointlist.insert(END,self.imstack.point_kind_list[i])
            if i+1 <= 9: self.master.bind_all(str(i+1),self.setPointKind)
        self.pointKind = 0
        self.updatePointKind()
        #Fill the list of predictor choices
        if not self.filledSelectedPredList: self.updateSelectedPredList()

    def fillPredictorList(self):
        '''List each available predictor in the predictor Listbox'''
        self.madePredictorList = True
        for pred in self.predictor_name:
            self.predlist.insert(END,pred)
        self.updateActivePred()

#****** Set-Up GUI ******

    def createGui(self):
        '''Create Tkinter GUI environment for chamview'''
        #Set up application window
        self.master.title('Tkinter GUI Chooser')
        self.master.protocol('WM_DELETE_WINDOW',self.quit)
        #Set up top menu: File Help
        self.topmenu = Menu(self.master)
        self.master.config(menu=self.topmenu)
        self.filemenu = Menu(self.topmenu)
        self.topmenu.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label='New', command=self.new)
        self.filemenu.add_command(label='Open', command=self.open)
        self.filemenu.add_command(label='Save As', command=self.save_as)
        self.filemenu.add_command(label='Save', command=self.save)
        self.filemenu.add_separator()
        zoommenu = Menu(self.filemenu)
        self.filemenu.add_cascade(label='Zoom Factor', menu=zoommenu)
        zoommenu.add_command(label='4',command=lambda x=4:self.set_zoom(x))
        zoommenu.add_command(label='3.5',command=lambda x=3.5:self.set_zoom(x))
        zoommenu.add_command(label='3',command=lambda x=3:self.set_zoom(x))
        zoommenu.add_command(label='2.5',command=lambda x=2.5:self.set_zoom(x))
        zoommenu.add_command(label='2',command=lambda x=2:self.set_zoom(x))
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Exit', command=self.quit)
        self.topmenu.add_command(label='Help', command=self.showHelp)
        #Grid manager:
        #       Annotation buttons, point kinds, and predictors on left
        #       Image and navigation buttons on right
        self.frameL = Frame(self.master,height=BasicGui.canvas_height)
        self.frameL.pack(side=LEFT,fill=Y)
        self.frameR = Frame(self.master)
        self.frameR.pack(side=LEFT,fill=BOTH)
        self.frameR.config(borderwidth=3,relief=GROOVE)

        ###frameL###
        #Tix Balloon for hover-over help
        self.balloon = Tix.Balloon(self.master)
        #Separator line
        self.lineframe = Frame(self.frameL, height=15)
        self.lineframe.grid(row=0,column=0,columnspan=3,rowspan=1)
        #Annotation frame
        self.aframe = Frame(self.frameL)
        self.aframe.grid(row=1,column=0,columnspan=3,rowspan=1,pady=15)
        #Delete button
        self.button_del = Button(self.aframe,text='Delete',command=self.delete)
        self.balloon.bind_widget(self.button_del,
            balloonmsg='Deletes current point kind\'s selection from current frame.')
        self.button_del.grid(row=0,column=0,columnspan=2,ipadx=15)
        #Clear Frame button
        self.button_clearf = Button(self.aframe,text='Clear Frame',command=self.clearFrame)
        self.balloon.bind_widget(self.button_clearf,
            balloonmsg='Deletes all points on the current frame.')
        self.button_clearf.grid(row=1,column=0,sticky='WE')
        #Clear All button
        self.button_cleara = Button(self.aframe,text='Clear All Frames',command=self.clearAll)
        self.balloon.bind_widget(self.button_cleara,
            balloonmsg='Deletes all points from all frames.')
        self.button_cleara.grid(row=1,column=1,sticky='WE')
        #Save and Help frame
        self.shframe = Frame(self.frameL)
        self.shframe.grid(row=2,column=0,columnspan=3,rowspan=1,pady=5)
        #Save button
        self.button_save = Button(self.shframe,text='Save Points',command=self.save)
        self.balloon.bind_widget(self.button_save,
            balloonmsg='Saves all point data to text file.')
        self.button_save.grid(row=0,column=0,sticky=E)
        #Help button
        self.button_help = Button(self.shframe,text='Help',command=self.showHelp)
        self.balloon.bind_widget(self.button_help,
            balloonmsg='Display help window.')
        self.button_help.grid(row=0,column=1,sticky=W)
        #Point Types Label and edit button
        self.pt_label = Label(self.frameL,text='Point Types',height=4,anchor=S)
        self.pt_label.grid(row=3,column=1)
        self.pt_edit = Button(self.frameL,text='Edit',command=self.pointKindEdit)
        self.balloon.bind_widget(self.pt_edit,
            balloonmsg='Click to edit the available point kinds.')
        self.pt_edit.grid(row=3,column=2,sticky=S)
        #Listbox used to select point kind
        self.pointlist = Listbox(self.frameL,width=15,height=10,selectmode=SINGLE)
        self.pointlist.grid(row=4,column=1,columnspan=2)
        self.pt_scroll = Scrollbar(self.frameL,orient=VERTICAL)
        self.pt_scroll.grid(row=4,column=0,sticky=NS)
        self.pt_scroll.config(command=self.pointlist.yview,width=15)
        self.pointlist.config(yscrollcommand=self.pt_scroll.set)
        self.pointlist.bind('<<ListboxSelect>>',self.setPointKind)
        self.pointlist.focus()
        #Clear Point Kind button
        self.button_clearp = Button(self.frameL,text='Clear Point Kind',command=self.clearPointKind)
        self.balloon.bind_widget(self.button_clearp,
            balloonmsg='Clears selected point kind from all frames.')
        self.button_clearp.grid(row=5,column=1,columnspan=2)
        #Predictors Label and edit button
        self.pd_label = Label(self.frameL,text='Predictors',height=3,anchor=S)
        self.pd_label.grid(row=6,column=1)
        self.pd_info = Button(self.frameL,text='Edit',command=self.predictorsInfo)
        self.balloon.bind_widget(self.pd_info,
            balloonmsg='NOT IMPLEMENTED--will display predictor stats.')
        self.pd_info.grid(row=6,column=2,sticky=S)
        #Listbox used to show predictors
        self.predlist= Listbox(self.frameL,width=15,height=10,selectmode=SINGLE)
        self.predlist.grid(row=7,column=1,columnspan=2)
        self.pd_scroll = Scrollbar(self.frameL,orient=VERTICAL)
        self.pd_scroll.grid(row=7,column=0,sticky=NS)
        self.pd_scroll.config(command=self.predlist.yview,width=15)
        self.predlist.config(yscrollcommand=self.pd_scroll.set)
        self.predlist.bind('<<ListboxSelect>>',self.setActivePred)

        ###frameR###
        #Canvas to display the current frame
        self.canvas = Canvas(self.frameR,width=BasicGui.canvas_width,
            height=BasicGui.canvas_height)
        self.canvas.pack()
        #Status bar Frame
        self.stat_frame = Frame(self.frameR)
        self.stat_frame.pack(fill=X)
        #Status Bar
        self.temporary_statusbar = support.StatusBar(self.stat_frame)
        self.temporary_statusbar.pack(fill=X)
        self.format = 'Image: %s    Point Kind: %s      Point Position: X: %5.1d   Y: %5.1d'
        self.temporary_statusbar.set(self.format, 'none', 'default', 0, 0)
        #frame counter Frame
        self.fframe = Frame(self.frameR)
        self.fframe.pack()
        #frame label
        label = Label(self.fframe,text='Frame')
        label.grid(row=0,column=0,pady=10,sticky=E)
        label.config(borderwidth=0)
        #Current frame label
        self.label_goto = Entry(self.fframe,width=3,textvariable=self.currentFrame)
        self.label_goto.grid(row=0,column=1)
        self.label_goto.config(borderwidth=2,relief=SUNKEN)
        self.label_goto.bind("<KeyRelease-Return>", self.gotoFrame)
        #Total Frames
        label_framenum = Label(self.fframe,textvariable=self.totalFrame)
        label_framenum.grid(row=0,column=2,sticky=W)
        label_framenum.config(borderwidth=0)
        Label(self.fframe,text='\t\t').grid(row=0,column=3)
        #Frame Tag
        label = Label(self.fframe,text='Label')
        label.grid(row=0,column=4,sticky=E)
        self.tag = Entry(self.fframe,textvariable=self.currentTag)
        self.tag.grid(row=0,column=5,sticky=W)
        self.tag.config(borderwidth=2,relief=SUNKEN)
        self.tag.bind("<FocusIn>", lambda e: self.tag.grab_set())
        self.tag.bind("<KeyRelease-Return>", lambda e: self.master.focus_set())
        self.tag.bind("<FocusOut>", lambda e: self.tag.grab_release())
        #Search Tags
        search_button = Button(self.fframe,text='GoTo',command=self.searchFrames)
        search_button.grid(row=0,column=6)
        #Navigation frame
        self.navframe = Frame(self.frameR)
        self.navframe.pack()
        #First Frame button
        self.nav_button = Button(self.navframe,text='First',
                            command=lambda x=0: self.navigate(x))
        self.nav_button.grid(row=0,column=0,padx=7)
        #Previous 100 button
        self.nav_button = Button(self.navframe,text='-100',
                            command=lambda x=-100: self.navigate(x))
        self.nav_button.grid(row=0,column=1,padx=7)
        #Previous 10 button
        self.nav_button = Button(self.navframe,text='-10',
                            command=lambda x=-10: self.navigate(x))
        self.nav_button.grid(row=0,column=2,padx=7)
        #Previous button
        self.nav_button = Button(self.navframe,text='Previous',command=self.prev)
        self.nav_button.grid(row=0,column=3,padx=7)
        #Next button
        self.nav_button = Button(self.navframe,text='Next',command=self.next)
        self.nav_button.grid(row=0,column=4,padx=7)
        #Next 10 button
        self.nav_button = Button(self.navframe,text='+10',
                            command=lambda x=10: self.navigate(x))
        self.nav_button.grid(row=0,column=5,padx=7)
        #Next 100 button
        self.nav_button = Button(self.navframe,text='+100',
                            command=lambda x=100: self.navigate(x))
        self.nav_button.grid(row=0,column=6,padx=7)
        #Last Frame button
        self.nav_button = Button(self.navframe,text='Last',
                            command=lambda x=-1: self.navigate(x))
        self.nav_button.grid(row=0,column=7,padx=7)

#****** Point Kind Functions ******

    def setPointKind(self,event=''):
        self.update_points()
        self.pointlist.select_clear(self.pointKind)
        if event.char == '??':
            #User clicked on the pointlist
            try:
                self.pointKind = int(self.pointlist.curselection()[0])
            except IndexError:
                pass
        else:
            #User hit a key 1-9 on the keyboard
            self.pointKind = int(event.char) - 1
        self.updatePointKind()

    def incPointKind(self,event=''):
        self.update_points()
        self.pointKind = self.pointKind+1
        if self.pointKind > self.imstack.point_kinds-1:
            self.pointKind = 0
        self.updatePointKind()

    def decPointKind(self,event=''):
        self.update_points()
        self.pointKind = (self.pointKind-1)
        if self.pointKind < 0:
            self.pointKind = self.imstack.point_kinds-1
        self.updatePointKind()

    def updatePointKind(self):
        '''Set the pointlist's selection and draw the new pointkind on the frame.'''
        self.pointlist.select_clear(0,END)
        self.pointlist.select_set(self.pointKind)
        self.pointlist.see(self.pointKind)
        self.pointlist.activate(self.pointKind)  # underline
        self.button_clearp.configure(text='Clear '+ self.pointlist.get(self.pointKind))
        self.end_update_loop()

    def pointKindEdit(self,event=''):
        '''Window where the user can add and remove point kinds.'''
        self.editedPointKinds = True    #used to tell predictors if the point kinds were edited
        self.added = 0
        self.deleted = []
        window = support.EditPointKinds(self.master,self.imstack)
        self.added, self.deleted = window.result

        if self.added > 0 or self.deleted != []:
            self.pointlist.delete(0,END)
            self.fillPointkindList()
            self.updateSelectedPredList(self.added,self.deleted)
        else:
            self.editedPointKinds = False
        self.update_points()
        self.end_update_loop()

#****** Predictor Functions ******

    def updateSelectedPredList(self,add=0,deleted=[]):
        '''Update list of which predictors are currently used for which point type
        after the number of point types has been changed.'''
        #-1 corresponds to human input, other nums are the index for a predictor
        #in predictor_name and predicted arrays
        if not self.filledSelectedPredList:
            self.filledSelectedPredList = True   # only need to do this once
            for i in range(0,self.imstack.point_kinds):
                self.selectedPredictions.append(-1)
        else:
            temp = []
            for i in range(len(self.selectedPredictions)):
                if i not in deleted:
                    temp.append(self.selectedPredictions[i])
            self.selectedPredictions = temp
            for n in range(add):
                self.selectedPredictions.append(-1)

    def setActivePred(self,event=''):
        self.predlist.select_clear(self.activePoint[0])
        try:
            self.activePoint[0] = int(self.predlist.curselection()[0])
        except IndexError:
            pass
        self.updateActivePred()

    def cyclePredictions(self,event=''):
        '''Cycle through the predicted points to choose one to save as the point.'''
        if not self.madePointkindList: return
        self.predlist.select_clear(self.activePoint[0])
        if(event.char=='q'):
            self.decActivePred()
        elif(event.char=='e' or event.num==3):
            self.incActivePred()
        self.updateActivePred()

        if self.activePoint[0] != -1:
            # store predicted coordinates in activePoint
            self.activePoint[1] = self.predicted[self.activePoint[0],self.pointKind,0]
            self.activePoint[2] = self.predicted[self.activePoint[0],self.pointKind,1]
        else:
            # no prediction or point data stored
            self.activePoint[1] = 0
            self.activePoint[2] = 0
#        print '****ACTIVE POINT after cyclePredictions:****\n', self.activePoint

        # clear saved data for point because predictions are being examined
        self.selectedPredictions[self.pointKind] = -1
        self.imstack.point[self.imstack.current_frame,self.pointKind,0] = 0
        self.imstack.point[self.imstack.current_frame,self.pointKind,1] = 0
        self.imstack.point_sources[self.imstack.current_frame][self.pointKind] = -1
        self.drawCanvas()

    def incActivePred(self):
        self.activePoint[0] += 1
        if self.activePoint[0] > len(self.predicted)-1:
            self.activePoint[0] = -1
        self.updateActivePred()

    def decActivePred(self):
        self.activePoint[0] -= 1
        if self.activePoint[0] < -1:
            self.activePoint[0] = len(self.predicted)-1
        self.updateActivePred()

    def updateActivePred(self):
        '''Set the predlist's selection.'''
        self.predlist.select_clear(0,END)
        if self.activePoint[0] != -1:
            self.predlist.select_set(self.activePoint[0])
            self.predlist.see(self.activePoint[0])
            self.predlist.activate(self.activePoint[0])  # underline

    def togglePredictions(self,event=''):
        '''Turn the drawing of predicted points on or off.'''
        self.showPredictions = not self.showPredictions
        self.update_points()
        self.end_update_loop()

    def predictorsInfo(self,event=''):
        '''Window displaying accuracy info about each predictor.'''
        print 'basicgui pred lists'
        print self.activePredictors
        print self.displayedPredictors
        window = support.PredictorWindow(self.master,
                                         self.predictor_name,
                                         self.activePredictors,
                                         self.displayedPredictors)
        self.activePredictors, self.displayedPredictors = window.result
        self.end_update_loop()

#****** Key Bindings ******

    def createKeyBindings(self):   # *** here's the problem ***
        self.master.bind('<Down>',self.incPointKind, '+')
        self.master.bind('<Up>',self.decPointKind)
        self.master.bind('<s>',self.incPointKind, '+')
        self.master.bind('<w>',self.decPointKind, '+')
        self.master.bind('<Left>',self.prev)
        self.master.bind('<Right>',self.next)
        self.master.bind('<a>',self.prev)
        self.master.bind('<d>',self.next)
        self.master.bind('<Shift-p>',self.togglePredictions)
        self.master.bind('<q>',self.cyclePredictions)
        self.master.bind('<e>',self.cyclePredictions)
        self.master.bind('<z>',self.zoom_in)
        self.master.bind('<Button-3>',self.cyclePredictions)
        self.master.bind('<Delete>',self.delete)
        self.canvas.bind("<Button-1>",self.onClick)
        self.canvas.bind("<Double-Button-1>",self.onDoubleClick)

#****** Canvas and Point Drawing ******

    def onClick(self,event):
        '''Set the current pointkind's position in the current frame to the mouse
        position and redraw it.'''
        self.store_mouse_position(event)
#        print '****ACTIVE POINT after onClick:****\n', self.activePoint
        self.update_points()
        self.end_update_loop()

    # Refine point (zoom feature)
    def onDoubleClick(self,event):
        '''Set the current pointkind's position in the current frame to the mouse
        position and zoom-in for refinement.'''
        self.store_mouse_position(event)
        self.zoom_in()

    def store_mouse_position(self,event):
        '''Store the x-y coordinates of the mouse in the activePoint'''
        mouseX,mouseY = event.x/self.scale,event.y/self.scale
        self.activePoint[0] = -1 #-1 corresponds to human choice
        self.activePoint[1] = mouseX
        self.activePoint[2] = mouseY

    def zoom_in(self,event=''):
        dialog = support.RefinePoint(self.master,self.imstack.img_current,self.activePoint,self.zoom_factor)
        self.activePoint = dialog.new_point
        self.update_points()
        self.end_update_loop()

    def set_zoom(self,new_factor):
        self.zoom_factor = new_factor

    def drawCanvas(self):
        if (self.selectedPredictions[self.pointKind] != -1 and
        self.imstack.point_empty(self.imstack.current_frame,self.pointKind)):
            i = self.selectedPredictions[self.pointKind]
            x = self.predicted[self.selectedPredictions[self.pointKind],self.pointKind,0]
            y = self.predicted[self.selectedPredictions[self.pointKind],self.pointKind,1]
            self.activePoint[0] = i
            self.activePoint[1] = x
            self.activePoint[2] = y
            self.imstack.point[self.imstack.current_frame,self.pointKind,0] = x
            self.imstack.point[self.imstack.current_frame,self.pointKind,1] = y
            self.imstack.point_sources[self.imstack.current_frame][self.pointKind] = i
#        print '****ACTIVE POINT after drawCanvas:****\n', self.activePoint
        #Clear out any existing points
        self.canvas.delete('all')
        #If the photo hasn't been set yet then do so
        if self.photo == None:
            self.updatePhoto()
        self.canvas.create_image(0,0,image=self.photo,anchor=NW)
        #Update status bar
        img_name = self.imstack.name_current
        if len(img_name.split(os.path.sep)) > 3:
            img_name = img_name.split(os.path.sep)
            img_name = '...'+os.path.sep+os.path.sep.join(img_name[-3:])
        try:
            self.temporary_statusbar.set(self.format, img_name,
                            self.imstack.point_kind_list[self.pointKind],
                            self.activePoint[1], self.activePoint[2])
        except TypeError:
            self.temporary_statusbar.set(self.format, img_name,
                            self.imstack.point_kind_list[self.pointKind],0,0)
        #Draw predictions of the current point kind in yellow if we're on the
        #frame that the predictions are for and there is no point selected
        if (self.imstack.current_frame == self.predictedFrame
                and
            self.imstack.point_empty(self.imstack.current_frame,self.pointKind)):
            self.drawPredictions()
        #Draw the selected point for every point kind in this frame
        self.drawPoints()

    def updatePhoto(self):
        #Scale the photo to fit the canvas
        photo = self.imstack.img_current
        width,height = photo.size
        scaleX = float(BasicGui.canvas_width)/width
        scaleY = float(BasicGui.canvas_height)/height
        if scaleX < scaleY: self.scale = scaleX
        if scaleX >= scaleY: self.scale = scaleY
        photo = photo.resize((int(width*self.scale),int(height*self.scale)),
                Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(photo)
        #Update the GUI label that displays the frame number
        self.currentFrame.set(str(self.imstack.current_frame+1))
        self.totalFrame.set('/'+str(self.imstack.total_frames))
        self.currentTag.set(str(self.imstack.label_list[self.imstack.current_frame]))

    def drawPredictions(self):
        if not self.showPredictions: return
        rad = BasicGui.circle_radius
        #For each predictor, draw the current pointkind's predicted position
        #in yellow
        cnt = -1
        print self.predicted
        for pred in self.predicted[:]:
            cnt = cnt+1
            x = pred[self.pointKind,0] * self.scale
            y = pred[self.pointKind,1] * self.scale
            color='yellow'
            if cnt == self.activePoint[0]:
                color='blue'
            #If it didn't return a point, don't draw anything
            if not(x == 0 and y == 0):
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill=color)

    def drawPoints(self):
        '''Draw the selected points in this frame. The current pointkind is in red
        and the other pointkinds are in green.'''
        rad = BasicGui.circle_radius
        for k in range(self.imstack.point_kinds):
            x = self.imstack.point[self.imstack.current_frame,k,0] * self.scale
            y = self.imstack.point[self.imstack.current_frame,k,1] * self.scale
            i = self.imstack.point_sources[self.imstack.current_frame][k]
            #If we haven't selected a point yet then don't draw it
            if x == 0 and y == 0: continue
            #Red is selected pointkind, green is other pointkinds
            if k == self.pointKind:
                if i != -1:
                    self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='magenta')
                else:
                    self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='red')
            else:
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='green')

#****** Button functions ******

    def prev(self,event=''):
        '''Move the frame back by one and draw the correct image and points.'''
        self.update_points()
        self.imstack.prev()
        self.updatePhoto()
        self.end_update_loop()

    def next(self,event=''):
        '''Move the frame forward by one and draw the correct image and points.'''
        self.update_points()
        self.imstack.next()
        self.updatePhoto()
        self.end_update_loop()

    def navigate(self,n,event=''):
        '''Move n frames away from current frame, 0 is the first frame in the
        #image stack, -1 is the last frame.'''
        self.update_points()
        if n == 0:
            self.imstack.set_frame(0)
        elif n == -1:
            self.imstack.set_frame(self.imstack.total_frames)
        else:
            self.imstack.advance_frame(n)
        self.updatePhoto()
        self.end_update_loop()

    def gotoFrame(self,event=''):
        '''Use frame count label to go to a specific frame.'''
        self.update_points()
        try:
            frame=int(float(self.currentFrame.get())-1)
        except ValueError:
            self.currentFrame.set(str(self.imstack.current_frame+1))
            return
        if frame < 0:
            self.currentFrame.set(str(self.imstack.current_frame+1))
            return
        if frame > self.imstack.total_frames-1:
            self.currentFrame.set(str(self.imstack.current_frame+1))
            return
        #Move the frame and draw the correct image and points
        self.imstack.set_frame(frame)
        self.updatePhoto()
        self.end_update_loop()

    def searchFrames(self,event=''):
        '''Use text in frame tag to search for next frame with that tag.'''
        tag = str(self.currentTag.get())
        new_frame = self.imstack.find_frame(tag)
        if new_frame != None:
            self.imstack.set_frame(new_frame)
            self.updatePhoto()
            self.end_update_loop()
        else:
            msg = 'No frame tagged as: ' + tag
            tkMessageBox.showinfo(title='Search Error', message=msg)
            self.currentTag.set('')

    def update_points(self):
        '''Update self.imstack.point array and imstack label_list.'''
        i = self.activePoint[0]
        x = self.activePoint[1]
        y = self.activePoint[2]
        L = self.currentTag.get()

        self.selectedPredictions[self.pointKind] = i
        self.imstack.point[self.imstack.current_frame,self.pointKind,0] = x
        self.imstack.point[self.imstack.current_frame,self.pointKind,1] = y
        self.imstack.point_sources[self.imstack.current_frame][self.pointKind] = i
        self.imstack.set_label(L)

    def end_update_loop(self):
        '''Exit TKinter's update loop, control is given back to ChamView.
        After a prediction is made, choose() will be called and the window appears'''
        self.activePoint = [-1,0,0]
        self.master.quit()

    def delete(self,event=''):
        '''Reset the selected point.'''
        self.selectedPredictions[self.pointKind] = -1
        self.imstack.point[self.imstack.current_frame,self.pointKind,0] = 0
        self.imstack.point[self.imstack.current_frame,self.pointKind,1] = 0
        # reset Point Kind source history
        self.selectedPredictions[self.pointKind] = self.activePoint[0] = -1
        self.activePoint[1] = self.activePoint[2] = 0
        self.drawCanvas()

    def clearPointKind(self,event=''):
        '''Clear the selected point kind from all frames.'''
        if tkMessageBox.askyesno(icon='warning',title='Warning',default='no',
                    message='This action will delete the selected point kind from ALL frames.\nWould you like to proceed?',
                    parent=self.master):
            for frame in range(self.imstack.total_frames):
                self.imstack.point[frame][self.pointKind] *= 0
                self.imstack.point_sources[frame][self.pointKind] = -1
            # reset Point Kind source history
            self.selectedPredictions[self.pointKind] = self.activePoint[0] = -1
            self.activePoint[1] = self.activePoint[2] = 0
            self.drawCanvas()

    def clearFrame(self,event=''):
        '''Clear all points on the current frame.'''
        if tkMessageBox.askyesno(icon='warning',title='Warning',default='no',
                    message='This action will delete ALL points on the current frame.\nWould you like to proceed?',
                    parent=self.master):
            self.imstack.point[self.imstack.current_frame] *= 0
            for i in range(len(self.imstack.point_sources[self.imstack.current_frame])):
                self.imstack.point_sources[self.imstack.current_frame][i] = -1
            # reset Point source history
            for i in range(len(self.selectedPredictions)):
                self.selectedPredictions[i] = -1
            self.activePoint[0] = -1
            self.activePoint[1] = self.activePoint[2] = 0
            self.drawCanvas()

    def clearAll(self,event=''):
        '''Clear all points from all frames.'''
        if tkMessageBox.askyesno(icon='warning',title='Warning',default='no',
                    message='This action will delete ALL point data from ALL frames.\nWould you like to proceed?',
                    parent=self.master):
            self.imstack.point *= 0
            for frame in self.imstack.point_sources:
                for i in range(len(frame)):
                    frame[i] = -1
            # reset Point source history
            for i in range(len(self.selectedPredictions)):
                self.selectedPredictions[i] = -1
            self.activePoint[0] = -1
            self.activePoint[1] = self.activePoint[2] = 0
            self.drawCanvas()

    def new(self,event=''):
        print "New"

    def open(self,event=''):
        print "Open"

    def save(self,event=''):
        if self.saveFile == '':
            self.save_as()
        else:
            self.update_points()
            self.imstack.save_points(self.saveFile)
            self.end_update_loop()

    def save_as(self,event=''):
        filename = tkFileDialog.asksaveasfilename(defaultextension='.txt',
                        filetypes=[('Text File',"*.txt")],
                        initialdir=os.path.dirname(self.imstack.name_current),
                        initialfile='points',
                        parent=self.master,
                        title='Save Points Data')
        if filename:
            self.saveFile = filename
            self.save()

    def showHelp(self,event=''):
        '''Shows basic usage information in a popup window.'''
        message = ''
        message += 'Previous/next image\t\tA/D or L/R arrow\n'
#        message += 'Choose point kind\t\t1-9\n'
        message += 'Choose point kind\t\tW/S or U/D arrow\n'
        message += 'Toggle predictions\t\tShift+P\n'
        message += 'Cycle chosen prediction\tQ/E or Right-Click\n'
        message += 'Delete selected point\t\t<Del>\n'
        tkMessageBox.showinfo("Chamview Help",message)

    def quit(self,event=''):
        '''Exit ChamView's main loop and destroy the GUI window'''
        msg = 'Make sure all point data is saved by pressing the save button.\nContinue exiting Chamview?'
        if tkMessageBox.askyesno(icon='warning',title='Exiting Chamview',
                    default='no',message=msg,parent=self.master):
            self.imstack.exit = True
            self.update_points()
            self.end_update_loop()




