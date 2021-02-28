from scrolledlist import ScrolledList
from scrolledtext import ScrolledText
from tkinter import *
from tkinter import ttk
import _thread, queue, time
from db import EventANN
import fnutils



class FrameSelection(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.make_widgets(options)
        self.options = options
        self.suggestions_queue = queue.Queue()
        self.all_frames_queue = queue.Queue()
        self.events = []
        self.selected_frames = dict()
        self.event_ann_type_selection_handler = None
        self.event_val_handler = None
        self.load_content()

    
    def set_events(self, events):
        self.events = events
        self.triggers_combo.config(values=[e.trigger for e in events])


    # def set_val_event(self, val_event):
    #     print('set val event')
    #     if val_event:
    #         if val_event.is_wrong():
    #             print('val wrong')
    #             self.ans_type_event.set('Errado')
    #         else:
    #             print('val right')
    #             self.ans_type_event.set('Certo')
    
    def set_events_ann(self, events_ann):
        self.events_ann = events_ann

    def set_event_ann_type_selection_handler(self, func):
        self.event_ann_type_selection_handler = func
        
    def make_widgets(self, options):
        #vlist = options['triggers']
        self.trigger_var = StringVar()
        self.trigger_var.set("Selecione um gatilho")
        self.triggers_combo = ttk.Combobox(self)#
        self.triggers_combo.config(textvariable=self.trigger_var)
        self.triggers_combo.pack(side=TOP)
        #self.triggers_combo.current(0)
        self.triggers_combo.bind("<<ComboboxSelected>>", self.trigger_change_handler)

        self.var_event_type = StringVar()
        self.var_event_type.set('Tipo:')
        label = Label(self)
        label.pack(side=TOP, anchor=W)
        label.config(textvariable=self.var_event_type)

        # row_val = Frame(self)
        # lab_type_qs = Label(row_val)
        # lab_type_qs.config(text='Tipo está: ')
        # lab_type_qs.pack(side=LEFT)

        # self.ans_type_event = StringVar()

        # rad_type_wrong = Radiobutton(row_val, text='Errado', value='Errado', variable=self.ans_type_event, command=(lambda : self.on_press_type_radio_event('wrong')))
        # rad_type_wrong.pack(side=LEFT)

        # rad_type_right = Radiobutton(row_val, text='Certo',  value='Certo', variable=self.ans_type_event, command=(lambda : self.on_press_type_radio_event('right')))
        # rad_type_right.pack(side=LEFT)
        

        # row_val.pack(side=TOP, expand=YES, fill=X)
        
            

        print('Options here %s' % options)
        self.suggestion_scroll = ScrolledList(options['suggestion'], parent=self)
        self.all_scroll = ScrolledList(options['all'], parent=self)
        
        
        self.suggestion_scroll.pack(side=TOP, expand=YES, fill=BOTH)
        self.all_scroll.pack(side=TOP, expand=YES, fill=BOTH)

    
        self.suggestion_scroll.set_middle_mouse_handle(lambda i, s: self.event_type_selection_suggestion(i[0], s))
        self.all_scroll.set_middle_mouse_handle(lambda i, s: self.event_type_selection_all(i[0], s))

        self.suggestion_scroll.set_double_1_handler(lambda i, s: self.event_view_frame_suggestion(i[0], s))
        self.all_scroll.set_double_1_handler(lambda i, s: self.event_view_frame_all(i[0], s))

    def load_content(self):
        _thread.start_new_thread(self.load_all_frames_list, ())
        self.all_frames = []
        self.update_suggestions_list()
        self.update_all_frames_list()
        self.trigger_change_handler(None)

    def _event_by_position(self, i):
        if self.events:
            return self.events[i]

    def create_or_update_event_ann(self, event_id, frame_id):
        if self.events_ann:
            event_ann = fnutils.find_event_ann(self.events_ann, event_id)
            #if event_ann:
            #    event_ann.event_fn_id = frame_id
            #else:
            if event_ann:
                self.events_ann.remove(event_ann)
                fnutils.delete_previous(event_ann, event_ann.args_ann)
            event_ann = EventANN(id=fnutils.str_uuid(),
                                     event_id=event_id,
                                     event_fn_id=frame_id,
                                     created_at=fnutils.now(),
                                     updated_at=fnutils.now())
            self.events_ann.append(event_ann)    
        else:
            event_ann = EventANN(id=fnutils.str_uuid(),
                                 event_id=event_id,
                                 event_fn_id=frame_id,
                                 created_at=fnutils.now(),
                                 updated_at=fnutils.now())
            self.events_ann.append(event_ann)
        return event_ann

    # def on_press_type_radio_event(self, ans):
    #     print('type ans %s' % ans)
    #     if self.event_val_handler:
    #         self.event_val_handler(ValEventANN(status_type=ans))
        

    def set_event_val_handler(self, func):
        self.event_val_handler = func

        
    def event_type_selection_suggestion(self, i, s):
        self.var_event_type.set('Tipo: %s' % s)
        event_pos = self.triggers_combo.current()
        event = self._event_by_position(event_pos)
        if self.suggestions_frames:
            frame = self.suggestions_frames[i]
            self.selected_frames[frame.ID] = frame
            event_ann = self.create_or_update_event_ann(event.id, frame.ID)
            if self.event_ann_type_selection_handler:
                self.event_ann_type_selection_handler(event_ann, frame)
        
        
    def event_type_selection_all(self, i, s):
        self.var_event_type.set('Tipo: %s' % s)
        event_pos = self.triggers_combo.current()
        event = self._event_by_position(event_pos)
        if self.all_frames:
            frame = self.all_frames[i]
            self.selected_frames[frame.ID] = frame
            event_ann = self.create_or_update_event_ann(event.id, frame.ID)
            if self.event_ann_type_selection_handler:
                self.event_ann_type_selection_handler(event_ann, frame)

    
    def event_view_frame_suggestion(self, i, s):
        print('frame suggestion position double-1 : %s ' % i)
        frame = self.suggestions_frames[i]
        if frame:
            self.load_view_frame_info(frame)

    def event_view_frame_all(self, i, s):
        frame = self.all_frames[i]
        if frame:
            self.load_view_frame_info(frame)
            
    def load_view_frame_info(self, frame):
        win = Toplevel()
        scroll_text = ScrolledText(win, text=str(frame))
        scroll_text.get_text_widget().bind("<Key>", lambda e: "break")
        win.focus_set()
        win.grab_set()
        win.wait_window()
        
    def trigger_change_handler(self, event):
        trigger = self.trigger_var.get()
        print(trigger)
        i = self.triggers_combo.current()
        
        if self.events and self.events_ann:
            print('frame selection events_ann')
            event_tbpt = self.events[i]
            event_ann = fnutils.find_event_ann(self.events_ann, event_tbpt.id)
            if event_ann:
                frame = self.selected_frames.get(event_ann.event_fn_id) or fnutils.frame_by_id(event_ann.event_fn_id)
                if frame:
                    self.var_event_type.set('Tipo: %s' % frame.name)
                    if self.event_ann_type_selection_handler:
                        self.event_ann_type_selection_handler(event_ann, frame)
            else:
                self.var_event_type.set('Tipo:')
                if self.event_ann_type_selection_handler:
                    self.event_ann_type_selection_handler(None, None)
        else:
            self.var_event_type.set('Tipo:')
            if self.event_ann_type_selection_handler:
                self.event_ann_type_selection_handler(None, None)
            
        self.suggestions_frames = []
        self.suggestion_scroll.clear_list()
        if self.events:
            trigger_lemma = self.events[i].lemma
            _thread.start_new_thread(self.load_frames_suggestions, (trigger_lemma,))

        
    def load_frames_suggestions(self, trigger_lemma):
        for frame_id in fnutils.query_frameid(trigger_lemma):
            frame = fnutils.frame_by_id(frame_id)
            if frame:
                self.suggestions_frames.append(frame)
        self.suggestions_queue.put(self.suggestions_frames)

    def load_all_frames_list(self):
        for frame in sorted(fnutils.all_event_frames(), key=lambda f: f.name):
            self.all_frames.append(frame)
        self.all_frames_queue.put(self.all_frames)

    def update_suggestions_list(self):
        try:
            frames = self.suggestions_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.suggestion_scroll.clear_list()
            for frame in frames:
                self.suggestion_scroll.add_line(END, frame.name)
        self.after(50, lambda: self.update_suggestions_list())


    def update_all_frames_list(self):
        try:
            frames = self.all_frames_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            for frame in frames:
                self.all_scroll.add_line(END, frame.name)
        self.after(50, lambda: self.update_all_frames_list())
            

if __name__ == '__main__':
    options = {'triggers': ['falar', 'transferir'],
               'suggestion': {'title': 'Sugestões'},
               'all':{'title': 'Todos' }}
    fnutils.create_session()
    FrameSelection(options).mainloop()
