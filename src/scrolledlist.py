"A simple customizable scrolled listbox component"
from tkinter import *

class ScrolledList(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.config(takefocus=0)
        parent.config(takefocus=0)
        self.options = options
        self.makeWidgets(options)

    def handleList(self, event):
        index = self.listbox.curselection()
        label = self.listbox.get(index)
        return index, label

    def get_current_selection(self):
        index = self.listbox.curselection()
        index = index[0] if index else -1
        label = self.listbox.get(index)
        return index, label

    def get_list_size(self):
        return self.listbox.size()

    def select_item(self, item_index):
        if 0 <= item_index < self.listbox.size() :
            self.listbox.selection_clear(0, END)
            self.listbox.selection_set(item_index)
            self.listbox.see(item_index)

    def is_selected(self):
        index = self.listbox.curselection()
        return len(index) > 0
    
    def select_next(self):
        if self.get_list_size() == 0: return
        index = self.listbox.curselection()
        index = index[0] if index else 0
        print('next index %s' % index)
        index += 1
        index = index % self.listbox.size()
        self.listbox.selection_clear(0,END)
        self.listbox.selection_set(index)
        self.listbox.see(index)


    def select_previous(self):
        if self.get_list_size() == 0: return
        index = self.listbox.curselection()
        index = index[0] if index else 1
        print('previous index %s' % index)
        index -= 1
        index = index % self.listbox.size()
        self.listbox.selection_clear(0,END)
        self.listbox.selection_set(index)
        self.listbox.see(index)
            
    def config_listbox(self, **configs):
        print(configs)
        self.listbox.config(**configs)


    def print_list_size(self):
        size = self.get_list_size()
        title = self.options['title']
        if size > 1:
            title_end =  title[-3:]
            if title_end == 'ada' or title_end == 'ido' or title_end == 'odo':
                title_end += 's'
            text = title[:-3] + title_end + ' %s' % size
        elif size == 1:
            text = title + ' %s' % size
        else:
            text = title
        self.label_title.config(text=text)
        
    
    def set_single_mode(self):
        self.listbox.config(selectmode=SINGLE)

    def set_browse_mode(self):
        self.listbox.config(selectmode=BROWSE)

    def set_multiple_mode(self):
        self.listbox.config(selectmode=MULTIPLE)

    def makeWidgets(self, options):
        print(options)
        label_title = Label(self, text=options['title'], takefocus=0)
        label_title.pack(side=TOP)

        self.label_title = label_title
        
        sbar = Scrollbar(self, takefocus=0)
        list = Listbox(self, relief=SUNKEN,takefocus=1)
        sbar.config(command=list.yview)
        list.config(fg='black', yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list.pack(side=LEFT, expand=YES, fill=BOTH)

        pos = 0
        if 'data' in options:
            for label in options['data']:
                list.insert(pos, label)
                pos += 1
                #
        
        self.left_mouse_handle = lambda i, s: None
        
        self.middle_mouse_handle = lambda i, s: None
        
        self.right_mouse_handle = lambda i, s: None
        self.listbox = list
        self.set_single_mode()

    def remove_line(self, i):
        self.listbox.delete(i)

    def clear_list(self):
        self.listbox.delete(0,END)

    def add_line(self, i, s):
        self.listbox.insert(i, s)

    def get_list_focus(self):
        self.listbox.focus_force()
        

    def set_1_handler(self, func):
        self._1_handler = func
        self.listbox.bind('<KeyPress-1>', self.handler_1)

    def set_2_handler(self, func):
        self._2_handler = func
        self.listbox.bind('<KeyPress-2>', self.handler_2)

    def set_3_handler(self, func):
        self._3_handler = func
        self.listbox.bind('<KeyPress-3>', self.handler_3)
        
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

    def set_return_handler(self, func):
        self.return_key_handler = func
        self.listbox.bind('<Return>', self.handler_return_key)

    def generic_handler_call(self, event, handler_func):
        index, selection = self.handleList(event)
        handler_func(index, selection)


    def handler_return_key(self, event):
        self.generic_handler_call(event, self.handler_return_key)


    def handler_1(self, event):
        self._1_handler(0, '')

    def handler_2(self, event):
        self._2_handler(0, '')
        
    def handler_3(self, event):
        self._3_handler(0, '')

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
