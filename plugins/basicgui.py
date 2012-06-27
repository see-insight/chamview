from base import Chooser
from numpy import *
from Tkinter import *
import ttk
from PIL import ImageTk


class BasicGui(Chooser):

    def setup(self):
        pass

    def teardown(self):
        self.quit()

    def choose(self,stack,predicted,predictor_name):
        self.master = Tk()
        self.imstack = stack
        self.currentFrame = StringVar()
        self.currentFrame.set('Frame '+str(self.imstack.current_frame))
        self.createGui()
        self.createHotkeys()
        self.master.mainloop()

    def createGui(self):
        #Create the window and grid
        self.frame = Frame(self.master)
        self.master.title('Basic GUI Chooser')
        self.frame.grid(columnspan=4,rowspan=2)
        self.master.protocol('WM_DELETE_WINDOW',self.quit)
        #Quit button
        self.button_quit = Button(self.master,text='Quit',command=self.quit)
        self.button_quit.grid(column=1,row=1)
        #Empty gadget to take up room
        self.empty = Label(self.master)
        self.empty.grid(column=1,row=2)
        #Current frame label
        self.label_framenum = Label(self.master,textvariable=self.currentFrame)
        self.label_framenum.grid(column=1,row=3)
        #Previous button
        self.button_prev = Button(self.master,text='Previous',command=self.prev)
        self.button_prev.grid(column=1,row=4)
        #Next button
        self.button_next = Button(self.master,text='Next',command=self.next)
        self.button_next.grid(column=1,row=5)
        #Canvas to display the image
        self.canvas = Canvas(self.master)
        self.canvas.grid(column=2,row=6,columnspan=1,rowspan=1)
        self.drawFrame()

    def createHotkeys(self):
        self.master.bind_all('<a>',self.prev)
        self.master.bind_all('<A>',self.prev)
        self.master.bind_all('<d>',self.next)
        self.master.bind_all('<D>',self.next)

    def drawFrame(self):
        #Keep a reference to this image to Pytohn doesn't garbage-collect it
        self.photo = ImageTk.PhotoImage(self.imstack.img_current)
        self.canvas.config(width=self.photo.width(),height=self.photo.height())
        self.canvas.create_image((0,0),image=self.photo,anchor = NW)

    def quit(self,event=''):
        self.imstack.exit = True
        self.master.quit()

    def prev(self,event=''):
        self.imstack.prev()
        if self.imstack.current_frame < 0:
            self.imstack.set_frame(0)
        self.currentFrame.set('Frame '+str(self.imstack.current_frame))
        self.drawFrame()

    def next(self,event=''):
        self.imstack.next()
        if self.imstack.current_frame > self.imstack.total_frames-1:
            self.imstack.set_frame(self.imstack.total_frames-1)
        self.currentFrame.set('Frame '+str(self.imstack.current_frame))
        self.drawFrame()

