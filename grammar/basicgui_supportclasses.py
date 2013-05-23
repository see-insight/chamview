# class to create simple entry oriented Dialog Windows

from Tkinter import *


class StatusBar(Frame):
    
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=GROOVE)
        self.label.pack(fill=X)
        
    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()
        
    def clear(self):
        self.label.config(text='')
        self.label.update_idletasks()
        
##################################################

class Dialog(Toplevel): 
           
    def __init__(self, parent, title = None):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)

        self.parent = parent
        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT,padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("&lt;Return>", self.ok)
        self.bind("&lt;Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        return 1 # override

    def apply(self):
        pass # override
     
##################################################        

class EditPointKinds(Dialog):
    
    def __init__(self, parent, pointlist=[], title=None):
        self.currentpoints = pointlist
        self.num_added = 0
        self.deleted_indices = []
        Dialog.__init__(self,parent,title)
        
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.
        self.topframe = Frame(master)
        self.topframe.grid(padx=15,pady=15)
        self.listbox = Listbox(self.topframe,width=45,relief=SUNKEN)
        self.listbox.pack(fill=BOTH)
        for kind in self.currentpoints:
            self.listbox.insert(END,kind)
        self.listbox.bind('<<ListboxSelect>>',self.highlight)
        
        self.bottomframe = Frame(master,height=70,width=295)
        self.bottomframe.grid(row=1,padx=15,pady=15)
        self.ptkind = StringVar()
        self.entry = Entry(self.bottomframe,textvariable=self.ptkind,
                    width=35,relief=SUNKEN)
        self.ptkind.set('Type entry here')
        self.entry.pack(side=LEFT,fill=Y)
        self.add = Button(self.bottomframe,text='Add',command=self.add)
        self.add.pack(side=LEFT,fill=Y)
        self.delete = Button(self.bottomframe,text='Delete',command=self.delete)
        self.delete.pack(side=LEFT,fill=Y)
        
    def highlight(self,event=''):
        #Set the listbox's selection
        try:
            self.point = int(self.listbox.curselection()[0])
        except IndexError:
            pass
        self.listbox.selection_set(self.point)
        self.listbox.see(self.point)
        self.listbox.activate(self.point)
        
    def add(self,event=''):
        self.listbox.select_clear(ACTIVE)
        self.listbox.insert(END,self.ptkind.get())
        self.point = self.listbox.size()-1
        self.listbox.selection_set(self.point)
        self.listbox.see(self.point)
        self.listbox.activate(self.point)
        self.num_added += 1
        
    def delete(self,event=''):
        original_index = self.currentpoints.index(self.listbox.get(ACTIVE))
        if original_index < len(self.currentpoints):
            self.deleted_indices.append(original_index)
        self.listbox.delete(ACTIVE) 
        
    def apply(self):
        self.result = (self.listbox.get(0,END), 
                       self.num_added, 
                       self.deleted_indices)


