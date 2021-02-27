from scrolledlist import ScrolledList
from tkinter import *
import _thread, queue, time



class SearchAnnotatorFrame(Frame):

    def __init__(self, optinos, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.options = options
        self.make_widgets()
        self.load_content()

    def make_widgets(self):
        row_email = Frame(self)

        self.ent_email = Entry(row_email, text='Digite o email')
        btn_search = Button(row_email, text='Pesquisar', command=self.cmd_search_annotator)

        row_email.pack(side=TOP, fill=X)
        ent_email.pack(side=LEFT)
        btn_search.pack(side=RIGHT, expand=YES, fill=X)
        

    def load_content(self):
        self.annotator_queue = queue.Queue()
        self.annotator = None

    def cmd_search_annotator(self):
        email = self.ent_email.get().strip()
        if email:
            _thread.start_new_thread(self.search_annotator, (email,))

    def search_annotator(self, email):
        annotator = datasource.search_annotator(email)
        if annotator:
            self.annotator_queue.put(annotator)

    def result_annotator_search(self):
        try:
            annotator = self.annotator_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.on_annotator_result(annotator)
        self.after(50, self.result_annotator_search)
