from scrolledlist import ScrolledList
from tkinter import *
import _thread, queue, time
import fnutils


class LoginPanel(Frame):

    dataQueue = queue.Queue()
    
    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets(options)
        


    def makeWidgets(self, options):
        self.annotators_scroll = ScrolledList(options['annotators'], parent=self)
        self.annotators_scroll.set_middle_mouse_handle(lambda i,s: self.load_annotator(i,s))
        row = Frame(self)
        lab = Label(row, width=5, text='E-mail')
        ent = Entry(row)
        row.pack(side=TOP, fill=X)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        self.email_entry = ent
        Button(self, text='Criar', command=self.create_annotator).pack(side=RIGHT)

        self.annotators_scroll.pack(side=TOP, expand=YES, fill=BOTH)
        _thread.start_new_thread(self.load_annotators_thread, ())
        self.update_annotator_list()

    def load_annotator(self, i, s):
        print('anotator {} {}'.format(i,s))
        self.on_load_annotator(s)

        
    def create_annotator(self):
        email = self.email_entry.get()
        email = email.strip()
        if email and email != 'lome':
            _thread.start_new_thread(self.create_annotator_thread, (email,))
        print(email)


    def set_on_load_annotator(self, fn):
        self.on_load_annotator = fn

        
    def create_annotator_thread(self, email):
        annotator = fnutils.create_annotator(email)
        LoginPanel.dataQueue.put(annotator)
            
    def update_annotator_list(self):
        try:
            annotator = LoginPanel.dataQueue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.annotators_scroll.add_line(END, annotator.email)
        self.after(250, lambda: self.update_annotator_list())

    def load_annotators_thread(self):
        for annotator  in fnutils.get_all_annotators(notin_emails=['lome']):
            LoginPanel.dataQueue.put(annotator)

if __name__ == '__main__':
    options = {'annotators':{'title': 'Anotadores'}}#, 'data':['ander@mail.com', 'silva@gmail.com']}}
    #fnutils.create_session()
    LoginPanel(options).mainloop()
