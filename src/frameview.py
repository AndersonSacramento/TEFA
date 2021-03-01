from scrolledtext import ScrolledText
from tkinter import *
import fnutils


class FrameView(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        self.fn_frame = options['frame']
        self.frame_sentences = []
        self.options = options
        self.make_widgets()


    def make_widgets(self):
        self.scroll_text = ScrolledText(self, text=str(self.fn_frame))
        self.scroll_text.get_text_widget().bind("<KeyPress>", self.on_keyboard)
        self.scroll_text.get_text_widget().bind('<Control-Key-h>', self.key_bind_help)


    def key_bind_help(self, event):
        text = """
        Pressione a : Visualizar resumo de informações do frame\n\n
        Pressione d : Visualizar definição do frame\n\n
        Pressione s : Visualizar exemplos de sentenças do frame\n\n
        Pressione e : Visualizar todos os elementos do frame\n\n
        Pressione c : Visualizar todos os elementos core do frame\n\n
        Pressione p : Visualizar todos os elementos peripheral do frame\n\n
        Pressione q : Fechar janela de visualização do frame\n\n
        Pressione Ctrl-h : Visualizar lista de teclas e funções\n\n
        """
        self.scroll_text.settext(text)
        
        

    def on_keyboard(self, event):
        pressed = event.char
        if pressed == 'a':
            self.print_all_frame_info()
        elif pressed == 'd':
            self.print_frame_definition()
        elif pressed == 's':
            if not self.frame_sentences:
                self.frame_sentences = fnutils.get_all_frame_sentences(self.fn_frame)
                self.sentence_index = 0
            self.print_next_frame_sentence()
        elif pressed == 'q':
            Frame.destroy(self.parent)
        elif pressed == 'e':
            self.print_all_fes()
        elif pressed == 'c':
            self.print_core_fes()
        elif pressed == 'p':
            self.print_peripheral_fes()
        
        return 'break'


    def print_all_frame_info(self):
        self.scroll_text.settext(str(self.fn_frame))

    def print_frame_definition(self):
        self.scroll_text.settext(str(self.fn_frame.definition))

    def print_next_frame_sentence(self):
        if self.frame_sentences:
            if self.sentence_index >= len(self.frame_sentences):
                self.sentence_index = 0
            self.scroll_text.settext(str(self.frame_sentences[self.sentence_index]))
            self.sentence_index += 1
        

    def print_fe(self, fe):
        return '[name] %s \n [definition]\n\t%s\n\n' % (fe.name, fe.definition)


    def _get_all_fes(self):
        return self.fn_frame.FE.values()

    def _get_core_fes(self):
        fes = []
        for fe in self._get_all_fes():
            if fe.coreType == 'Core':
                fes.append(fe)
        return fes

    def _get_peripheral_fes(self):
        fes = []
        for fe in self._get_all_fes():
            if fe.coreType == 'Peripheral':
                fes.append(fe)
        return fes
                
    def print_all_fes(self):
        text = '[All]\n\n'
        for fe in self._get_all_fes():
            text += self.print_fe(fe)

        self.scroll_text.settext(text)

    def print_core_fes(self):
        text = '[Core]\n\n'
        for fe in self._get_core_fes():
            text += self.print_fe(fe)

        self.scroll_text.settext(text)


    def print_peripheral_fes(self):
        text = '[Peripheral]\n\n'
        for fe in self._get_peripheral_fes():
            text += self.print_fe(fe)

        self.scroll_text.settext(text)
        
