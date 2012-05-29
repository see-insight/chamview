import os, string, dircache, time, shutil
from Tkinter import *
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
import ttk
import Image, ImageTk
import sys
import pyglet   #Solely for extracting video frames
from PIL import Image

##Notes:
##button fxns will run as soon as button is made if callback includes ()
##span starts in top left
##anchor neccessary or image will not fit correctly
##event is neccessary argument for event-bound items


#second 'main' window
class PickClick:

    def __init__(self, master, directory,fList,fps):

        self.directory = directory
        self.dirList = self.directory.split(os.path.sep)

        self.fList = fList
        self.fDic = {}
        n = 1
        #puts files in order so they can be iterated through one at a time    
        for image in self.fList: 
            if '.png' in image or '.PNG' in image  \
            or '.jpg'in image or '.JPG' in image   \
            or '.bmp' in image or '.BMP' in image  \
            or '.gif' in image or '.GIF' in image:
                self.fDic[str(n)] = image
                n = n + 1
                

        #gets fps from first window
        self.fps = fps
        
        self.length = len(self.fDic)
        #open file for reading/writing coords, name based on given image directory
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','a')

        self.num = StringVar()
        self.num.set(1)
        self.dotType = StringVar()
        self.comment = StringVar()
        self.comment.set("comment")
        
        self.frame = Frame(master)
        master.title('ChamView')
        self.frame.grid(columnspan=8,rowspan=5)
        #binds shortcut keys
        master.bind_all('<a>', self.Prev)
        master.bind_all('<A>', self.Prev)
        master.bind_all('<d>', self.Nxt)
        master.bind_all('<d>', self.Nxt)
        master.bind_all('<p>', self.Play)
        master.bind_all('<o>', self.Pause)
        master.bind_all('<i>',self.Rewind)
        master.bind_all('<s>',self.SaveAll)

        master.bind_all('1', self.ChangeLF)
        master.bind_all('2', self.ChangeRF)
        master.bind_all('3', self.ChangeLB)
        master.bind_all('4', self.ChangeRB)
        master.bind_all('5', self.ChangeGS)
        master.bind_all('6', self.ChangeGE)
        master.bind_all('7', self.ChangeSV)
        master.bind_all('8', self.ChangeCm)

        #quit button
        self.quitB = Button(master,text='QUIT',command = master.quit)
        self.quitB.grid(column=8,row=1)
        #previous button
        self.prevB = Button(master, text = 'PREV [A]',command = self.Prev) 
        self.prevB.grid(column=4,row=5)
        
        self.prev10B = Button(master, text = 'PREV10',command = self.Prev10)
        self.prev10B.grid(column=3,row=5)
        
        self.prev100B = Button(master, text = 'PREV100',command = self.Prev100)
        self.prev100B.grid(column=2,row=5)
        #first button
        self.firstB = Button(master, text = 'FIRST',command = self.First)
        self.firstB.grid(column=1,row=5)
        #next button
        self.nextB = Button(master,text='NEXT [D]',command = self.Nxt)
        self.nextB.grid(column=5,row=5)
        
        self.next10B = Button(master, text = 'NEXT10',command = self.Nxt10)
        self.next10B.grid(column=6,row=5)
        
        self.next100B = Button(master, text = 'NEXT100',command = self.Nxt100)
        self.next100B.grid(column=7,row=5)
        #last button
        self.lastB = Button(master,text='LAST',command = self.Last)
        self.lastB.grid(row=5,column=8)
        #frame label
        self.numLab = Label(master,textvariable = self.num)
        self.numLab.grid(column=1,row=1,sticky=W)
        #clear all of points
        self.clearB = Button(master,text='CLEAR ALL',command = self.Clear)
        self.clearB.grid(column=7,row=1,sticky=E) 
        #clear frame of points
        self.clearFrameB = Button(master,text='CLEAR FRAME',command=self.ClearPic)
        self.clearFrameB.grid(column=6,row=1,sticky=E) 
        #shows what kind of label/point is currently selected
        self.dotLab = Label(master,textvariable=self.dotType)
        self.dotLab.grid(column=2,row=1)
        #comment box
        self.commentInput = Entry(master, bd=5, textvariable=self.comment, width=40)
        self.commentInput.grid(column=3,row=1, columnspan=2)
        #bind return key for comment box
        self.commentInput.bind("<KeyPress-Return>",self.Comment)
        #shows directory
        self.dirLab = Label(master,text=self.directory)
        self.dirLab.grid(row=4,column=1,sticky=W)
        #shows file with point coords
        self.fileLab = Label(master,text = self.dirList[-1]+'.txt')
        self.fileLab.grid(row=4,column=8,sticky=E)
        #rewind button
        self.rewB = Button(master,text = 'REW. [I]',command = self.Rewind)
        self.rewB.grid(row=4,column=3)
        #pause button
        self.pauseB = Button(master,text='PAUSE [O]',command=self.Pause)
        self.pauseB.grid(row=4,column=4,columnspan=2)
        #play button
        self.playB = Button(master,text='PLAY [P]',command=self.Play)
        self.playB.grid(row=4,column=6)
        
        self.canv = Canvas(master)
        self.canv.grid(column=1,row=2,columnspan = 8, rowspan = 2)
        imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
        #makes file into tkinter object so it can be drawn on canvas
        self.photo = ImageTk.PhotoImage(Image.open(imageFile))
        #returns id as self.obj
        self.obj = self.canv.create_image(0,0,
                                          image = self.photo,
                                          tags = (self.num.get()+'n'),anchor=NW)
        #checks if image has any points
        boo = self.Check(self.num.get()+'n')
        if boo:
            #draws points if so
            self.ReDraw(self.num.get()+'n')
            #binds click to create circle
        self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
        #size canvas to image
        self.canv.config(width = self.photo.width(),height = self.photo.height())
        fo.close()

        #allow window to resize properly
        #master.columnconfigure(0,weight=1)
        #master.rowconfigure(0,weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=1)
        master.columnconfigure(3, weight=1)
        master.columnconfigure(4, weight=1)
        master.columnconfigure(5, weight=1)
        master.columnconfigure(6, weight=1)
        master.columnconfigure(7, weight=1)
        master.columnconfigure(8, weight=1)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=3)
        master.rowconfigure(3, weight=3)
        master.rowconfigure(4, weight=1)
        master.rowconfigure(5, weight=1)

    def ChangeLF(self,event):
        '''Changes the type of point'''
        self.dotType.set('LF')
    def ChangeRF(self,event):
        '''Changes the type of point'''
        self.dotType.set('RF')
    def ChangeLB(self,event):
        '''Changes the type of point'''
        self.dotType.set('LB')
    def ChangeRB(self,event):
        '''Changes the type of point'''
        self.dotType.set('RB') 
    def ChangeGS(self,event):
        '''Changes the type of point'''
        self.dotType.set('GS')
    def ChangeGE(self,event):
        '''Changes the type of point'''
        self.dotType.set('GE')
    def ChangeSV(self,event):
        '''Changes the type of point'''
        self.dotType.set('S/V')
    def ChangeCm(self,event):
        '''Changes the type of point'''
        self.dotType.set('Cm')
        
    def Comment(self,event):
        '''Adds a comment to the frame in question'''
        comment = self.comment.get()
        comment = comment.strip()
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','a')
        stri = "COM:"+self.num.get()+":"+comment 
        fo.write(stri+"\n")
        fo.close()

    #event arg neccessary because this has been bound to keyboard
    def Nxt(self,event=''):
        '''Advances picture in directory'''
        try:
            self.num.set(int(self.num.get())+1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            #convert image file to Tkinter image object via PIL
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            #size canvas to image
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            #binds click to this picture
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            #checks if image has any points
            boo = self.Check(self.num.get()+'n')
            if boo:
                #draws points if so
                self.ReDraw(self.num.get()+'n')
        except:
            #sets frame to last if nxt encounters error
            self.num.set(self.length)

    def Nxt10(self):
        '''Advances 10 frames'''
        try:
            #only thing different from Nxt is +10 instead of +1
            self.num.set(int(self.num.get())+10)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')
        except:
            self.num.set(self.length)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')

    def Nxt100(self):
        '''Advances 100 frames'''
        try:
            #only difference from Nxt is +100
            self.num.set(int(self.num.get())+100)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')
        except:
            self.num.set(self.length)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')

    def Last(self):
        '''Advances to last frame'''
        self.num.set(self.length)
        imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
        #convert image file to Tkinter image object via PIL
        self.photo = ImageTk.PhotoImage(Image.open(imageFile))
        #size canvas to image
        self.canv.config(width = self.photo.width(),height = self.photo.height())
        self.obj = self.canv.create_image((0,0),
                                          image = self.photo,
                                          tags = (self.num.get()+'n'),anchor = NW)
        #binds click to this picture
        self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
        #checks if image has any points
        boo = self.Check(self.num.get()+'n')
        if boo:
            #draws points if so
            self.ReDraw(self.num.get()+'n')
            
    def Prev(self,event=''):
        '''Previous picture in directory'''
        try:
            self.num.set(int(self.num.get())-1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            #convert image file to Tkinter image object via PIL
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            #size canvas to image
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            #binds click to this picture
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            #checks if image has any points
            boo = self.Check(self.num.get()+'n')
            if boo:
                #draws points if so
                self.ReDraw(self.num.get()+'n')
        except:
            #sets frame to one if prev encounters error
            self.num.set(1)

    def Prev10(self):
        '''Go 10 frames back'''
        try:
            #only difference from prev is -10 instead of -1
            self.num.set(int(self.num.get())-10)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor=NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')
        except:
            self.num.set(1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor=NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')

    def Prev100(self):
        '''Go 100 frames back'''
        try:
            #-100 instead of -1
            self.num.set(int(self.num.get())-100)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor=NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')
        except:
            self.num.set(1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor=NW)
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            boo = self.Check(self.num.get()+'n')
            if boo:
                self.ReDraw(self.num.get()+'n')

    def First(self):
        '''Go to last frame'''
        self.num.set(1)
        imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
        #convert image file to Tkinter image object via PIL
        self.photo = ImageTk.PhotoImage(Image.open(imageFile))
        #size canvas to image
        self.canv.config(width = self.photo.width(),height = self.photo.height())
        self.obj = self.canv.create_image((0,0),
                                          image = self.photo,
                                          tags = (self.num.get()+'n'),anchor = NW)
        #binds click to this picture
        self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
        #checks if image has any points
        boo = self.Check(self.num.get()+'n')
        if boo:
            #draws points if so
            self.ReDraw(self.num.get()+'n')

    def Play(self,event=''):
        '''Animates video sequence'''
        #stop other play/pause 
        self.go = False
        #allow Play while loop to run
        self.go = True
        #will run while not at max frame number, self.go controlled by Pause
        self.playing = True
        self.rewing = False
        while int(self.num.get()) < self.length and self.go == True and self.playing==True and self.rewing==False:
            #delay between frames, set according to fps
            time.sleep(1.0/self.fps)
            self.num.set(int(self.num.get())+1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            #size canvas to image
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            #binds click to this picture
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            #needed after sleep to stop window from crashing
            self.canv.update()
            #checks if image has any points
            boo = self.Check(self.num.get()+'n')
            if boo:
                #draws points if so
                self.ReDraw(self.num.get()+'n')
            #needed to make points appear
            self.canv.update()
            if int(self.num.get()) == self.length:
                self.go = False
                self.playing = False

    def Pause(self,event=''):
        '''Pauses video sequence'''
        #stops play/rewind while loops from running
        self.go = False
        self.playing = False
        self.rewing = False
        
    def Rewind(self,event=''):
        '''Animates video sequence in reverse'''
        #stop other play/pause 
        self.go = False
        #allow Rewind while loop to run
        self.go = True
        self.rewing = True
        self.playing = False
        while int(self.num.get()) > 1 and self.go == True and self.playing == False and self.rewing == True: 
            #delay between frames, set according to fps
            time.sleep(1.0/self.fps)
            self.num.set(int(self.num.get())-1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
            #size canvas to image
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),
                                              image = self.photo,
                                              tags = (self.num.get()+'n'),anchor = NW)
            #binds click to this picture
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
            #needed after sleep to stop window from crashing
            self.canv.update()
            #checks if image has any points
            boo = self.Check(self.num.get()+'n')
            if boo:
                #draws points if so
                self.ReDraw(self.num.get()+'n')
            #needed to make points appear
            self.canv.update()
            if int(self.num.get()) == 1:
                self.go = False
                self.rewing = False
     
    

    def Click(self,event):
        '''Draw circle on click and record tag/circle coords in file'''
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','a')
        
        label = self.dotType.get()
        if label == 'LF':
            #coords are two opposite corners of circle
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'yellow')
            #tags item so it can be used(deleted) later
            self.canv.itemconfigure(circId,tags=(str(circId)+'LF'))
            #binds item to unclick
            self.canv.tag_bind(str(circId)+'LF','<Button-1>',self.UnClick)
            #writes coordinates of circle, tag/id of circle to file
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'LF')
        if label == 'RF':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'orange')
            self.canv.itemconfigure(circId,tags=(str(circId)+'RF'))
            self.canv.tag_bind(str(circId)+'RF','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'RF')
        if label == 'LB':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'blue')
            self.canv.itemconfigure(circId,tags=(str(circId)+'LB'))
            self.canv.tag_bind(str(circId)+'LB','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'LB')
        if label == 'RB':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'turquoise')
            self.canv.itemconfigure(circId,tags=(str(circId)+'RB'))
            self.canv.tag_bind(str(circId)+'RB','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'RB')
        if label == 'GS':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'plum')
            self.canv.itemconfigure(circId,tags=(str(circId)+'GS'))
            self.canv.tag_bind(str(circId)+'GS','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'GS')
        if label =='GE':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'purple')
            self.canv.itemconfigure(circId,tags=(str(circId)+'GE'))
            self.canv.tag_bind(str(circId)+'GE','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'GE')
        if label == 'S/V':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'red')
            self.canv.itemconfigure(circId,tags=(str(circId)+'S/V'))
            self.canv.tag_bind(str(circId)+'S/V','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'S/V')
        if label == 'Cm':
            circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                          fill = 'lime green')
            self.canv.itemconfigure(circId,tags=(str(circId)+'Cm'))
            self.canv.tag_bind(str(circId)+'Cm','<Button-1>',self.UnClick)
            stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                    +':'+str(event.y+3)+':'+str(circId)+'Cm')
        
        fo.write(stri+'\n')
        fo.close()


    def UnClick(self,event):
        '''Deletes point circles when they are clicked'''
        x,y = self.canv.canvasx(event.x),self.canv.canvasy(event.y)
        closeItem = self.canv.find_closest(x,y)[0]
        #gets tag of the closest item
        tags = self.canv.gettags(closeItem)
        #original file
        fin = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','r')
        #temporary file
        fout = open('temp.txt','w')
        
        for line in fin:
            lineLst = line.split(':')
            #prevents this from deleting the frame
            #last part of each line is circle tag(id)
            if lineLst[-1][0:-1] == tags[0]: 
                self.canv.delete(tags[0])
            else:
                #if item not deleted, line is written to temp file
                fout.write(line)

        fin.close()
        fout.close()
        #orig,wiped clean
        fin2 = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','w')
        #temp
        fout2 = open('temp.txt','r')

        for line2 in fout2:
            #copies temp file to orig file
            fin2.write(line2)
        
        fin2.close()
        fout2.close()
            
    def ClearPic(self):
        '''Clears current frame of points'''
        #original file
        fin = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','r')
        #temporary file
        fout = open('temp.txt','w')
        
        for line in fin:
            lineLst = line.split(':')
            if lineLst[0] == (self.num.get()+'n'):
                self.canv.tag_raise((self.num.get()+'n'))
            else:
                #if item not deleted, line is written to temp file
                fout.write(line)

        fin.close()
        fout.close()
        #orig,wiped clean
        fin2 = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','w')
        #temp
        fout2 = open('temp.txt','r')

        for line2 in fout2:
            #copies temp file to orig file
            fin2.write(line2)
        
        fin2.close()
        fout2.close()
        
        

    def ReDraw(self,tag):
        '''Redraws circles on frame'''
        boo = False
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','r')
        #redraws circles based on coordinates in file
        for line in fo:
            lineLst = line.split(':')
            if lineLst[0] == tag:
                if 'LF' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'yellow')
                    #tags item with id of original circle so it can be used(deleted) later
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    #binds item to unclick
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'RF' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'orange')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'LB' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'blue')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'RB' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'turquoise')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'GS' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'plum')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'GE' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'purple')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'S/V' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'red')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
                if 'Cm' in lineLst[-1]:
                    circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                                   fill = 'lime green')
                    self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                    self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)
        fo.close()

    def Check(self,tag):
        '''Checks if current picture has any points clicked'''
        boo = False
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','r')
        for line in fo:
            lineLst = line.split(':')
            if lineLst[0] == tag:
                boo = True      
        return boo
        fo.close()

    def Clear(self):
        '''Clears file of all points'''
        #clears current frame so user isn't confused
        self.canv.tag_raise((self.num.get()+'n'))
        #wipes file of all coords
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','w')
        fo.close()

    def SaveImg(self):
        '''Saves current frame as a png'''
        dirName = self.directory+os.path.sep+'annotated'
        try:
            #make a new directory to put dotted frames in
            os.mkdir(dirName)
        except WindowsError:
            pass
        fileName = dirName+os.path.sep+self.fDic[self.num.get()]
        self.canv.update()
        x0 = self.canv.winfo_rootx()
        y0 = self.canv.winfo_rooty()
        x1 = x0 + self.canv.winfo_width()
        y1 = y0 + self.canv.winfo_height()
        offset1 = 0
        offset2 = 0
        #grabs area of the screen and makes it into PIL image object
        im = ImageGrab.grab((x0-offset1, y0-offset1, x1+offset2,y1+offset2))
        im.save(fileName)

    def SaveAll(self,event=''):
        pass
        #This is currently not working, messes with text file somehow.  Figure out later.
        '''Saves all frames as pngs'''
