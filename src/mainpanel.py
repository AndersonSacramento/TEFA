from sentencespanel import SentencesPanel
from loginpanel import LoginPanel
from tkinter import *
import _thread, queue, time
import fnutils

class MainPanel(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets(options)
        self.options = options


    def makeWidgets(self, options):
        self.login_frame = LoginPanel(options, parent=self)
        self.login_frame.set_on_load_annotator(self.load_sentences_frame)

    def load_sentences_frame(self, email):
        self.login_frame.pack_forget()
        self.back_btn = Button(self, text='Retornar', command=self.handle_back_btn)
        self.back_btn.pack(side=TOP, anchor=NW)
        self.options['email'] = email
        self.sentences_frame = SentencesPanel(self.options, parent=self)
        self.sentences_frame.pack(side=TOP, expand=YES, fill=BOTH)

    def handle_back_btn(self):
        self.back_btn.pack_forget()
        self.sentences_frame.pack_forget()
        self.login_frame.pack(side=TOP, expand=YES, fill=BOTH)

        
if __name__ == '__main__':
    options = {'todo':{'title': 'Anotar'}, # 'data':['sent1', 'sent2']},
               'doing':{'title': 'Anotando'},# 'data':[]},
               'done': {'title': 'Anotado'},#, 'data':['sent0'] },
               'annotators':{'title': 'Anotadores'}}#'data':['ander@mail.com', 'silva@gmail.com']}}
    fnutils.create_session()
    MainPanel(options).mainloop()
