from scrolledlist import ScrolledList
from scrolledtext import ScrolledText
from feselection import FESelection
from frameselection import FrameSelection
from tkinter import *
from tkinter import ttk
import _thread, queue, time
import fnutils
from frameview import FrameView
from db import ArgANN
from copy import copy

class SentenceAnnotation(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.options = options
        self.options['suggestion'] = {'title': 'Sugestões'}
        self.options['all'] = {'title': 'Todos' }
        self.sentence_queue = queue.Queue()
        self.events_queue = queue.Queue()
        self.vals_queue = queue.Queue()
        self.cur_event_ann = None
        self.make_widgets(self.options)
        self.load_content(self.options)
        self.load_default_modes()

    def load_default_modes(self):
        self.set_search_mode(False)


    def middle_button_in_text(self):
        self.sentence_text_view.edit_undo()
        
    def make_widgets(self, options):
        left_frame = Frame(self)
        text = Text(left_frame)
        text.config(font=('courier', 15, 'normal'))
        text.config(width=20, height=12)
        text.pack(side=TOP, expand=YES, fill=BOTH)
        text.bind('<KeyPress>', lambda e: self.on_keyboard(e))
        #text.bind('<Key>', lambda e: 'break')
        #text.bind('<Button-2>', lambda e: self.middle_button_in_text)

        self.sentence_text_view = text


        ann_frame = Frame(left_frame)
        self.fe_arg_var = StringVar()
        label_fe =  Label(ann_frame, text='', textvariable=self.fe_arg_var)
        label_fe.pack(side=LEFT, expand=YES)
        self.label_fe = label_fe


        txt_fe_def = Text(ann_frame, font=('times', 12), height=2, width=50)
        txt_fe_def.pack(side=LEFT, expand=YES)
        txt_fe_def.bind('<KeyPress>', lambda e: self.on_keyboard(e))
        #txt_fe_def.bind('<Key>', lambda e: 'break')
        self.txt_fe_def = txt_fe_def


        btn_tag = Button(ann_frame, text='Anotar', command=self.annotate_arg)
        btn_tag.pack(side=RIGHT, expand=YES)
        ann_frame.pack(side=TOP, expand=YES, fill=X)
        

        self.fe_selection = FESelection(options, parent=left_frame)
        self.fe_selection.pack(side=TOP, anchor=SW)
        self.fe_selection.set_arg_ann_remove_handler(self.arg_ann_remove_handler)
        self.fe_selection.set_on_fe_selection_handler(self.set_fe_arg_label)
        left_frame.pack(side=LEFT, expand=YES, fill=BOTH)
        #self.fe_selection.set_arg_val_handler(self.arg_val_handler)
        

        right_frame = Frame(self)
        self.frame_selection = FrameSelection(options, parent=right_frame)
        self.frame_selection.pack(side=TOP, anchor=NE)
        self.frame_selection.set_event_ann_type_selection_handler(self.event_type_selection_handler)
        self.frame_selection.set_event_ann_type_remove_handler(self.event_ann_type_remove_handler)
        #self.frame_selection.set_event_val_handler(self.event_val_handler)
        

        # btn_frame = Frame(right_frame)

         
        
        # btn_save = Button(btn_frame, text='Salvar', command=self.save_annotation)
        # btn_save.pack(side=RIGHT, anchor=SE)

        # btn_preview = Button(btn_frame, text='Pré-visualizar', command=self.preview_annotation)
        # btn_preview.pack(side=LEFT, anchor=SE)
        # btn_frame.pack(side=TOP)
        right_frame.pack(side=RIGHT, expand=YES, fill=BOTH)
        self.parent.bind('<KeyPress>', self.on_keyboard)


        
    def load_view_frame_info(self):
        if self.cur_event_ann:
            frame = fnutils.frame_by_id(self.cur_event_ann.event_fn_id)
            if frame:
                win = Toplevel()
                frame_view = FrameView({'frame':frame}, win)
                win.focus_set()
                win.grab_set()
                win.wait_window()

        
    def load_content(self, options):
        _thread.start_new_thread(self.load_sentence, (options['sentence_id'], options['annotator_id']))
        self.sentence = None
        self.update_sentence_text()
        #self.update_val_ann()
        

    def load_sentence(self, sentence_id, annotator_id):
        self.events_ann = []
        sentence = fnutils.query_sentence_by(sentence_id)
        if sentence:
            events = fnutils.query_events_sentence(sentence)
            # from lome annotator
            events_ann = fnutils.query_events_ann(annotator_id, [e.id for e in events])
            if events_ann:
                self.events_ann = events_ann
                print('events ann recovered annotator_id: %s' % annotator_id)
            self.sentence_queue.put(sentence)
            self.events_queue.put(events)
            

    def save_annotation(self):
        # for event_ann in self.events_ann:
        #     event_ann.annotator_id = self.options['annotator_id']
        #     for arg_ann in event_ann.args_ann:
        #         arg_ann.annotator_id = self.options['annotator_id']
        #     fnutils.save_event_ann(event_ann)

        Frame.destroy(self.parent)

    def preview_annotation(self):
        pass

    def _find_arg_ann(self, args_ann, fe_id, start_at, end_at):
        for arg_ann in args_ann:
            if arg_ann.event_fe_id == fe_id and ((arg_ann.start_at <= start_at < end_at <= arg_ann.end_at) or (start_at <= arg_ann.start_at < arg_ann.end_at <= end_at)):

                return arg_ann
            

    def _is_alt_key(self, event):
        return event.state & 0x0008 or event.state & 0x0080

    def _is_ctrl_key(self, event):
        return event.state & 0x0004 or event.keysym == 'Control_L' or event.keysym == 'Control_R'

    def set_search_mode(self, value):
        self.search_mode = value
        self.search_str = ''

    def increment_search_str(self, char):
        self.search_str += char
        print('search string: %s' % self.search_str)
        self.frame_selection.search_frame(self.search_str)

    def is_search_mode(self):
        return self.search_mode
    
    def on_keyboard(self, event):
        pressed = event.keysym
     
        #self.bind_all('<Control-Key-f>', lambda e: Frame.destroy(self.parent))
        if self.is_search_mode():
            if self._is_ctrl_key(event):
                if  pressed == 'g':
                    print('cancel search mode')
                    self.set_search_mode(False)
                    self.frame_selection.clear_search_frame()
                elif pressed == 'n':
                    self.frame_selection.select_next_frame_all_list()
                elif pressed == 'p':
                    self.frame_selection.select_previous_frame_all_list()
                elif pressed == 'i':
                    self.frame_selection.view_info_current_frame()
            elif  pressed == 'Return':
                self.frame_selection.select_event_type()
            else:
                if pressed == 'underscore':
                    pressed = '_'
                self.increment_search_str(pressed)
        elif self._is_alt_key(event):
            if pressed == 'c':
                self.fe_selection.cycle_selection_core_fe()
            elif pressed == 'p':
                self.fe_selection.cycle_selection_peripheral_fe()
            elif pressed == 'a':
                self.fe_selection.cycle_selection_ann_fe()
        elif self._is_ctrl_key(event):
            print('contrl key pressed: %s' % pressed)
            if pressed == 's':
                self.set_search_mode(True)
                print('enter search mode')
            elif pressed == 'g':
                print('cancel search mode')
                self.set_search_mode(False)
                
        else:
            if pressed == 'a':
                self.annotate_arg()
            elif pressed == 'i':
                self.load_view_frame_info()
            elif pressed == 'q':
                Frame.destroy(self.parent)
            elif pressed == 't':
                self.frame_selection.cycle_combobox_trigger()

        return "break"

    def set_fe_arg_label(self):
        print('set_fe_arg_label')
        output = self.fe_selection.get_radio_fe_and_color()
        if output:
            fe, fe_color = output
            self.fe_arg_var.set(fe.name)
            self.txt_fe_def.delete('1.0', END)
            self.txt_fe_def.insert('1.0', fe.definition)
            self.label_fe.config(background=fe_color)
        else:
            self.fe_arg_var.set('')
            bg = self.cget("background")
            self.label_fe.config(background=bg)
            self.txt_fe_def.delete('1.0', END)
            self.txt_fe_def.insert('1.0', '')
        
    def annotate_arg(self):
        try:
            text = self.sentence_text_view.get(SEL_FIRST, SEL_LAST)
        except Exception:
            text = ''
        if text and self.fe_selection.is_selected():
            start_at = self.sentence_text_view.index(SEL_FIRST).split('.')[1]
            end_at = self.sentence_text_view.index(SEL_LAST).split('.')[1]
            output = self.fe_selection.get_radio_fe_and_color()
            if output:
                fe, fe_color = output
            if self.cur_event_ann:

                arg_ann = self._find_arg_ann(self.cur_event_ann.args_ann, fe.ID, int(start_at), int(end_at))
                if arg_ann:
                    tag_name = '%s-%s-%s:%s' % (fe.ID, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
                    self.sentence_text_view.tag_remove(tag_name,'1.0', END)
                    previous_arg = arg_ann.copy()
                    arg_ann.start_at =  int(start_at)
                    arg_ann.end_at = int(end_at)
                    arg_ann.updated_at = fnutils.now()
                    fnutils.save_arg_ann(arg_ann)
                    fnutils.delete_arg_ann(previous_arg)

                    print('update arg_ann start_at %s end_at %s' % (arg_ann.start_at, arg_ann.end_at))
                else:
                    arg_ann = ArgANN(start_at=int(start_at),
                                     end_at=int(end_at),
                                     created_at=fnutils.now(),
                                     event_fe_id=fe.ID,
                                     event_ann_id=self.cur_event_ann.id,
                                     annotator_id=self.options['annotator_id'])
                    fnutils.save_arg_ann(arg_ann)
                    self.cur_event_ann.args_ann.append(arg_ann)
                    print('create arg_ann')
                tag_name = '%s-%s-%s:%s' % (fe.ID, self.cur_event_ann.id, start_at, end_at)
                self.sentence_text_view.tag_remove(tag_name,'1.0', END)
                self.sentence_text_view.tag_add(tag_name, '1.%s' % start_at, '1.%s' % end_at)
                self.sentence_text_view.tag_config(tag_name, background=fe_color)
                    
                self._update_fes_selections(self.cur_event_ann)
                                                     
            
        #sel_first_pos = SEL + '.first'
        #sel_last_pos = SEL + '.last'
        #print('annotate arg %s \n %s %s %s' % (text, str(self.sentence_text_view.index(sel_first_pos)), str(self.sentence_text_view.index(sel_last_pos)), str(len(self.sentence_text_view.get('0.0', END)))))


    def load_event_ann_tags(self):
        if self.cur_event_ann:
            for arg_ann in self.cur_event_ann.args_ann:
                tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
                self.sentence_text_view.tag_remove(tag_name,'1.0', END)
                self.sentence_text_view.tag_add(tag_name, '1.%s' % arg_ann.start_at, '1.%s' % arg_ann.end_at)
                print('even_ann_id = %s event_fe_id %s' % (arg_ann.event_ann_id, arg_ann.event_fe_id))
                fe_color = self.fe_selection.get_fe_color(arg_ann.event_fe_id)
                self.sentence_text_view.tag_config(tag_name, background=fe_color)
        

    def highlight_event(self, event):
        if event:
            self.sentence_text_view.tag_delete('trigger', '1.0', END)
            self.sentence_text_view.tag_add('trigger','1.%s' % event.start_at, '1.%s' % event.end_at)
            self.sentence_text_view.tag_config('trigger', font=('times', 16, 'bold'))
    
    def event_val_handler(self, val_event_ann):
        if self.cur_event_ann:
            val_event_ann.event_ann_id = self.cur_event_ann.id
            val_event_ann.annotator_id = self.options['annotator_id']
            _thread.start_new_thread(fnutils.save_val_event, (val_event_ann,))


    def arg_val_handler(self, val_arg_ann):
        if self.cur_event_ann:
            val_arg_ann.event_ann_id = self.cur_event_ann.id
            val_arg_ann.annotator_id = self.options['annotator_id']
            _thread.start_new_thread(fnutils.save_val_arg, (val_arg_ann,))


    

    def event_type_selection_handler(self, event, event_ann, frame):
        if self.cur_event_ann:
            for arg_ann in self.cur_event_ann.args_ann:
                tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
                self.sentence_text_view.tag_delete(tag_name,'1.0', END)
                print('delete tag')
            #if event_ann and self.cur_event_ann.event_fn_id != event_ann.event_fn_id:
            #    event_ann.args_ann = []
            #    print('set empty list')

        self.cur_event_ann = event_ann
        if event_ann and frame:
            print('Frame name: %s \n event_id: %s \n event_args %s' % (frame.name, event_ann.event_id, event_ann.args_ann))
            #self.fe_selection.set_args_ann(event_ann.args_ann)
            self.fe_selection.update_fes()
            self.fe_selection.set_args_ann_fes(fnutils.get_fes_from_args(event_ann, event_ann.args_ann), event_ann.args_ann , self.sentence.text)#get_args_ann_fes(event_ann.id, self.options['annotator_id']))
            self.fe_selection.set_core_fes(fnutils.filter_core_fes(frame))
            self.fe_selection.set_peripheral_fes(fnutils.filter_peripheral_fes(frame))
            #_thread.start_new_thread(self.load_val_ann, (self.options['annotator_id'], event_ann.id)) 
        else:
            self.fe_selection.update_fes()
        self.highlight_event(event)
        self.load_event_ann_tags()
        self.set_fe_arg_label()
        _thread.start_new_thread(self.save_events_ann, ())


    def save_events_ann(self):
        for event_ann in self.events_ann:
            event_ann.annotator_id = self.options['annotator_id']
            for arg_ann in event_ann.args_ann:
                arg_ann.annotator_id = self.options['annotator_id']
            fnutils.save_event_ann(event_ann)

    def event_ann_type_remove_handler(self, event_ann):
        self.fe_selection.update_fes()
        if self.cur_event_ann:
            for arg_ann in self.cur_event_ann.args_ann:
                tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
                self.sentence_text_view.tag_delete(tag_name,'1.0', END)
                print('delete tag')
        self.cur_event_ann = None

    def arg_ann_remove_handler(self, arg_ann):
        if self.cur_event_ann:
            tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
            self.sentence_text_view.tag_delete(tag_name,'1.0', END)
            self.cur_event_ann.args_ann.remove(arg_ann)
            fnutils.delete_arg_ann(arg_ann)
            self._update_fes_selections(self.cur_event_ann)
        
    def _update_fes_selections(self, event_ann):
        frame = fnutils.frame_by_id(event_ann.event_fn_id)
        if event_ann and frame:
            print('update_fes_selection frame id: %s' % frame.ID)
            self.fe_selection.update_selections()
            
            self.fe_selection.set_args_ann_fes(fnutils.get_fes_from_args(event_ann, event_ann.args_ann), event_ann.args_ann, self.sentence.text)
            self.fe_selection.set_core_fes(fnutils.filter_core_fes(frame))
            self.fe_selection.set_peripheral_fes(fnutils.filter_peripheral_fes(frame))

        
    def update_sentence_text(self):
        try:
            self.sentence = self.sentence_queue.get(block=False)
            events = self.events_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.sentence_text_view.delete('1.0', END)
            self.sentence_text_view.insert('1.0', self.sentence.text)
            print([e.trigger for e in events])
            self.frame_selection.set_events(events)
            self.frame_selection.set_events_ann(self.events_ann)
        self.after(10, self.update_sentence_text)


    def load_val_ann(self, annotator_id, event_ann_id):
        val_event = fnutils.query_val_event(event_ann_id, annotator_id)
        val_args = fnutils.query_val_args(event_ann_id, annotator_id)
        self.vals_queue.put((val_event, val_args))
        
        
    def update_val_ann(self):
        try:
            val_event, vals_args = self.vals_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.frame_selection.set_val_event(val_event)
            self.fe_selection.set_val_args(vals_args)
        self.after(10, self.update_val_ann)
            

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
