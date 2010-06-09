import os, string, dircache, time, shutil
from Tkinter import *
import Image, ImageTk, ImageGrab
import cv


##Notes:
##button fxns will run as soon as button is made if callback includes ()
##span starts in top left
##anchor neccessary or image will not fit correctly
##event is neccessary argument for event-bound items


#second 'main' window
class PickClick: 

    def __init__(self, master, directory,fList):

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
                

        #gets fps from first filename in fDic
        dirName = self.directory.split(os.path.sep)[-1]
        length = len(dirName)
        self. fps = float(self.fDic['1'][length:-13])
        print self.fps
        
        self.length = len(self.fDic)
        #open file for reading/writing coords, name based on given image directory
        fo = open(self.directory+os.path.sep+self.dirList[-1]+'.txt','a')

        self.num = StringVar()
        self.num.set(1)
        
        self.frame = Frame(master)
        master.title('ChamView')
        self.frame.grid(columnspan=8,rowspan=5)
        #binds shortcut keys
        self.frame.bind_all('<a>', self.Prev)
        self.frame.bind_all('<A>', self.Prev)
        self.frame.bind_all('<d>', self.Nxt)
        self.frame.bind_all('<d>', self.Nxt)
        self.frame.bind_all('<p>', self.Play)
        self.frame.bind_all('<o>', self.Pause)
        self.frame.bind_all('<i>',self.Rewind)
        self.frame.bind_all('<s>',self.SaveAll)
        
        #quit button
        self.quitB = Button(self.frame,text='QUIT',command = master.quit)
        self.quitB.grid(column=8,row=1)
        #previous button
        self.prevB = Button(self.frame, text = 'PREV',command = self.Prev) 
        self.prevB.grid(column=4,row=5)
        
        self.prev10B = Button(self.frame, text = 'PREV10',command = self.Prev10)
        self.prev10B.grid(column=3,row=5)
        
        self.prev100B = Button(self.frame, text = 'PREV100',command = self.Prev100)
        self.prev100B.grid(column=2,row=5)
        #first button
        self.firstB = Button(self.frame, text = 'FIRST',command = self.First)
        self.firstB.grid(column=1,row=5)
        #next button
        self.nextB = Button(self.frame,text='NEXT',command = self.Nxt)
        self.nextB.grid(column=5,row=5)
        
        self.next10B = Button(self.frame, text = 'NEXT10',command = self.Nxt10)
        self.next10B.grid(column=6,row=5)
        
        self.next100B = Button(self.frame, text = 'NEXT100',command = self.Nxt100)
        self.next100B.grid(column=7,row=5)
        #last button
        self.lastB = Button(self.frame,text='LAST',command = self.Last)
        self.lastB.grid(row=5,column=8)
        #frame label
        self.numLab = Label(self.frame,textvariable = self.num)
        self.numLab.grid(column=1,row=1,sticky=W)
        #clear all of points
        self.clearB = Button(self.frame,text='CLEAR ALL',command = self.Clear)
        self.clearB.grid(column=7,row=1,sticky=E) 
        #clear frame of poits
        self.clearFrameB = Button(self.frame,text='CLEAR FRAME',command=self.ClearPic)
        self.clearFrameB.grid(column=6,row=1,sticky=E) 
        #saves frame with points as png
        self.saveB = Button(self.frame,text = 'SAVE IMAGE',command = self.SaveImg)
        self.saveB.grid(column=2,row=1)
        #save all button
        self.saveAllB = Button(self.frame,text='SAVE FROM CURRENT FRAME',command = self.SaveAll)
        self.saveAllB.grid(column=3,row=1, columnspan=2)
        #shows directory
        self.dirLab = Label(self.frame,text=self.directory)
        self.dirLab.grid(row=4,column=1,sticky=W)
        #shows file with point coords
        self.fileLab = Label(self.frame,text = self.dirList[-1]+'.txt')
        self.fileLab.grid(row=4,column=8,sticky=E)
        #rewind button
        self.rewB = Button(self.frame,text = 'REW.',command = self.Rewind)
        self.rewB.grid(row=4,column=3)
        #pause button
        self.pauseB = Button(self.frame,text='PAUSE',command=self.Pause)
        self.pauseB.grid(row=4,column=4,columnspan=2)
        #play button
        self.playB = Button(self.frame,text='PLAY',command=self.Play)
        self.playB.grid(row=4,column=6)
        
        self.canv = Canvas(self.frame)
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
        #coords are two opposite corners of circle
        circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),
                                      fill = 'yellow',activefill = 'red')
        #tags item so it can be used(deleted) later
        self.canv.itemconfigure(circId,tags=(str(circId)+'c'))
        #binds item to unclick
        self.canv.tag_bind(str(circId)+'c','<Button-1>',self.UnClick)
        #writes coordinates of circle, tag/id of circle to file
        stri = (self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)
                +':'+str(event.y+3)+':'+str(circId)+'c')
        
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
                circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),
                                               fill = 'yellow',activefill = 'red')
                #tags item with id of original circle so it can be used(deleted) later
                self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1])
                #binds item to unclick
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
        '''Saves all frames as pngs'''
        #stop other play/pause 
        self.go = False
        dirName = self.directory+os.path.sep+'annotated'
        try:
            #make a new directory to put dotted frames in
            os.mkdir(dirName)
        except WindowsError:
            pass
        #allow saveAll while loop to run
        self.go = True
        #will run while not at max frame number, self.go controlled by Pause
        while int(self.num.get()) < self.length and self.go == True:
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
            fileName = dirName+os.path.sep+self.fDic[self.num.get()]
            self.canv.update()
            x0 = self.canv.winfo_rootx()
            y0 = self.canv.winfo_rooty()
            x1 = x0 + self.canv.winfo_width()
            y1 = y0 + self.canv.winfo_height()
            offset1 = 0
            offset2 = 0
            im = ImageGrab.grab((x0-offset1, y0-offset1, x1+offset2,y1+offset2))
            im.save(fileName)
            if int(self.num.get()) == self.length:
                self.go = False
            
        
        


