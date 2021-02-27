"a simple customizable scrolled listbox component"
from tkinter import *

class ScrolledList(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.config(takefocus=0)
        parent.config(takefocus=0)
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
        Label(self, text=options['title'], takefocus=0).pack(side=TOP)
        sbar = Scrollbar(self, takefocus=0)
        list = Listbox(self, relief=SUNKEN,takefocus=1)
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

    def clear_list(self):
        self.listbox.delete(0,END)

    def add_line(self, i, s):
        self.listbox.insert(i, s)

    def get_list_focus(self):
        self.listbox.focus_force()
        
        
    def set_ctrl_1_handler(self, func):
        self.ctrl_1_handler = func
        self.listbox.bind('<Control-Key-1>', self.handler_ctrl_1)

    def set_ctrl_2_handler(self, func):
        self.ctrl_2_handler = func
        self.listbox.bind('<Control-Key-2>', self.handler_ctrl_2)

    def set_ctrl_3_handler(self, func):
        self.ctrl_3_handler = func
        self.listbox.bind('<Control-Key-3>', self.handler_ctrl_3)        
        
    def set_left_arrow_handler(self, func):
        self.left_arrow_handler = func
        self.listbox.bind('<Left>', self.handler_left_arrow)

    def set_right_arrow_handler(self, func):
        self.right_arrow_handler = func
        self.listbox.bind('<Right>', self.handler_right_arrow)

    def set_a_key_handler(self, func):
        self.a_key_handler = func
        self.listbox.bind('<Key-a>', self.handler_a_key)
        
    def set_double_1_handler(self, func):
        self.double_1_handler = func
        self.listbox.bind('<Double-1>', self.handler_double_1)
        
    def set_left_mouse_handle(self, func):
        self.left_mouse_handle = func
        self.listbox.bind('<B1-Motion>', self.handle_left_mouse)

    def set_middle_mouse_handle(self, func):
        self.middle_mouse_handle = func
        self.listbox.bind('<Button-2>', self.handle_middle_mouse)

    def set_right_mouse_handle(self, func):
        self.right_mouse_handle = func
        self.listbox.bind('<B3-Motion>', self.handle_right_mouse)



    def generic_handler_call(self, event, handler_func):
        index, selection = self.handleList(event)
        handler_func(index, selection)


    def handler_ctrl_1(self, event):
        self.ctrl_1_handler(0, '')

    def handler_ctrl_2(self, event):
        self.ctrl_2_handler(0, '')        

    def handler_ctrl_3(self, event):
        self.ctrl_3_handler(0, '')        
        
    def handler_left_arrow(self, event):
        self.generic_handler_call(event, self.left_arrow_handler)

    def handler_right_arrow(self, event):
        self.generic_handler_call(event, self.right_arrow_handler)

    def handler_a_key(self, event):
        self.generic_handler_call(event, self.a_key_handler)
        
    def handler_double_1(self, event):
        index, selection = self.handleList(event)
        self.double_1_handler(index, selection)
        
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
