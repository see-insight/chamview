from Grammar import Chooser
from numpy import *
from Tkinter import *
import tkMessageBox
import ttk
from PIL import Image, ImageTk


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
        #Fill the listbox with point kinds available for use if it hasn't been
        if not self.madePointkindList:self.fillPointkindList()
        if not self.madePredictorList:self.fillPredictorList()

        #Draw new frame and predictions
        self.drawCanvas()
        #Show the window and get user input
        self.master.mainloop()

    def fillPointkindList(self):
        #We don't have to fill the list again after this
        self.madePointkindList = True
        #For every point kind in our imagestack, create an entry in the list
        #and bind the first 9 to the number keys on the keyboard
        for i in range(0,self.imstack.point_kinds):
            self.listbox.insert(END,self.imstack.point_kind[i])
            #if i+1 <= 9: self.master.bind_all(str(i+1),self.setPointKind)
        self.listbox.selection_set(0)
        #Fill the list of predictor choices
        for i in range(0,self.imstack.point_kinds):
            self.selectedPrediction.append(-1) #-1 corresponds to human input
    
    def fillPredictorList(self):
        self.madePredictorList = True
        for n in self.predictor_name:
            self.prelist.insert(END,n)

    def createGui(self):
        #Set up application window
        self.master.title('Basic GUI Chooser')
        self.master.protocol('WM_DELETE_WINDOW',self.quit)
        #Grid manager: buttons on left size, image on right
        self.frameL = Frame(self.master)
        self.frameL.grid(row=0,column=0,columnspan=3,rowspan=5)
        self.frameR = Frame(self.master)
        self.frameR.grid(row=0,column=3,columnspan=1,rowspan=1)
        self.frameR.config(borderwidth=3,relief=GROOVE)
        #Quit button
        self.button_quit = Button(self.frameL,text='Quit',command=self.quit)
        self.button_quit.grid(column=0,row=0,columnspan=3)
        #Help button
        self.button_help = Button(self.frameL,text='Help',command=self.showHelp)
        self.button_help.grid(column=2,row=0,columnspan=2)
        #Predict button
        self.button_next = Button(self.frameL,text='Predict',command=self.predict)
        self.button_next.grid(column=0,row=1,columnspan=2)
        #frame label
        self.label_framenum = Label(self.frameL,text='Frame')
        self.label_framenum.grid(column=2,row=1)
        self.label_framenum.config(borderwidth=0)
        #Current frame label
        self.label_goto = Entry(self.frameL,width=3,textvariable=self.currentFrame)
        self.label_goto.grid(column=3,row=1)
        self.label_goto.config(borderwidth=2,relief=SUNKEN)
        self.label_goto.bind("<KeyRelease-Return>", self.gotoFrame)
        #Total Frames
        self.label_framenum = Label(self.frameL,textvariable=self.totalFrame)
        self.label_framenum.grid(column=4,row=1)
        self.label_framenum.config(borderwidth=0)
        #Previous button
        self.button_prev = Button(self.frameL,text='Previous',command=self.prev)
        self.button_prev.grid(column=0,row=2,columnspan=2)
        #Next button
        self.button_next = Button(self.frameL,text='Next',command=self.next)
        self.button_next.grid(column=2,row=2)
        #Listbox used to select point kind
        self.listbox = Listbox(self.frameL,width=15,height=10)
        #self.listbox.config(cursor=0)
        self.listbox.grid(column=1,row=4,columnspan=2)
        self.listbar = Scrollbar(self.frameL,orient=VERTICAL)
        self.listbar.grid(column=0,row=4,sticky='ns')
        self.listbar.config(command=self.listbox.yview,width=15)
        self.listbox.config(yscrollcommand=self.listbar.set)
        self.listbox.bind('<<ListboxSelect>>',self.setPointKind)
        self.listbox.focus()
        
    
        #Listbox used to show predictors
        self.prelist= Listbox(self.frameL,width=15,height=10)
        self.prelist.grid(column=1,row=5,columnspan=2)

        #Canvas to display the current frame
        self.canvas = Canvas(self.frameR,width=BasicGui.canvas_width,
            height=BasicGui.canvas_height)
        self.canvas.grid(column=0,row=0,columnspan=1,rowspan=1)

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
        self.listbox.selection_clear(self.pointKind)
        if event.char == '??':
            #User clicked on the listbox
            try:
                self.pointKind = int(self.listbox.curselection()[0])
            except IndexError:
                pass
        else:
            #User hit a key 1-9 on the keyboard
            self.pointKind = int(event.char) - 1
        self.updatePointKind()

    def incPointKind(self,event=''):
        self.listbox.selection_clear(self.pointKind)
        self.pointKind = self.pointKind+1
        if self.pointKind > self.imstack.point_kinds-1:
            self.pointKind = self.imstack.point_kinds-1
        self.updatePointKind()

    def decPointKind(self,event=''):
        self.listbox.selection_clear(self.pointKind)
        self.pointKind = (self.pointKind-1)
        if self.pointKind < 0:
            self.pointKind = 0
        self.updatePointKind()

    def updatePointKind(self):
        #Set the listbox's selection and draw the new pointkind on the frame
        self.listbox.selection_clear(self.pointKind)
        self.listbox.selection_set(self.pointKind)
        self.listbox.see(self.pointKind)
        self.listbox.activate(self.pointKind)
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
        self.canvas.bind("<Button-1>",self.onClick)

    def onClick(self,event):
        #Set the current pointkind's position in the current frame to the mouse
        #position and redraw it
        mouseX,mouseY = event.x/self.scale,event.y/self.scale
        self.imstack.point[self.imstack.current_frame,self.pointKind,0] = mouseX
        self.imstack.point[self.imstack.current_frame,self.pointKind,1] = mouseY
        self.selectedPrediction[self.pointKind] = -1 #-1 corresponds to human choice
        self.master.quit()
        #self.drawCanvas()

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
        self.prelist.selection_clear(0,END) 
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
                self.prelist.selection_clear(cnt)
                color='yellow'
            else:
                self.prelist.selection_set(cnt)
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

    def predict(self,event=''):
        #Exit TKinter's update loop to control is given back to ChamView. After
        #a prediction is made, choose() will be called and the window appears
        self.master.quit()

    def togglePredictions(self,event=''):
        #Turn the drawing of predicted points on or off
        self.showPredictions = not self.showPredictions
        if not self.showPredictions:
            for x in self.selectedPrediction:
                x = -1 #-1 corresponds to human input
        self.master.quit()
        #self.drawCanvas()

    def showHelp(self,event=''):
        #Shows basic usage information in a popup window
        message = ''
        message += 'Previous/next image\ta/d\n'
        message += 'Previous/next image\tL/R arrow\n'
        message += 'Choose point kind\t\t1-9\n'
        message += 'Choose point kind\t\tU/D arrow\n'
        message += 'Calculate predictions\ts\n'
        message += 'Toggle predictions\t\th\n'
        message += 'Cycle chosen prediction\tz/x\n'
        tkMessageBox.showinfo("Chamview Help",message)

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
        #Reset the clicked point if it's selected as active
        if self.selectedPrediction[self.pointKind] == -1:
            self.imstack.point[self.imstack.current_frame,self.pointKind,0] = 0
            self.imstack.point[self.imstack.current_frame,self.pointKind,1] = 0
        self.drawCanvas()