#first window, choose directory for CV or make frames from video
class ChooseDir:
    def __init__(self,master):

        self.master = master
        self.frame = Frame(master)
        master.title('Choose Directory')
        self.frame.grid(rowspan=6,columnspan=2)

        self.directory = StringVar()
        self.directory.set(os.curdir)
        
        self.vidDir = StringVar()
        self.frameNum = StringVar()
        self.frameNum.set('-----')
	
        self.dirInput = Entry(self.frame,textvariable=self.directory,width=40)
        self.dirInput.grid(row=5,column=1)
        
        self.dirLab = Label(self.frame,text='View/annotate frames')
        self.dirLab.grid(row=4,column=1)

        self.dirLabel = Label(self.frame,text='-----')
        self.dirLabel.grid(row=5,column=2) 

        self.okButton = Button(self.frame,text='OK',command=self.ShowLab)
        self.okButton.grid(row=6,column=1)
        
        self.vidBox = Entry(self.frame,textvariable=self.vidDir,width=40)
        self.vidBox.grid(row=2,column=1)
        
        self.vidLab = Label(self.frame,text='Convert avi to frames')
        self.vidLab.grid(row=1,column=1)
        
        self.vidOK = Button(self.frame,text='OK',command=self.MakeFrames)
        self.vidOK.grid(row=3,column=1)

        self.vidLab2 = Label(self.frame,textvariable=self.frameNum)
        self.vidLab2.grid(row=2,column=2)

    def MakeFrames(self):
        '''Converts video file into frames'''
        valid = False
        #name of video file
        vidFil = self.vidDir.get()
        vidFil = self.vidDir.get().strip()
        filList = vidFil.split(os.path.sep)
        if '.mpg' in filList[-1] or '.avi' in filList[-1]:
            valid = True
        if valid == True and os.path.isfile(vidFil):
            #prefix to be used for frame files
            name = filList[-1][:-4]

            capture = cv.CaptureFromFile(vidFil)
            fps = cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FPS)

            #first two digits of num are fps
            num = int(str(int(fps))+'000000001')
            n = 0
            while 1:
                try:
                    #make a new directory based on named of video file
                    #keep trying until an unused directory is found
                    dirName = name+str(n)
                    os.mkdir(dirName)
                    break
                except WindowsError:
                    n = n + 1
                    continue
            while True:
                frame = cv.QueryFrame(capture)
                #end loop if no more frames
                if frame == None:
                    self.frameNum.set('Complete')
                    self.directory.set(dirName)
                    break

                #save image with num as part of filename and moves it to directory
                cv.SaveImage(dirName + str(num)+'.png',frame)
                shutil.move(dirName + str(num)+'.png',dirName)
                num = num + 1
                self.frameNum.set(num - int(str(int(fps))+'000000001'))
                self.frame.update()
        else:
            self.frameNum.set('Invalid file')    

    def ShowLab(self):
        '''Shows label if okay button is pressed'''
        boo = False
        try:
            #get rid of label if it already exists
            self.dirLabel.destroy()
        except:
            pass
        directory = self.directory.get().strip()
        #check if this is a valid directory
        if os.path.isdir(directory):
            self.picList = dircache.listdir(directory)
            #checks if pictures are usable
            for pic in self.picList:
                if '.png' in pic or '.PNG' in pic  \
                or '.jpg'in pic or '.JPG' in pic   \
                or '.bmp' in pic or '.BMP' in pic  \
                or '.gif' in pic or '.GIF' in pic:
                    boo = True
            if boo == True:
                #valid label
                self.dirLabel = Label(self.frame,text='Valid images found in directory')
                self.dirLabel.grid(row=5,column=2)
                #get ok button out of the way
                self.okButton.destroy()
                #brings up continue button which will close window
                self.contButton = Button(text='CONTINUE',command = self.master.destroy)
                self.contButton.grid(row=6,column=1)
            else:
                #Prints invalid if no .gifs in file
                self.dirLabel = \
                Label(self.frame,text='No valid image files found in the directory') 
                self.dirLabel.grid(row=5,column=2) 
        else:
            #prints invalid is directory is invalid
            self.dirLabel = Label(self.frame,text=directory+' - Invalid Directory')
            self.dirLabel.grid(row=5,column=2)
        


root = Tk()
#first window, choose directory for CV or make frames from video
app = ChooseDir(root)
root.mainloop()


#name of directory as string
directory = app.directory.get().strip()
#list of files in directory including non-usable files
fList = app.picList 
        
        
                
#second window, ChamView                    
root2 = Tk()
app2 = PickClick(root2,directory,fList)
root2.mainloop()

