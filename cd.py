from Tkinter import *
import string
import dircache
import os
import Image
import time

#button fxns will run as soon as button is made if callback includes ()
class PickClick:#second 'main' window

    def __init__(self, master, directory,fList):

        self.directory = directory
        self.dirList = self.directory.split(os.path.sep)#only one backslash in reality

        self.fList = fList
        self.fDic = {}
        n = 1
        for image in self.fList:#makes .gif of all .png files
            if '.PNG' in image or '.png' in image:
                Image.open(image).save(image[0:-4]+'.gif')
                self.fList = dircache.listdir(directory)

            
        for image2 in self.fList: #puts files in order so they can be iterated through one at a time
            if '.gif' in image2 or '.GIF' in image2:
                self.fDic[str(n)] = image2
                n = n + 1

        self.length = len(self.fDic)
        
        fo = open(self.dirList[-1]+'.txt','a')#open file for reading/writing coords
        #name based on given image directory

        self.num = StringVar()#so label updates
        self.num.set(1)
        
        self.frame = Frame(master)
        master.title('ChamView')
        self.frame.grid(columnspan=8,rowspan=5)
        self.frame.bind_all('<a>', self.Prev)
        self.frame.bind_all('<A>', self.Prev)
        self.frame.bind_all('<d>', self.Nxt)
        self.frame.bind_all('<d>', self.Nxt)
