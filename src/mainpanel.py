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
        self.load_sentences_frame(None)
        

    def load_sentences_frame(self, email):
        annotator = fnutils.find_unique_annotator()
        if annotator:
            self.options['email'] = annotator.email
        else:
            self.options['email'] = 'anonymous'
            fnutils.create_annotator(self.options['email'])
        self.sentences_frame = SentencesPanel(self.options, parent=self)
        self.sentences_frame.pack(side=TOP, expand=YES, fill=BOTH)
        

    def handle_back_btn(self):
        self.back_btn.pack_forget()
        self.sentences_frame.pack_forget()
        self.login_frame.pack(side=TOP, expand=YES, fill=BOTH)

if __name__ == '__main__':
    options = {'todo':{'title': 'Anotar'},
               'doing':{'title': 'Anotando'},
               'done': {'title': 'Anotada'},
               'annotators':{'title': 'Anotadores'}}
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
