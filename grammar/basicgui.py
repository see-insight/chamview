from Grammar import Chooser
from numpy import *
from Tkinter import *
import tkMessageBox
import ttk
from PIL import Image, ImageTk
import basicgui_supportclasses as support


class BasicGui(Chooser):

    #Size of circles drawn onscreen
    circle_radius = 3
    #How large each frame should be scaled to
    canvas_width = 800
    canvas_height = 600

    def setup(self):
        self.master = Tk()
        #Frame and point info
        self.currentFrame = StringVar()
        self.totalFrame = StringVar()
        self.photo = None
        self.pointKind = 0
        self.added = 0      # number of new point types added during cycle
        self.deleted = []   # indices of point types deleted during cycle
        #Choosing a prediction to use
        self.showPredictions = True
        self.selectedPrediction = []
        #Intitialize GUI, but don't show it yet
        self.madePointkindList = False
        self.madePredictorList = False
        self.createGui()
        self.createKeyBindings()

    def teardown(self):
        #Close the GUI window
        self.quit()

    def choose(self,stack,predicted,predictor_name):
        #Get the imagestack and predicted points
        self.imstack = stack
        self.predicted = predicted
        self.predictor_name = predictor_name
        self.predictedFrame = self.imstack.current_frame
        #Fill the pointlist with point kinds available for use if it hasn't been
        if not self.madePointkindList:self.fillPointkindList()
        if not self.madePredictorList:self.fillPredictorList()

        #Draw new frame and predictions
        self.drawCanvas()
        #Show the window and get user input
        self.master.mainloop()
        return self.added, self.deleted

    def fillPointkindList(self):
        #We don't have to fill the list again after this
        self.madePointkindList = True
        #For every point kind in our imagestack, create an entry in the list
        #and bind the first 9 to the number keys on the keyboard
        for i in range(0,self.imstack.point_kinds):
            self.pointlist.insert(END,self.imstack.point_kind_list[i])
            if i+1 <= 9: self.master.bind_all(str(i+1),self.setPointKind)
        self.pointlist.selection_set(0)
        #Fill the list of predictor choices
        for i in range(0,self.imstack.point_kinds):
            self.selectedPrediction.append(-1) #-1 corresponds to human input
    
    def fillPredictorList(self):
        self.madePredictorList = True
        for n in self.predictor_name:
            self.predlist.insert(END,n)

    def createGui(self):
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
        #Separator line
        self.lineframe = Frame(self.frameL, height=20)
        self.lineframe.grid(row=0,column=0,columnspan=3,rowspan=1)
        #Annotation frame
        self.aframe = Frame(self.frameL)
        self.aframe.grid(row=1,column=0,columnspan=3,rowspan=1,pady=15)
        #Predict button
        self.button_pred = Button(self.aframe,text='Predict',command=self.predict)
        self.button_pred.grid(row=0,column=0,sticky=E)
        #Delete button
        self.button_del = Button(self.aframe,text='Delete',command=self.delete)
        self.button_del.grid(row=0,column=1,sticky=W)
        #Clear Frame button
        self.button_clearf = Button(self.aframe,
                        text='Clear Frame',command=self.clearFrame)
        self.button_clearf.grid(row=1,column=0,sticky=E)
        #Clear All button
        self.button_cleara = Button(self.aframe,
                        text='Clear All',command=self.clearAll)
        self.button_cleara.grid(row=1,column=1,sticky=W)
        #Save and Help frame
        self.shframe = Frame(self.frameL)
        self.shframe.grid(row=2,column=0,columnspan=3,rowspan=1,pady=10)
        #Save button
        self.button_save = Button(self.shframe,text='Save',command=self.save_as)
        self.button_save.grid(row=0,column=0,sticky=E)
        #Help button
        self.button_help = Button(self.shframe,text='Help',command=self.showHelp)
        self.button_help.grid(row=0,column=1,sticky=W)
        #Point Types Label and edit button
        self.pt_label = Label(self.frameL,text='Point Types',height=4,anchor=S)
        self.pt_label.grid(row=3,column=1)
        self.pt_edit = Button(self.frameL,text='Edit',command=self.pointKindEdit)
        self.pt_edit.grid(row=3,column=2,sticky=S)
        #Listbox used to select point kind
        self.pointlist = Listbox(self.frameL,width=15,height=10)
        #self.pointlist.config(cursor=0)
        self.pointlist.grid(row=4,column=1,columnspan=2)
        self.pt_scroll = Scrollbar(self.frameL,orient=VERTICAL)
        self.pt_scroll.grid(row=4,column=0,sticky=NS)
        self.pt_scroll.config(command=self.pointlist.yview,width=15)
        self.pointlist.config(yscrollcommand=self.pt_scroll.set)
        self.pointlist.bind('<<ListboxSelect>>',self.setPointKind)
        self.pointlist.focus()
        #Predictors Label and edit button
        self.pd_label = Label(self.frameL,text='Predictors',height=3,anchor=S)
        self.pd_label.grid(row=5,column=1)
        self.pd_edit = Button(self.frameL,text='Edit',command=self.predictorsOnOff)
        self.pd_edit.grid(row=5,column=2,sticky=S)
        #Listbox used to show predictors
        self.predlist= Listbox(self.frameL,width=15,height=10)
        self.predlist.grid(row=6,column=1,columnspan=2)
        self.pd_scroll = Scrollbar(self.frameL,orient=VERTICAL)
        self.pd_scroll.grid(row=6,column=0,sticky=NS)
        self.pd_scroll.config(command=self.predlist.yview,width=15)
        self.predlist.config(yscrollcommand=self.pd_scroll.set)
        
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
        self.format = 'Point Kind: %s\t\tCursor Position: X: %5.1d\tY: %5.1d\t'
        self.temporary_statusbar.set(self.format, 'TEMP', 0, 0)
        #frame counter Frame
        self.fframe = Frame(self.frameR)
        self.fframe.pack()
        #frame label
        self.label_framenum = Label(self.fframe,text='Frame')
        self.label_framenum.grid(row=0,column=0,pady=10,sticky=E)
        self.label_framenum.config(borderwidth=0)
        #Current frame label
        self.label_goto = Entry(self.fframe,width=3,textvariable=self.currentFrame)
        self.label_goto.grid(row=0,column=1)
        self.label_goto.config(borderwidth=2,relief=SUNKEN)
        self.label_goto.bind("<KeyRelease-Return>", self.gotoFrame)
        #Total Frames
        self.label_framenum = Label(self.fframe,textvariable=self.totalFrame)
        self.label_framenum.grid(row=0,column=2,sticky=W)
        self.label_framenum.config(borderwidth=0)
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

    def gotoFrame(self,event=''):
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
        #Move the frame forward by one and draw the correct image and points
        self.imstack.set_frame(frame)
        self.updatePhoto()
        self.master.quit()

    def setPointKind(self,event=''):
        self.pointlist.selection_clear(self.pointKind)
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
        self.pointlist.selection_clear(self.pointKind)
        self.pointKind = self.pointKind+1
        if self.pointKind > self.imstack.point_kinds-1:
            self.pointKind = self.imstack.point_kinds-1
        self.updatePointKind()

    def decPointKind(self,event=''):
        self.pointlist.selection_clear(self.pointKind)
        self.pointKind = (self.pointKind-1)
        if self.pointKind < 0:
            self.pointKind = 0
        self.updatePointKind()

    def updatePointKind(self):
        '''Set the pointlist's selection and draw the new pointkind on the frame.'''
        self.pointlist.selection_set(self.pointKind)
        self.pointlist.see(self.pointKind)
        self.pointlist.activate(self.pointKind)
        self.master.quit()
    
    def createKeyBindings(self):
        #self.master.bind_all('t',self.decPointKind)
        #self.master.bind_all('b',self.incPointKind)
        self.master.bind_all('<Left>',self.prev)
        self.master.bind_all('<Right>',self.next)
        self.master.bind_all('<a>',self.prev)
        self.master.bind_all('<d>',self.next)
        self.master.bind_all('<s>',self.predict)
        self.master.bind_all('<h>',self.togglePredictions)
        self.master.bind_all('<z>',self.cycleSelectedPrediction)
        self.master.bind_all('<x>',self.cycleSelectedPrediction)
        self.master.bind_all('<Delete>',self.delete)
        self.canvas.bind("<Button-1>",self.onClick)

    def onClick(self,event):
        #Set the current pointkind's position in the current frame to the mouse
        #position and redraw it
        mouseX,mouseY = event.x/self.scale,event.y/self.scale
        self.imstack.point[self.imstack.current_frame,self.pointKind,0] = mouseX
        self.imstack.point[self.imstack.current_frame,self.pointKind,1] = mouseY
        self.selectedPrediction[self.pointKind] = -1 #-1 corresponds to human choice
        self.master.quit()
        self.drawCanvas()

    def drawCanvas(self):
        #If we're using a predictor to set the selected point, then set it
        if (self.selectedPrediction[self.pointKind] != -1 and 
                self.imstack.current_frame == self.predictedFrame):
            i = self.selectedPrediction[self.pointKind]
            x = self.predicted[i][self.pointKind,0]
            y = self.predicted[i][self.pointKind,1]
            self.imstack.point[self.imstack.current_frame,self.pointKind,0] = x
            self.imstack.point[self.imstack.current_frame,self.pointKind,1] = y
        #Clear out any existing points
        self.canvas.delete('all')
        #If the photo hasn't been set yet then do so
        if self.photo == None:
            self.updatePhoto()
        self.canvas.create_image((0,0),image=self.photo,anchor = NW)
        #Set the title of the window to the current image filename
        self.master.title(self.imstack.name_current)
        #Draw predictions of the current point kind in yellow if we're on the
        #frame that the predictions are for
        if(self.imstack.current_frame == self.predictedFrame):
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

    def drawPredictions(self):
        rad = BasicGui.circle_radius
        #For each predictor, draw the current pointkind's predicted position
        #in yellow
        cnt = -1
        self.predlist.selection_clear(0,END) 
        for pred in self.predicted[:]:
            cnt = cnt+1
            x = pred[self.pointKind,0] * self.scale
            y = pred[self.pointKind,1] * self.scale
            conf = pred[self.pointKind,2]
            color='yellow'
            if self.selectedPrediction[self.pointKind] == -1:
                    color='yellow'
            else:
                if cnt == self.selectedPrediction[self.pointKind]: 
                    color='blue'
            #If it didn't return a point, don't draw anything
            if x == 0 and y == 0 and conf == 0: 
                self.predlist.selection_clear(cnt)
                color='yellow'
            else:
                self.predlist.selection_set(cnt)
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill=color)

    def drawPoints(self):
        #Draw the selected points in this frame. The current pointkind is in red
        #and the other pointkinds are in green
        rad = BasicGui.circle_radius
        for i in range(0,self.imstack.point_kinds):
            x = self.imstack.point[self.imstack.current_frame,i,0] * self.scale
            y = self.imstack.point[self.imstack.current_frame,i,1] * self.scale
            #If we haven't selected a point yet then don't draw it
            if x == 0 and y == 0: continue
            #Red is selected pointkind, green is other pointkinds
            if i == self.pointKind:
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='red')
            else:
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='green')

    def quit(self,event=''):
        #Exit ChamView's main loop and destroy the GUI window
        self.imstack.exit = True
        self.master.quit()

    def prev(self,event=''):
        #Move the frame back by one and draw the correct image and points
        self.imstack.prev()
        #if self.imstack.current_frame < 0:
        #    self.imstack.set_frame(0)
        #else:
        self.updatePhoto()
        self.drawCanvas()

    def next(self,event=''):
        #Move the frame forward by one and draw the correct image and points
        self.imstack.next()
        #self.imif self.imstack.current_frame > self.imstack.total_frames-1:
        #    self.imstack.set_frame(self.imstack.total_frames-1)
        #else:
        self.updatePhoto()
        self.drawCanvas()
        
    def navigate(self,n,event=''):
        #Move n frames away from current frame, 0 is the first frame in the
        #image stack, -1 is the last frame
        if n == 0:
            self.imstack.set_frame(0)
        elif n == -1:
            self.imstack.set_frame(self.imstack.total_frames)
        else:
            self.imstack.advance_frame(n)
        self.updatePhoto()
        self.drawCanvas()              

    def predict(self,event=''):
        #Exit TKinter's update loop to control is given back to ChamView. After
        #a prediction is made, choose() will be called and the window appears
        self.master.quit()
        
    def delete(self,event=''):
        #Reset the clicked point if it's selected as active
        if self.selectedPrediction[self.pointKind] == -1:
            self.imstack.point[self.imstack.current_frame,self.pointKind,0] = 0
            self.imstack.point[self.imstack.current_frame,self.pointKind,1] = 0
        self.drawCanvas()
        
    def clearFrame(self,event=''):
        print "Clear Frame"
        
    def clearAll(self,event=''):
        print "Clear All"
        
    def new(self,event=''):
        print "New"
        
    def open(self,event=''):
        print "Open"
        
    def save_as(self,event=''):
        print "Save As"
        
    def pointKindEdit(self,event=''):
        dialog_window = support.EditPointKinds(self.master,self.imstack.point_kind_list,
                                        'Edit Point Kinds')
        new_points, self.added, self.deleted = dialog_window.result
        
        self.imstack.deletePointKinds(self.deleted)
        self.imstack.addPointKinds(self.added)
        self.imstack.get_point_kinds(List=new_points)
        self.pointlist.delete(0,END)
        self.fillPointkindList()
        
    def predictorsOnOff(self,event=''):
        print "Window to turn Predictors on/off"
        
    def togglePredictions(self,event=''):
        #Turn the drawing of predicted points on or off
        self.showPredictions = not self.showPredictions
        if not self.showPredictions:
            for x in self.selectedPrediction:
                x = -1 #-1 corresponds to human input
        self.master.quit()
        self.drawCanvas()
        
    def cycleSelectedPrediction(self,event=''):
        #Cycle through the predicted points to choose one as the next prediction
        if not self.madePointkindList: return
        if(event.char=='z'):
            self.selectedPrediction[self.pointKind] -= 1
            if self.selectedPrediction[self.pointKind] < -1:
                self.selectedPrediction[self.pointKind] = len(self.predicted)-1
        elif(event.char=='x'):
            self.selectedPrediction[self.pointKind] += 1
            if self.selectedPrediction[self.pointKind] > len(self.predicted)-1:
                self.selectedPrediction[self.pointKind] = -1
        #Reset the clicked point if it's selected as active (MAY REPLACE W/ DELETE FUNC)
        if self.selectedPrediction[self.pointKind] == -1:
            self.imstack.point[self.imstack.current_frame,self.pointKind,0] = 0
            self.imstack.point[self.imstack.current_frame,self.pointKind,1] = 0
        self.drawCanvas()


    def showHelp(self,event=''):
        #Shows basic usage information in a popup window
        message = ''
        message += 'Previous/next image\t\ta/d\n'
        message += 'Previous/next image\t\tL/R arrow\n'
        message += 'Choose point kind\t\t1-9\n'
        message += 'Choose point kind\t\tU/D arrow\n'
        message += 'Calculate predictions\t\ts\n'
        message += 'Toggle predictions\t\th\n'
        message += 'Cycle chosen prediction\tz/x\n'
        message += 'Delete selected point\t\t<Del>\n'
        tkMessageBox.showinfo("Chamview Help",message)



