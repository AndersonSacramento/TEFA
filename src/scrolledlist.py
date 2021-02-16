"a simple customizable scrolled listbox component"
from tkinter import *

class ScrolledList(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets(options)

    def handleList(self, event):
        index = self.listbox.curselection()
        label = self.listbox.get(index)
        return index, label

    def config_listbox(self, **configs):
        print(configs)
        self.listbox.config(**configs)
        
    def makeWidgets(self, options):
        print(options)
        Label(self, text=options['title']).pack(side=TOP)
        sbar = Scrollbar(self)
        list = Listbox(self, relief=SUNKEN)
        sbar.config(command=list.yview)
        list.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list.pack(side=LEFT, expand=YES, fill=BOTH)
        pos = 0
        if 'data' in options:
            for label in options['data']:
                list.insert(pos, label)
                pos += 1
                #list.config(selectmode=SINGLE, setgrid=1)
        
        self.left_mouse_handle = lambda i, s: None
        
        self.middle_mouse_handle = lambda i, s: None
        
        self.right_mouse_handle = lambda i, s: None
        self.listbox = list

    def remove_line(self, i):
        self.listbox.delete(i)

    def add_line(self, i, s):
        self.listbox.insert(i, s)
        
    def set_left_mouse_handle(self, func):
        self.left_mouse_handle = func
        self.listbox.bind('<Button-1>', self.handle_left_mouse)

    def set_middle_mouse_handle(self, func):
        self.middle_mouse_handle = func
        self.listbox.bind('<Button-2>', self.handle_middle_mouse)

    def set_right_mouse_handle(self, func):
        self.right_mouse_handle = func
        self.listbox.bind('<Button-3>', self.handle_right_mouse)
        
    def handle_left_mouse(self, event):
        index, selection = self.handleList(event)
        self.left_mouse_handle(index, selection)

    def handle_middle_mouse(self, event):
        index, selection = self.handleList(event)
        self.middle_mouse_handle(index, selection)

    def handle_right_mouse(self, event):
        index, selection = self.handleList(event)
        self.right_mouse_handle(index, selection)

if __name__ == '__main__':
    options = (('Lumberjack-%s' % x) for x in range(20))
    ScrolledList(options).mainloop()        