##        self.frame.bind_all('<p>', self.Play)
        
        
        
        self.quitB = Button(self.frame,text='QUIT',command = master.quit)#quit button
        self.quitB.grid(column=8,row=1)

        self.prevB = Button(self.frame, text = 'PREV',command = self.Prev) #previous button
        self.prevB.grid(column=4,row=5)

        self.prev10B = Button(self.frame, text = 'PREV10',command = self.Prev10)
        self.prev10B.grid(column=3,row=5)

        self.prev50B = Button(self.frame, text = 'PREV100',command = self.Prev100)
        self.prev50B.grid(column=2,row=5)

        self.firstB = Button(self.frame, text = 'FIRST',command = self.First)
        self.firstB.grid(column=1,row=5)
        
        self.nextB = Button(self.frame,text='NEXT',command = self.Nxt)#next button
        self.nextB.grid(column=5,row=5)
        
        self.next10B = Button(self.frame, text = 'NEXT10',command = self.Nxt10)
        self.next10B.grid(column=6,row=5)

        self.next50B = Button(self.frame, text = 'NEXT100',command = self.Nxt100)
        self.next50B.grid(column=7,row=5)

        self.lastB = Button(self.frame,text='LAST',command = self.Last)
        self.lastB.grid(row=5,column=8)
        
        self.numLab = Label(self.frame,textvariable = self.num)#label depicting current frame
        self.numLab.grid(column=1,row=1,sticky=W)

        self.clearB = Button(self.frame,text='CLEAR ALL',command = self.Clear)
        self.clearB.grid(column=7,row=1,sticky=E) #clears all point data

        self.clearFrameB = Button(self.frame,text='CLEAR FRAME',command=self.ClearPic)
        self.clearFrameB.grid(column=6,row=1,sticky=E) #clears points on current frame

        self.saveB = Button(self.frame,text = 'SAVE IMAGE',command = self.SaveImg)
        self.saveB.grid(column=2,row=1)#saves frame with points as postscript image

        self.dirLab = Label(self.frame,text=self.directory)
        self.dirLab.grid(row=4,column=1,columnspan=4,rowspan=1,sticky=W)

        self.fileLab = Label(self.frame,text = self.dirList[-1]+'.txt')
        self.fileLab.grid(row=4,column=5,columnspan=4,rowspan=1,sticky=E)
        
        self.canv = Canvas(self.frame)
        self.canv.grid(column=1,row=2,columnspan = 8, rowspan = 2)#span starts in top left
        
        imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
        self.photo = PhotoImage(file = imageFile)
        #returns id as self.obj
        self.obj = self.canv.create_image(2,2 ,image = self.photo,tags = (self.num.get()+'n'),anchor=NW)#anchor neccessary or image will not fit correctly
        boo = self.Check(self.num.get()+'n')#checks if image has any points
        if boo:
            self.ReDraw(self.num.get()+'n')#draws points if so
        self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to create circle
        self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image

        fo.close()
        

    def Nxt(self,event=''):
        '''Advances picture in directory'''
        try:
            self.num.set(int(self.num.get())+1)

            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so
            #self.canv.tag_raise(self.obj)
        except:
            self.num.set(self.length)

    def Nxt10(self):
        '''Advances 10 frames'''
        try:
            self.num.set(int(self.num.get())+10)

            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so
        except:
            self.num.set(self.length)
            
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so

    def Nxt100(self):
        '''Advances 100 frames'''
        try:
            self.num.set(int(self.num.get())+100)

            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so
        except:
            self.num.set(self.length)
            
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so

    def Last(self):
        '''Advances to last frame'''
        self.num.set(self.length)

        imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
        self.photo = PhotoImage(file = imageFile)
        self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
        self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
        self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
        boo = self.Check(self.num.get()+'n')#checks if image has any points
        if boo:
            self.ReDraw(self.num.get()+'n')#draws points if so
            
    def Prev(self,event=''):
        '''Previous picture in directory'''
        #self.canv.delete(self.obj)
        try:
            self.num.set(int(self.num.get())-1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor=NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so
            #self.canv.tag_raise(self.obj)
        except:
            self.num.set(1)

    def Prev10(self):
        '''Go 10 frames back'''
        try:
            self.num.set(int(self.num.get())-10)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor=NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so
        except:
            self.num.set(1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor=NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so

    def Prev100(self):
        '''Go 100 frames back'''
        try:
            self.num.set(int(self.num.get())-100)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor=NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so
        except:
            self.num.set(1)
            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
            self.photo = PhotoImage(file = imageFile)
            self.canv.config(width = self.photo.width(),height = self.photo.height())
            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor=NW)#anchor
            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
            boo = self.Check(self.num.get()+'n')#checks if image has any points
            if boo:
                self.ReDraw(self.num.get()+'n')#draws points if so

##    def Play(self,event=''):
##        '''Animates video sequence'''
##        while True:
##            #try:
##            self.num.set(int(self.num.get())+1)
##
##            imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
##            self.photo = PhotoImage(file = imageFile)
##            self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
##            self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
##            self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
##            boo = self.Check(self.num.get()+'n')#checks if image has any points
##            if boo:
##                self.ReDraw(self.num.get()+'n')#draws points if so
##            time.sleep(.80)
####            except:
####                self.num.set(self.length)
####                break

    def First(self):
        '''Go to last frame'''
        self.num.set(1)

        imageFile = self.directory+os.path.sep+self.fDic[self.num.get()]
        self.photo = PhotoImage(file = imageFile)
        self.canv.config(width = self.photo.width(),height = self.photo.height())#size canvas to image
        self.obj = self.canv.create_image((0,0),image = self.photo,tags = (self.num.get()+'n'),anchor = NW)#anchor
        self.canv.tag_bind(self.obj,'<Button-1>',self.Click)#binds click to this picture
        boo = self.Check(self.num.get()+'n')#checks if image has any points
        if boo:
            self.ReDraw(self.num.get()+'n')#draws points if so

    def Click(self,event):#event is neccessary argument
        '''Creates circles on click and records tag of picture as well as circle coords in file'''
        fo = open(self.dirList[-1]+'.txt','a')
        circId =self.canv.create_oval((event.x-3,event.y-3,event.x+3,event.y+3),fill = 'yellow',activefill = 'red')#coords are two opposite corners of circle
        self.canv.itemconfigure(circId,tags=(str(circId)+'c'))#tags item so it can be used(deleted) later
        self.canv.tag_bind(str(circId)+'c','<Button-1>',self.UnClick)#binds item to unclick
        
        stri = self.num.get()+'n:'+str(event.x-3)+':'+str(event.y-3)+':'+str(event.x+3)+':'+str(event.y+3)+':'+str(circId)+'c'
        
        fo.write(stri+'\n')
        fo.close()


    def UnClick(self,event):
        '''Deletes point circles when they are clicked'''
        x,y = self.canv.canvasx(event.x),self.canv.canvasy(event.y)
        closeItem = self.canv.find_closest(x,y)[0]
        tags = self.canv.gettags(closeItem) #gets tag of the closest item
        
        fin = open(self.dirList[-1]+'.txt','r')#original file
        fout = open('temp.txt','w') #temporary file
        
        for line in fin:
            lineLst = line.split(':')
            if lineLst[-1][0:-1] == tags[0]: #prevents this from deleting the main picture
                self.canv.delete(tags[0])
            else:
                fout.write(line)#if item not deleted, line is written to temp file

        fin.close()
        fout.close()
        
        fin2 = open(self.dirList[-1]+'.txt','w')#orig,wiped clean
        fout2 = open('temp.txt','r')#temp

        for line2 in fout2:
            fin2.write(line2)#copies temp file to orig file
        
        fin2.close()
        fout2.close()
            
    def ClearPic(self):
        '''Clears current frame of points'''
        fin = open(self.dirList[-1]+'.txt','r')#original file
        fout = open('temp.txt','w') #temporary file
        
        for line in fin:
            lineLst = line.split(':')
            if lineLst[0] == (self.num.get()+'n'):
                self.canv.tag_raise((self.num.get()+'n'))
            else:
                fout.write(line)#if item not deleted, line is written to temp file

        fin.close()
        fout.close()
        
        fin2 = open(self.dirList[-1]+'.txt','w')#orig,wiped clean
        fout2 = open('temp.txt','r')#temp

        for line2 in fout2:
            fin2.write(line2)#copies temp file to orig file
        
        fin2.close()
        fout2.close()
        
        

    def ReDraw(self,tag):
        '''Redraws circles on picture'''
        boo = False
        fo = open(self.dirList[-1]+'.txt','r')
        for line in fo: #redraws circles based on coordinates in file
            lineLst = line.split(':')
            if lineLst[0] == tag:
                circId = self.canv.create_oval((lineLst[1],lineLst[2],lineLst[3],lineLst[4]),fill = 'yellow',activefill = 'red')
                self.canv.itemconfigure(circId,tags=lineLst[-1][0:-1]) #tags item with id of original circle so it can be used(deleted) later
                self.canv.tag_bind(lineLst[-1][0:-1],'<Button-1>',self.UnClick)#binds item to unclick
        fo.close()

    def Check(self,tag):
        '''Checks if current picture has any points clicked'''
        boo = False
        fo = open(self.dirList[-1]+'.txt','r')
        for line in fo:
            lineLst = line.split(':')
            if lineLst[0] == tag:
                boo = True      
        return boo
        fo.close()

    def Clear(self):
        '''Clears file of all points'''
        self.canv.tag_raise((self.num.get()+'n'))#clears current frame so user isn't confused
        fo = open(self.dirList[-1]+'.txt','w')
        fo.close()

    def SaveImg(self):
        filename = self.directory+os.path.sep+self.fDic[self.num.get()][0:-4]
        self.canv.postscript(file=(filename+'.ps'),height=self.photo.height(),width=self.photo.width(),colormode="color")
        Image.open(filename+'.ps').save(filename+'.png')

class ChooseDir: #first window allowing user to choose directory
    def __init__(self,master):

        self.master = master
        self.frame = Frame(master)
        master.title('Choose Directory')
        self.frame.grid()

        self.directory = StringVar()
##        self.imgDir = StringVar()
##        self.vidDir = StringVar()
        
	self.directory.set(os.curdir)
        self.dirInput = Entry(self.frame,textvariable=self.directory,width=40)
        self.dirInput.grid()

        self.okButton = Button(self.frame,text='OK',command=self.ShowLab)
        self.okButton.grid()
        
##        self.vidBox = Entry(self.frame,textvariable=self.vidDir,width=40)
##        self.vidBox.grid()
##        self.vidLab = Label(self.frame,text='')
##        self.vidLab.grid()
##
##        self.dirBox = Entry(self.frame,textvariable=self.imgDir,width=40)
##        self.dirBox.grid()
##        self.dirLab = Label(self.frame,text=''



    def ShowLab(self):
        '''Shows label if okay button is pressed'''
        boo = False
        try: #gets rid of label if it already exists
            self.dirLabel.destroy()
        except:
            pass
        directory = self.directory.get().strip()
        if os.path.isdir(directory):#checks if this is a valid directory
            self.picList = dircache.listdir(directory)
            for pic in self.picList:
                if '.png' in pic or '.PNG' in pic: #checks if pictures are .gifs
                    boo = True
            if boo == True: #will bring up continue button if everything works
                self.contButton = Button(text='CONTINUE',command = self.master.destroy) #brings up continue button which will close window
                self.contButton.grid()
            else:
                self.dirLabel = Label(self.frame,text='No png files found in the directory')
                self.dirLabel.grid() #Prints invalid if no .gifs in file
        else:
            self.dirLabel = Label(self.frame,text=directory+' - Invalid Directory')
            self.dirLabel.grid() #prints invalid is directory is invalid
        


root = Tk()
app = ChooseDir(root) #first window, choose directory
root.mainloop()



directory = app.directory.get().strip()#name of directory as string
fList = app.picList #list of files in directory including non-.gifs
        
        
                
                      
root2 = Tk() #second window, main application
app2 = PickClick(root2,directory,fList)
root2.mainloop()

