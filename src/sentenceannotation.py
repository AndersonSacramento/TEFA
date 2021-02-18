from scrolledlist import ScrolledList
from scrolledtext import ScrolledText
from feselection import FESelection
from frameselection import FrameSelection
from tkinter import *
from tkinter import ttk
import _thread, queue, time
import fnutils
from db import ArgANN


class SentenceAnnotation(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.make_widgets(options)
        self.options = options
        self.sentence_queue = queue.Queue()
        self.cur_event_ann = None
        self.load_content(options)


    def make_widgets(self, options):
        left_frame = Frame(self)
        text = Text(left_frame)
        text.config(font=('courier', 15, 'normal'))
        text.config(width=20, height=12)
        text.pack(side=TOP, expand=YES, fill=BOTH)
        
        self.sentence_text_view = text

        self.fe_selection = FESelection(options, parent=left_frame)
        self.fe_selection.pack(side=TOP, anchor=SW)
        left_frame.pack(side=LEFT, expand=YES, fill=BOTH)

        right_frame = Frame(self)
        self.frame_selection = FrameSelection(options, parent=right_frame)
        self.frame_selection.pack(side=TOP, anchor=NE)
        self.frame_selection.set_event_ann_type_selection_handler(self.event_type_selection_handler)

        btn_frame = Frame(right_frame)

        btn_tag = Button(btn_frame, text='Anotar', command=self.annotate_arg)
        btn_tag.pack(side=LEFT)
        
        btn_save = Button(btn_frame, text='Salvar', command=self.save_annotation)
        btn_save.pack(side=RIGHT, anchor=SE)

        btn_preview = Button(btn_frame, text='Pré-visualizar', command=self.preview_annotation)
        btn_preview.pack(side=LEFT, anchor=SE)
        btn_frame.pack(side=TOP)
        right_frame.pack(side=RIGHT, expand=YES, fill=BOTH)

        
        

    def load_content(self, options):
        _thread.start_new_thread(self.load_sentence, (options['sentence_id'], options['annotator_id']))
        self.sentence = None
        self.update_sentence_text()
        

    def load_sentence(self, sentence_id, annotator_id):
        self.events_ann = []
        sentence = fnutils.query_sentence_by(sentence_id)
        if sentence:
            events_ann = fnutils.query_events_ann(annotator_id, [e.id for e in sentence.events])
            if events_ann:
                self.events_ann = events_ann
            self.sentence_queue.put(sentence)
            

    def save_annotation(self):
        pass

    def preview_annotation(self):
        pass

    def _find_arg_ann(self, args_ann, fe_id):
        for arg_ann in args_ann:
            if arg_ann.event_fe_id == fe_id:
                return arg_ann
            
    def annotate_arg(self):
        text = self.sentence_text_view.get(SEL_FIRST, SEL_LAST)
        if text:
            start_at = self.sentence_text_view.index(SEL_FIRST).split('.')[1]
            end_at = self.sentence_text_view.index(SEL_LAST).split('.')[1]
            output = self.fe_selection.get_radio_fe_and_color()
            if output:
                fe, fe_color = output
            if self.cur_event_ann:
                tag_name = '%s-%s' % (fe.ID, self.cur_event_ann.id)
                self.sentence_text_view.tag_remove(tag_name,'1.0', END)
                self.sentence_text_view.tag_add(tag_name, '1.%s' % start_at, '1.%s' % end_at)
                self.sentence_text_view.tag_config(tag_name, background=fe_color)
                arg_ann = self._find_arg_ann(self.cur_event_ann.args_ann, fe.ID)
                if arg_ann:
                    arg_ann.start_at =  start_at
                    arg_ann.end_at = end_at
                    arg_ann.updated_at = fnutils.now()
                    print('update arg_ann')
                else:
                    self.cur_event_ann.args_ann.append(ArgANN(start_at=start_at,
                                                     end_at=end_at,
                                                     created_at=fnutils.now(),
                                                     event_fe_id=fe.ID,
                                                     event_ann_id=self.cur_event_ann.id,
                                                              annotator_id=options['annotator_id']))
                    print('create arg_ann')
                                                     
            
        sel_first_pos = SEL + '.first'
        sel_last_pos = SEL + '.last'
        print('annotate arg %s \n %s %s %s' % (text, str(self.sentence_text_view.index(sel_first_pos)), str(self.sentence_text_view.index(sel_last_pos)), str(len(self.sentence_text_view.get('0.0', END)))))


    def event_type_selection_handler(self, event_ann, frame):
        if self.cur_event_ann:
            for arg_ann in self.cur_event_ann.args_ann:
                tag_name = '%s-%s' % (arg_ann.event_fe_id, self.cur_event_ann.id)
                self.sentence_text_view.tag_delete(tag_name,'1.0', END)
            
        if event_ann and frame:
            print('Frame name: %s \n event_id: %s \n event_args %s' % (frame.name, event_ann.event_id, event_ann.args_ann))
            self.cur_event_ann = event_ann
            self.fe_selection.set_args_ann(event_ann.args_ann)
            self.fe_selection.set_fes(fnutils.filter_core_fe(frame))
        else:
            self.fe_selection.clear_args_rows()
            
        
    def update_sentence_text(self):
        try:
            self.sentence = self.sentence_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.sentence_text_view.delete('1.0', END)
            self.sentence_text_view.insert('1.0', self.sentence.text)
            print([e.trigger for e in self.sentence.events])
            self.frame_selection.set_events(self.sentence.events)
            self.frame_selection.set_events_ann(self.events_ann)
        self.after(10, lambda: self.update_sentence_text())

if __name__ == '__main__':
    options = {'annotator_id': 'anderson@gmail.com',
               'sentence_id': '6c8c7963-eaae-48bb-9e6e-b75828078e95',
               'triggers': ['falar', 'transferir'],
               'suggestion': {'title': 'Sugestões'},
               'all':{'title': 'Todos' },
               'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': ['Local', 'Tempo', 'Atacante']}
    fnutils.create_session()
    SentenceAnnotation(options).mainloop()
