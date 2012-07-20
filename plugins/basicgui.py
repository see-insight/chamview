from base import Chooser
from numpy import *
from Tkinter import *
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
        self.photo = None
        self.pointKind = 0
        #Choosing a prediction to use
        self.showPredictions = True
        self.selectedPrediction = []
        #Intitialize GUI, but don't show it yet
        self.madePointkindList = False
        self.createGui()
        self.createKeyBindings()

    def teardown(self):
        #Close the GUI window
        self.quit()

    def choose(self,stack,predicted,predictor_name):
        #Get the imagestack and predicted points
        self.imstack = stack
        self.predicted = predicted
        self.predictedFrame = self.imstack.current_frame
        #Fill the listbox with point kinds available for use if it hasn't been
        if not self.madePointkindList:self.fillPointkindList()
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
            if i+1 <= 9: self.master.bind_all(str(i+1),self.setPointKind)
        self.listbox.selection_set(0)
        #Fill the list of predictor choices
        for i in range(0,self.imstack.point_kinds):
            self.selectedPrediction.append(-1) #-1 corresponds to human input

    def createGui(self):
        #Create the window and grid manager
        self.frameT = Frame(self.master)
        self.frameT.pack(side=LEFT,fill=X)
        self.frameT.grid(columnspan=7,rowspan=1)
        self.frameB = Frame(self.master)
        self.frameB.pack(side=RIGHT,fill=X)
        self.frameB.grid(columnspan=1,rowspan=1)
        self.master.title('Basic GUI Chooser')
        self.master.protocol('WM_DELETE_WINDOW',self.quit)
        #Quit button
        self.button_quit = Button(self.frameT,text='Quit',command=self.quit)
        self.button_quit.grid(column=1,row=1)
        #Current frame label
        self.label_framenum = Label(self.frameT,textvariable=self.currentFrame)
        self.label_framenum.grid(column=2,row=1)
        #Previous button
        self.button_prev = Button(self.frameT,text='Previous',command=self.prev)
        self.button_prev.grid(column=3,row=1)
        #Next button
        self.button_next = Button(self.frameT,text='Next',command=self.next)
        self.button_next.grid(column=4,row=1)
        #Predict button
        self.button_next = Button(self.frameT,text='Predict',command=self.predict)
        self.button_next.grid(column=5,row=1)
        #Listbox used to select point kind
        self.listbar = Scrollbar(self.frameT)
        self.listbar.grid(column=7,row=1)
        self.listbox = Listbox(self.frameT,height=4)
        self.listbox.grid(column=6,row=1)
        self.listbox.config(yscrollcommand=self.listbar.set)
        self.listbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>',self.setPointKind)
        #Canvas to display the current frame
        self.canvas = Canvas(self.frameB,width=BasicGui.canvas_width,
            height=BasicGui.canvas_height)
        self.canvas.grid(column=1,row=1,columnspan=1,rowspan=1)

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
        if self.pointKind > self.imstack.point_kinds -1:
            self.pointKind = self.imstack.point_kinds - 1
        self.updatePointKind()

    def decPointKind(self,event=''):
        self.listbox.selection_clear(self.pointKind)
        self.pointKind = (self.pointKind-1)
        if self.pointKind < 0:
            self.pointKind = 0
        self.updatePointKind()
    
    def updatePointKind(self):
        #Set the listbox's selection and draw the new pointkind on the frame
        self.listbox.selection_set(self.pointKind)
        self.listbox.see(self.pointKind)
        self.drawCanvas()

    def createKeyBindings(self):
        self.master.bind_all('<Up>',self.decPointKind)
        self.master.bind_all('<Down>',self.incPointKind)
        self.master.bind_all('<Left>',self.prev)
        self.master.bind_all('<Right>',self.next)
        self.master.bind_all('<w>',self.decPointKind)
        self.master.bind_all('<x>',self.incPointKind)
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
        self.drawCanvas()

    def drawCanvas(self):
        #Set the selected point if a prediction is selected
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
        #Draw predicted point (if any) and current point
        self.master.title(self.imstack.name_current)
        if (self.imstack.current_frame == self.predictedFrame and self.showPredictions):
            self.drawPrediction()
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
        self.currentFrame.set('Frame '+str(self.imstack.current_frame+1)+'/'+
            str(self.imstack.total_frames))

    def drawPrediction(self):
        rad = BasicGui.circle_radius
        #For each predictor, draw the current pointkind's predicted position
        for pred in self.predicted[:]:
            x = pred[self.pointKind,0] * self.scale
            y = pred[self.pointKind,1] * self.scale
            conf = pred[self.pointKind,2]
            self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='yellow')
        #If there is one, draw the selected prediction in green
        if self.selectedPrediction[self.pointKind] >= 0:
            i = self.selectedPrediction[self.pointKind]
            x = self.predicted[i][self.pointKind,0] * self.scale
            y = self.predicted[i][self.pointKind,1] * self.scale
            self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='green')

    def drawPoints(self):
        #Draw the point already defined for this frame, if any
        for i in range(0,self.imstack.point_kinds):
            x = self.imstack.point[self.imstack.current_frame,i,0] * self.scale
            y = self.imstack.point[self.imstack.current_frame,i,1] * self.scale
            rad = BasicGui.circle_radius
            if i == self.pointKind:
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='red')
            else:
                self.canvas.create_oval((x-rad,y-rad,x+rad,y+rad),fill='green')
        #self.listbox.selection_set(0)

    def quit(self,event=''):
        #Exit ChamView's main loop and destroy the GUI window
        self.imstack.exit = True
        self.master.quit()

    def prev(self,event=''):
        #Move the frame back by one and draw the correct image and points
        self.imstack.prev()
        if self.imstack.current_frame < 0:
            self.imstack.set_frame(0)
        else:
            self.updatePhoto()
            self.drawCanvas()

    def next(self,event=''):
        #Move the frame forward by one and draw the correct image and points
        self.imstack.next()
        if self.imstack.current_frame > self.imstack.total_frames-1:
            self.imstack.set_frame(self.imstack.total_frames-1)
        else:
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
        self.drawCanvas()

