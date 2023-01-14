from scrolledlist import ScrolledList
from sentenceannotation import SentenceAnnotation
from guiutils import show_text_dialog
from tkinter import *
from tkinter import filedialog as fd
import _thread, queue, time
import fnutils
from copy import copy



class SentenceViewObj():

    def __init__(self, id, text):
        self.id = id
        self.text = text

        
class SentencesPanel(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.makeWidgets(options)
        self.options = options
        self.focus_list = None
        self.todo_queue = queue.Queue()
        self.doing_queue = queue.Queue()
        self.done_queue = queue.Queue()
        self.load_content()


    def makeWidgets(self, options):
        #self.config(takefocus=0)
        self.todo_scroll = ScrolledList(options['todo'], parent=self)
        self.todo_scroll.config_listbox(bg='tomato')
        Button(self.todo_scroll, text='Adicionar', command=self.handler_file_dialog).pack(side=TOP)
        self.doing_scroll = ScrolledList(options['doing'], parent=self)
        self.doing_scroll.config_listbox(bg='aquamarine')
        self.done_scroll = ScrolledList(options['done'], parent=self)
        self.done_scroll.config_listbox(bg='SteelBlue1')

        self.todo_scroll.pack(side=LEFT, expand=YES, fill=BOTH)
        self.doing_scroll.pack(side=LEFT, expand=YES, fill=BOTH)
        self.done_scroll.pack(side=LEFT, expand=YES, fill=BOTH)

        todo_scroll_right = lambda i,s: self.todo_to_doing(i[0],s)
        self.todo_scroll.set_right_mouse_handle(todo_scroll_right)
        self.todo_scroll.set_right_arrow_handler(todo_scroll_right)
        

        doing_scroll_left = lambda i,s: self.doing_to_todo(i[0],s)
        self.doing_scroll.set_left_mouse_handle(doing_scroll_left)
        self.doing_scroll.set_left_arrow_handler(doing_scroll_left)

        doing_scroll_right = lambda i,s: self.doing_to_done(i[0],s)
        self.doing_scroll.set_right_mouse_handle(doing_scroll_right)
        self.doing_scroll.set_right_arrow_handler(doing_scroll_right)
        
        
        doing_scroll_ann = lambda i, s: self.annotate_sentence(i[0], s)
        self.doing_scroll.set_double_1_handler(doing_scroll_ann)
        self.doing_scroll.set_a_key_handler(doing_scroll_ann)

        done_scroll_left = lambda i,s: self.done_to_doing(i[0],s)
        self.done_scroll.set_left_mouse_handle(done_scroll_left)
        self.done_scroll.set_left_arrow_handler(done_scroll_left)


        # Move between lists
        todo_focus_lambda = lambda i, s: self.set_current_focus_list(self.todo_scroll)
        doing_focus_lambda = lambda i, s: self.set_current_focus_list(self.doing_scroll)
        done_focus_lambda = lambda i, s: self.set_current_focus_list(self.done_scroll)
        
        self.doing_scroll.set_ctrl_1_handler(todo_focus_lambda)
        self.doing_scroll.set_1_handler(todo_focus_lambda)
        self.done_scroll.set_ctrl_1_handler(todo_focus_lambda)
        self.done_scroll.set_1_handler(todo_focus_lambda)
        
        self.todo_scroll.set_ctrl_2_handler(doing_focus_lambda)
        self.todo_scroll.set_2_handler(doing_focus_lambda)
        self.done_scroll.set_ctrl_2_handler(doing_focus_lambda)
        self.done_scroll.set_2_handler(doing_focus_lambda)

        self.todo_scroll.set_ctrl_3_handler(done_focus_lambda)
        self.todo_scroll.set_3_handler(done_focus_lambda)
        self.doing_scroll.set_ctrl_3_handler(done_focus_lambda)
        self.doing_scroll.set_3_handler(done_focus_lambda)

        #
        self.parent.bind_all('<KeyPress>', self.on_keyboard)

    def handler_file_dialog(self):
        filename = fd.askopenfilename()
        print(f'File name: {filename}')
        fnutils.load_sentences_from(filename)
        fnutils.update_sentences_annotator(self.options['email'])
        _thread.start_new_thread(self.load_sentences, ('todo',))
        self.update_todo_sentence_list()
        
    def set_current_focus_list(self, scroll_list):
        self.focus_list = scroll_list
        scroll_list.get_list_focus()
        
    def _is_ctrl_key(self, event):
        return event.state & 0x0004 or event.keysym == 'Control_L' or event.keysym == 'Control_R'


    def select_next_in_focus_list(self):
        if self.focus_list:
            self.focus_list.select_next()
        else:
            self.set_current_focus_list(self.doing_scroll)

    def select_previous_in_focus_list(self):
        if self.focus_list:
            self.focus_list.select_previous()


    def show_helper_dialog(self):
        help_msg = """
        1 : ir para lista anotar
        2 : ir para lista anotando
        3 : ir para lista anotada(s)
        n : selecionar próxima sentença da lista
        p : selecionar sentença anterior da lista
        a : abrir janela de anotação para sentença seleciona - deve estar na lista anotando
        seta-esquerda : mover sentença selecionada para lista à esquerda
        seta-diretira : mover sentença selecionada para lista à direita
        h : visualizar lista de teclas de atalho
        """
        show_text_dialog(self, 'Ajuda - painel de seleção de sentenças', help_msg, font=('times', 14))

            
    def on_keyboard(self, event):
        pressed = event.keysym

        if self._is_ctrl_key(event):
            if pressed == 'n':
                self.select_next_in_focus_list()
            elif pressed == 'p':
                self.select_previous_in_focus_list()
        elif pressed == 'n':
            self.select_next_in_focus_list()
        elif pressed == 'p':
            self.select_previous_in_focus_list()
        elif pressed == 'h':
            self.show_helper_dialog()
        elif pressed == 'Down':
            self.select_next_in_focus_list()
        elif pressed == 'Up':
            self.select_previous_in_focus_list()
            
        
    def load_content(self):
        self.set_email(self.options['email'])

        self.todo_sentences = []
        self.doing_sentences = []
        self.done_sentences = []
        
        _thread.start_new_thread(self.load_sentences, ('todo',))
        _thread.start_new_thread(self.load_sentences, ('doing',))
        _thread.start_new_thread(self.load_sentences, ('done',))

        self.update_todo_sentence_list()
        self.update_doing_sentence_list()
        self.update_done_sentence_list()

    def set_email(self, email):
        self.email = email
        
    def load_sentences(self, status):
        status_queue = {'todo': (self.todo_queue, self.todo_sentences) ,
                        'doing': (self.doing_queue, self.doing_sentences),
                        'done': (self.done_queue, self.done_sentences)}
        # load sentence from annotator lome
        for sentence in fnutils.load_sentences(self.email, status):
            queue, sentences_list  = status_queue[status]
            
            queue.put(copy(sentence))#SentenceViewObj(sentence.id, sentence.text))
            sentences_list.append(copy(sentence))

    def annotate_sentence(self, i, s):
        if self.doing_sentences:
            sentence = self.doing_sentences[i]
            win = Toplevel()
            self.options['annotator_id'] = self.email
            self.options['sentence_id'] =  sentence.id
            SentenceAnnotation(self.options, parent=win)
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            win.geometry("%dx%d+0+0" % (w, h))
            win.focus_set()
            #win.grab_set()
            win.wait_window()

    
    def todo_to_doing(self, i, s):
        print('todo_to_doing {} {}'.format(i,s))
        self.todo_scroll.remove_line(i)
        sentence = self.todo_sentences[i]
        self.doing_sentences.insert(0, sentence)
        self.todo_sentences.remove(sentence)
        self.doing_scroll.add_line(0, s)
        _thread.start_new_thread(self.change_sentence_status, (sentence, 'doing'))

    def doing_to_todo(self, i, s):
        print('doing_to_todo {} {}'.format(i,s))
        self.doing_scroll.remove_line(i)
        sentence = self.doing_sentences[i]
        self.todo_sentences.insert(0, sentence)
        self.doing_sentences.remove(sentence)
        self.todo_scroll.add_line(0, s)
        _thread.start_new_thread(self.change_sentence_status, (sentence, 'todo'))

    def doing_to_done(self, i, s):
        print('doing_to_done {} {}'.format(i,s))
        self.doing_scroll.remove_line(i)
        sentence = self.doing_sentences[i]
        self.done_sentences.insert(0, sentence)
        self.doing_sentences.remove(sentence)
        self.done_scroll.add_line(0, s)
        _thread.start_new_thread(self.change_sentence_status, (sentence, 'done'))

    def done_to_doing(self, i, s):
        print('done_to_doing {} {}'.format(i,s))
        self.done_scroll.remove_line(i)
        sentence = self.done_sentences[i]
        self.doing_sentences.insert(0, sentence)
        self.done_sentences.remove(sentence)
        self.doing_scroll.add_line(i, s)
        _thread.start_new_thread(self.change_sentence_status, (sentence, 'doing'))

    def change_sentence_status(self, sentence, status):
        fnutils.change_sentence_status(sentence, self.email, status)

    def update_done_sentence_list(self):
        try:
            sentence = self.done_queue.get(block=False)
        except queue.Empty:
            self.done_scroll.print_list_size()
        else:
            self.done_scroll.add_line(END, sentence.text)
        self.after(50, lambda: self.update_done_sentence_list())

    def update_doing_sentence_list(self):
        try:
            sentence = self.doing_queue.get(block=False)
        except queue.Empty:
            self.doing_scroll.print_list_size()
        else:
            self.doing_scroll.add_line(END, sentence.text)
        self.after(50, lambda: self.update_doing_sentence_list())

    def update_todo_sentence_list(self):
        try:
            sentence = self.todo_queue.get(block=False)
        except queue.Empty:
            self.todo_scroll.print_list_size()
        else:
            self.todo_scroll.add_line(END, sentence.text)
        self.after(50, lambda: self.update_todo_sentence_list())        
        
if __name__ == '__main__':
    options = {'todo':{'title': 'Anotar', 'data':['sent1', 'sent2']},
               'doing':{'title': 'Anotando', 'data':[]},
               'done': {'title': 'Anotado', 'data':['sent0'] }}
    SentencesPanel(options).mainloop()