##        #stop other play/pause 
##        self.go = False
##        dirName = self.directory+os.path.sep+'annotated'
##        try:
##            #make a new directory to put dotted frames in
##            os.mkdir(dirName)
##        except WindowsError:
##            pass
##        #allow saveAll while loop to run
##        self.go = True
##        #will run while not at max frame number, self.go controlled by Pause
##        while int(self.num.get()) < self.length and self.go == True:
##            self.num.set(int(self.num.get())+1)
##            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
##            self.photo = ImageTk.PhotoImage(Image.open(imageFile))
##            #size canvas to image
##            self.canv.config(width = self.photo.width(),height = self.photo.height())
##            self.obj = self.canv.create_image((0,0),
##                                              image = self.photo,
##                                              tags = (self.num.get()+'n'),anchor = NW)
##            #binds click to this picture
##            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)
##            #needed after sleep to stop window from crashing
##            self.canv.update()
##            #checks if image has any points
##            boo = self.Check(self.num.get()+'n')
##            if boo:
##                #draws points if so
##                self.ReDraw(self.num.get()+'n')
##            #needed to make points appear
##            self.canv.update()
##            fileName = dirName+os.path.sep+self.fDic[self.num.get()]
##            self.canv.update()
##            x0 = self.canv.winfo_rootx()
##            y0 = self.canv.winfo_rooty()
##            x1 = x0 + self.canv.winfo_width()
##            y1 = y0 + self.canv.winfo_height()
##            offset1 = 0
##            offset2 = 0
##            im = ImageGrab.grab((x0-offset1, y0-offset1, x1+offset2,y1+offset2))
##            im.save(fileName)
##            if int(self.num.get()) == self.length:
##                self.go = False
##            
        
        


