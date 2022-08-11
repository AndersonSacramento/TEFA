from sentencespanel import SentencesPanel
from loginpanel import LoginPanel
from tkinter import *
import _thread, queue, time
import fnutils
import sys

class MainPanel(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.options = options
        self.makeWidgets(options)



    def makeWidgets(self, options):
        #self.login_frame = LoginPanel(options, parent=self)
        #self.login_frame.set_on_load_annotator(self.load_sentences_frame)
        self.load_sentences_frame(None)
        

    def load_sentences_frame(self, email):
        #self.login_frame.pack_forget()
        #self.back_btn = Button(self, text='Retornar', command=self.handle_back_btn)
        #self.back_btn.pack(side=TOP, anchor=NW)
        annotator = fnutils.find_unique_annotator()
        if annotator:
            self.options['email'] = annotator.email
        else:
            self.options['email'] = 'anonymous'
        self.sentences_frame = SentencesPanel(self.options, parent=self)
        self.sentences_frame.pack(side=TOP, expand=YES, fill=BOTH)
        

    def handle_back_btn(self):
        self.back_btn.pack_forget()
        self.sentences_frame.pack_forget()
        self.login_frame.pack(side=TOP, expand=YES, fill=BOTH)

if __name__ == '__main__':
    options = {'todo':{'title': 'Anotar'}, # 'data':['sent1', 'sent2']},
               'doing':{'title': 'Anotando'},# 'data':[]},
               'done': {'title': 'Anotada'},#, 'data':['sent0'] },
               'annotators':{'title': 'Anotadores'}}#'data':['ander@mail.com', 'silva@gmail.com']}}
    if len(sys.argv) > 1:
        fnutils.create_session(dbpath=sys.argv[1])
    else:
        fnutils.create_session()
    root = Tk()
    root.title('TEFA')
    main_panel = MainPanel(options, parent=root)
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    root.mainloop()
