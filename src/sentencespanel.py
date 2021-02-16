from scrolledlist import ScrolledList
from tkinter import *
import _thread, queue, time
import fnutils

class SentencesPanel(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets(options)
        self.options = options
        self.todo_queue = queue.Queue()
        self.doing_queue = queue.Queue()
        self.done_queue = queue.Queue()
        self.load_content()


    def makeWidgets(self, options):
        self.todo_scroll = ScrolledList(options['todo'], parent=self)
        self.todo_scroll.config_listbox(bg='tomato')
        self.doing_scroll = ScrolledList(options['doing'], parent=self)
        self.doing_scroll.config_listbox(bg='aquamarine')
        self.done_scroll = ScrolledList(options['done'], parent=self)
        self.done_scroll.config_listbox(bg='SteelBlue1')

        self.todo_scroll.pack(side=LEFT, expand=YES, fill=BOTH)
        self.doing_scroll.pack(side=LEFT, expand=YES, fill=BOTH)
        self.done_scroll.pack(side=LEFT, expand=YES, fill=BOTH)

        self.todo_scroll.set_right_mouse_handle(lambda i,s: self.todo_to_doing(i,s))

        self.doing_scroll.set_left_mouse_handle(lambda i,s: self.doing_to_todo(i,s))
        self.doing_scroll.set_right_mouse_handle(lambda i,s: self.doing_to_done(i,s))

        self.done_scroll.set_left_mouse_handle(lambda i,s: self.done_to_doing(i,s))

    def load_content(self):
        self.set_email(self.options['email'])
        _thread.start_new_thread(self.load_sentences, ('todo',))
        _thread.start_new_thread(self.load_sentences, ('doing',))
        _thread.start_new_thread(self.load_sentences, ('done',))

        self.update_todo_sentence_list()
        self.update_doing_sentence_list()
        self.update_done_sentence_list()

    def set_email(self, email):
        self.email = email
        
    def load_sentences(self, status):
        status_queue = {'todo': self.todo_queue ,
                        'doing':self.doing_queue,
                        'done': self.done_queue}
        for sentence in fnutils.load_sentences(self.email, status):
            status_queue[status].put(sentence)

    def todo_to_doing(self, i, s):
        print('todo_to_doing {} {}'.format(i,s))
        self.todo_scroll.remove_line(i)
        self.doing_scroll.add_line(0, s)

    def doing_to_todo(self, i, s):
        print('doing_to_todo {} {}'.format(i,s))
        self.doing_scroll.remove_line(i)
        self.todo_scroll.add_line(0, s)

    def doing_to_done(self, i, s):
        print('doing_to_done {} {}'.format(i,s))
        self.doing_scroll.remove_line(i)
        self.done_scroll.add_line(0, s)

    def done_to_doing(self, i, s):
        print('done_to_doing {} {}'.format(i,s))
        self.done_scroll.remove_line(i)
        self.doing_scroll.add_line(i, s)

    def update_done_sentence_list(self):
        try:
            sentence = self.done_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.done_scroll.add_line(END, sentence.text)
        self.after(250, lambda: self.update_done_sentence_list())

    def update_doing_sentence_list(self):
        try:
            sentence = self.doing_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.doing_scroll.add_line(END, sentence.text)
        self.after(250, lambda: self.update_doing_sentence_list())

    def update_todo_sentence_list(self):
        try:
            sentence = self.todo_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.todo_scroll.add_line(END, sentence.text)
        self.after(250, lambda: self.update_todo_sentence_list())        
        
if __name__ == '__main__':
    options = {'todo':{'title': 'Anotar', 'data':['sent1', 'sent2']},
               'doing':{'title': 'Anotando', 'data':[]},
               'done': {'title': 'Anotado', 'data':['sent0'] }}
    SentencesPanel(options).mainloop()
