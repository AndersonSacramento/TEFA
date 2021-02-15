from tkinter import *
from scrolledlist import ScrolledList



class MainPanel(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets(options)


    def makeWidgets(self, options):
        self.todo_scroll = ScrolledList(options['todo'], parent=self)
        self.doing_scroll = ScrolledList(options['doing'], parent=self)
        self.done_scroll = ScrolledList(options['done'], parent=self)

        self.todo_scroll.pack(side=LEFT, expand=YES, fill=BOTH)
        self.doing_scroll.pack(side=LEFT, expand=YES, fill=BOTH)
        self.done_scroll.pack(side=LEFT, expand=YES, fill=BOTH)

if __name__ == '__main__':
    options = {'todo':{'title': 'To Do', 'data':['sent1', 'sent2']},
               'doing':{'title': 'Doing', 'data':[]},
               'done': {'title': 'Done', 'data':['sent0'] }}
    MainPanel(options).mainloop()
