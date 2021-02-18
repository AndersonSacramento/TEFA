from scrolledlist import ScrolledList
from scrolledtext import ScrolledText
from tkinter import *
from tkinter import ttk
import _thread, queue, time
import fnutils



class FrameSelection(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.make_widgets(options)
        self.options = options
        self.suggestions_queue = queue.Queue()
        self.all_frames_queue = queue.Queue()
        self.load_content()


    def make_widgets(self, options):
        vlist = options['triggers']
        self.trigger_var = StringVar()
        self.trigger_var.set("Selecione um gatilho")
        self.triggers_combo = ttk.Combobox(self, values=vlist)
        self.triggers_combo.config(textvariable=self.trigger_var)
        self.triggers_combo.pack(side=TOP)
        self.triggers_combo.current(0)
        self.triggers_combo.bind("<<ComboboxSelected>>", self.trigger_change_handler)

        self.var_event_type = StringVar()
        self.var_event_type.set('Tipo:')
        label = Label(self)
        label.pack(side=TOP, anchor=W)
        label.config(textvariable=self.var_event_type)

        self.suggestion_scroll = ScrolledList(options['suggestion'], parent=self)
        self.all_scroll = ScrolledList(options['all'], parent=self)
        
        
        self.suggestion_scroll.pack(side=TOP, expand=YES, fill=BOTH)
        self.all_scroll.pack(side=TOP, expand=YES, fill=BOTH)

        middle_handler = lambda i, s: self.event_type_selection(i[0], s)
        self.suggestion_scroll.set_middle_mouse_handle(middle_handler)
        self.all_scroll.set_middle_mouse_handle(middle_handler)

        self.suggestion_scroll.set_double_1_handler(lambda i, s: self.event_view_frame_suggestion(i[0], s))
        self.all_scroll.set_double_1_handler(lambda i, s: self.event_view_frame_all(i[0], s))

    def load_content(self):
        _thread.start_new_thread(self.load_all_frames_list, ())
        self.all_frames = []
        self.update_suggestions_list()
        self.update_all_frames_list()
        self.trigger_change_handler(None)
        
    def event_type_selection(self, i, s):
        self.var_event_type.set('Tipo: %s' % s)
        print(s)

    def event_view_frame_suggestion(self, i, s):
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
        win.focus_set()
        
    def trigger_change_handler(self, event):
        trigger = self.trigger_var.get()
        print(trigger)
        print(self.triggers_combo.current())
        self.suggestions_frames = []
        self.suggestion_scroll.clear_list()
        _thread.start_new_thread(self.load_frames_suggestions, (trigger,))

        
    def load_frames_suggestions(self, trigger_name):
        for frame_id in fnutils.query_frameid(trigger_name):
            frame = fnutils.frame_by_id(frame_id)
            if frame:
                self.suggestions_queue.put(frame)
                self.suggestions_frames.append(frame)

    def load_all_frames_list(self):
        for frame in sorted(fnutils.all_event_frames(), key=lambda f: f.name):
            self.all_frames_queue.put(frame)
            self.all_frames.append(frame)

    def update_suggestions_list(self):
        try:
            frame = self.suggestions_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.suggestion_scroll.add_line(END, frame.name)
        self.after(50, lambda: self.update_suggestions_list())


    def update_all_frames_list(self):
        try:
            frame = self.all_frames_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.all_scroll.add_line(END, frame.name)
        self.after(50, lambda: self.update_all_frames_list())
            

if __name__ == '__main__':
    options = {'triggers': ['falar', 'transferir'],
               'suggestion': {'title': 'Sugestões'},
               'all':{'title': 'Todos' }}
    fnutils.create_session()
    FrameSelection(options).mainloop()