#--- The first window, user prompted for directory ----------------------------#
class Window1:


    '''Called upon creation'''
    def __init__(self,master):
        self.picList = None
        
        #Variable to hold the chosen video, directory, and video FPS
        self.video = StringVar()
        self.video.set('')
        self.directory = StringVar()
        self.directory.set(os.getcwd())
        self.fps = IntVar()
        self.fps.set(30)
        
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
    

    '''Opens a window to allow the user to select a video'''
    def chooseVideo(self):
        myFile = tkFileDialog.askopenfilename(parent = root,initialdir=os.getcwd(),title='Open video')
        if len(myFile) > 0: self.video.set(myFile)
    
    
    '''Opens a window to allow the user to select a directory'''
    def chooseDir(self):
        myDir = tkFileDialog.askdirectory(parent = root,
            initialdir=self.directory.get(),title='Navigate to image files')
        if len(myDir) > 0: self.directory.set(myDir)
    
    
    '''Determines whether or not the current directory is valid'''
    #Returns "bad dir" if the directory doesn't exist
    #Returns "no img" if no valid images were found in the directory
    #Otherwise, returns "good"
    def checkDir(self):
        directory = self.directory.get().strip()
        goodDirectory = False
        #Does the directory exist?
        if not os.path.isdir(directory): return "bad dir"
        #Check if there's a valid picture file
        self.picList = dircache.listdir(directory)
        for pic in self.picList:
            if '.png' in pic or '.PNG' in pic  \
            or '.jpg'in pic or '.JPG' in pic   \
            or '.bmp' in pic or '.BMP' in pic  \
            or '.gif' in pic or '.GIF' in pic:
                goodDirectory = True
        if goodDirectory == True: return "good"
        return "no img"
       
    
    '''Determines whether the inputted FPS is valid, returns True or False'''
    def checkFPS(self):
        if self.fps.get() > 0:
            return True
        else:
            return False
    
    
    '''Extracts frames from a video file and saves them'''
    def extract(self):
        source = self.video.get()
        start = 0
        end = 0
        time = 0
        vframe = None
        #Load in the video source file
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
            #Some other error
            tkMessageBox.showerror('ChamView','Error: Pyglet failure')
            return
        
        #Is the file a video?
        if sourceVid.video_format == None:
            tkMessageBox.showerror('ChamView', 'Error: invalid video file')
            return
        
        #Get the start and end time to extract
        start = tkSimpleDialog.askfloat('ChamView','Extraction start time (seconds)',
                                    initialvalue=0.0,minvalue=0,maxvalue=sourceVid.duration)
        end = tkSimpleDialog.askfloat('ChamView','Extraction end time (seconds)',
                                    initialvalue=sourceVid.duration,minvalue=start,maxvalue=sourceVid.duration)
        
        #Create the directory
        destination = os.getcwd() + os.path.sep + os.path.basename(source).split('.')[0]
        try:
            os.mkdir(destination)
        except OSError:
            #Directory already exists. Try apending a number on the back
            i = 1
            while os.path.isdir(destination+'('+str(i)+')'):
                i = i + 1
            destination = destination+'('+str(i)+')'
            os.mkdir(destination)
        tkMessageBox.showinfo('ChamView',"Frames will be saved in\n'"+destination+"'")
        
        try:
            #If needed, skip ahead to the start time
            if start > 0:
                #label.config(text='Seeking to first frame')
                notify = start / 10.0
                while time < start:
                    vframe = sourceVid.get_next_video_frame()
                    time = sourceVid.get_next_video_timestamp()
                    if time > notify:
                        progress += int(notify*10.0/start)*10
                        notify = notify + (start / 10.0)
            else:
                vframe = sourceVid.get_next_video_frame()
            
            #Save the video's frames until we run out of them or reach the end time
            #label.config(text='Saving frames')
            progress = 0
            frameCount = 1
            notify = (end-start) / 10.0
            while vframe != None and time <= end:
                if time-start > notify:
                    progress += int(notify*10.0/(end-start))*10
                    notify = notify + ((end-start) / 10.0)
                imageData = vframe.get_image_data()
                pixels = imageData.get_data(imageData.format,imageData.pitch *-1)
                imageData.set_data(imageData.format,imageData.pitch,pixels)
                imageData.save(destination+os.path.sep+"frame"+str(frameCount)+".png")
                time = sourceVid.get_next_video_timestamp()
                vframe = sourceVid.get_next_video_frame()
                frameCount += 1
            tkMessageBox.showinfo('ChamView',"     Success      ")
        except:
            tkMessageBox.showerror('ChamView','Error: Pyglet failure')
            #Rid of the failed, empty directory that we created
            os.rmdir(destination)
        
               
    '''Called when the Select Points button is clicked'''
    def proceed(self):
        if self.checkDir() == "bad dir":
            tkMessageBox.showerror('ChamView', 'Error: directory not found')
        elif self.checkDir() == "no img":
            tkMessageBox.showerror('ChamView', 'Error: no valid images found')
        elif self.checkFPS() == False:
            tkMessageBox.showerror('ChamView', 'Error: FPS must be at least 1')
        else:
            self.master.destroy()

#--- The code that runs upon execution ----------------------------------------#

#Open the first window to choose directory
root = Tk()
app1 = Window1(root)
root.mainloop()

#Did the user close out of the window early?
try:
    iterator = iter(app1.picList)
except TypeError:
    sys.exit()

#Get info from the first window
directory = app1.directory.get().strip()
fList = app1.picList
fps = app1.fps.get()

#Open the second window, which is ChamView                  
root2 = Tk()
app2 = Window2(root2,directory,fList,fps)
root2.mainloop()

