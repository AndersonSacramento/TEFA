from scrolledlist import ScrolledList
from tkinter import *


class LoginPanel(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets(options)


    def makeWidgets(self, options):
        self.annotators_scroll = ScrolledList(options['annotators'], parent=self)
        self.annotators_scroll.pack(side=TOP, expand=YES, fill=BOTH)

        self.annotators_scroll.set_middle_mouse_handle(lambda i,s: self.load_annotator(i,s))
        row = Frame(self)
        lab = Label(row, width=5, text='E-mail')
        ent = Entry(row)
        row.pack(side=TOP, fill=X)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.email_entry = ent
        Button(self, text='Criar', command=self.create_annotator).pack(side=RIGHT)

    def load_annotator(self, i, s):
        print('anotator {} {}'.format(i,s))
        self.on_load_annotator()
        
    def create_annotator(self):
        print(self.email_entry.get())

    def set_on_load_annotator(self, fn):
        self.on_load_annotator = fn

if __name__ == '__main__':
    options = {'annotators':{'title': 'Anotadores', 'data':['ander@mail.com', 'silva@gmail.com']}}

    LoginPanel(options).mainloop()
