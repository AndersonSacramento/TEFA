from tkinter import *

import _thread, queue, time


class FESelectedListFrame(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.options = options
        self.fes = {}
        self.make_widgets()


    def set_args_ann(self, args_ann):
        self.args_ann = args_ann

    def set_sentence_text(self, text):
        self.sentence_text = text

    def set_fes(self, fes):
        self.fes = fes
        
    def set_args_fes(self, fes, args_ann, sentence_text):
        self.set_fes(fes)
        self.set_args_ann(args_ann)
        self.set_sentence_text(sentence_text)
        self.create_fes_radios_list()

    def get_fes(self):
        return self.fes

    def on_press_radio_arg(self):
        pick = self.var_fes.get()
        if self.on_press_radion_handler:
            self.on_press_radion_handler(self)
        print('you pressed', pick)


    def set_on_press_radio_handler(self, fn):
        self.on_press_radion_handler = fn

    def get_radio_fe_and_color(self):
        fe_name = self.var_fes.get()
        if self.fes:
            for fe_color in self.fes.values():
                if fe_color.fe.name == fe_name:
                    return (fe_color.fe, fe_color.color)
            return None
        else:
            return None

    def get_fe_color(self, fe_id):
        print('fes selected %s' % self.fes)
        return self.fes[fe_id].color

    def create_fes_radios_list(self):
        self.clear_fes_rows()
        
        self.var_fes = StringVar()

        if self.fes:
            #self.var_fes.set(self.fes_names[0])
            
            self.canv.config(scrollregion=(0, 0, 150, 30+(len(list(self.fes.values())) + len(self.args_ann))*80))

        self.fes_selection_vars = []

        #fes_colors = [fe_color.color for fe_color in self.fes.values()]

        args_fe_count = {fe_id:len([arg_ann for arg_ann in self.args_ann if arg_ann.event_fe_id == fe_id]) for fe_id in self.fes }
        next_row_px_add = 0
        for i, fe_color in enumerate(self.fes.values()):
            row = Frame(self)
            row_type = Frame(row)
            rad_type = Radiobutton(row_type, text=fe_color.fe.name, value=fe_color.fe.name, variable=self.var_fes, command=self.on_press_radio_arg, bg=fe_color.color)
            rad_type.pack(side=TOP, anchor=NW)
            row_type.pack(side=TOP, expand=YES, fill=X,  anchor=NW)
            j = 0
            row_arg = Frame(row)
            row_arg.config(width=140)
            for arg_ann in [arg_ann for arg_ann in self.args_ann if arg_ann.event_fe_id == fe_color.fe.ID]:
                arg_text = self.sentence_text[arg_ann.start_at:arg_ann.end_at]
                msg_arg = Message(row_arg,text=arg_text)
                msg_arg.config(font=('times', 12))
                msg_arg.config(width=300)
                msg_arg.pack(side=TOP, fill=X, expand=YES, anchor=NW)
                print('make message: %s \n%d' % (arg_text, j))
                j += 1
            row_arg.pack(side=TOP, expand=YES, fill=X,  anchor=NW)
            row.config(width=300)
            row.pack(expand=YES, fill=X)
            self.rows_ids.append(self.canv.create_window(10,((i+1) * 100) + (args_fe_count[fe_color.fe.ID]-1)*50 +next_row_px_add, anchor=W, window=row, width=300))
            next_row_px_add = (args_fe_count[fe_color.fe.ID]-1)*50



    # def create_fes_radios_list(self):
    #     self.clear_fes_rows()
        
    #     self.var_fes = StringVar()
    #     self.fes_names = [fe.name for fe in self.fes]
    #     if self.fes_names:
    #         self.var_fes.set(self.fes_names[0])
    #         self.canv.config(scrollregion=(0, 0, 150, 30+len(self.fes)*30))

    #     self.fes_selection_vars = []

    #     for i in range(len(self.fes)):
    #         row = Frame(self)
    #         row_type = Frame(row)
    #         rad_type = Radiobutton(row_type, text=self.fes_names[i], value=self.fes_names[i], variable=self.var_fes, command=self.on_press_radio_arg, bg=self.fes_colors[i])
    #         rad_type.pack(side=TOP)
    #         row_type.pack(side=TOP, expand=YES, fill=X)
            
    #         self.rows_ids.append(self.canv.create_window(10,30+(i*30), anchor=W, window=row))



    def clear_fes_rows(self):
        for row_id in self.rows_ids:
            self.canv.delete(row_id)

    
    

    def make_widgets(self):
        lab = Label(self, text=self.options['title'])
        lab.pack(side=TOP, fill=X)
        canv = Canvas(self, bg='white', relief=SUNKEN)
        canv.config(highlightthickness=0)
        canv.config(width=150, height=100)
        # canv.config(scrollregion=(0, 0, 300, 200))


        sbar = Scrollbar(self)
        sbar.config(command=canv.yview)
        canv.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canv.pack(side=LEFT, expand=YES, fill=BOTH)

        self.canv = canv
        self.rows_ids = []
        self.create_fes_radios_list()


        
    def load_args_text(self):
        args_text = []
        if self.args_ann:
            sentence = fnutils.query_sentence_by_event_id(self.args_ann[0].event_ann_id)
            if sentence:
                for arg_ann in self.args_ann:
                    args_text.append(sentence.text[arg_ann.start_at:arg_ann.end_at])
                    self.queue_args_text.put(args_text)


    def update_args_text(self):
        try:
            args_text = self.queue_args_text.get(block=False)
        except queue.Empty:
            pass
        else:
            i = 0
            if self.fes and self.args_ann and self.fes_selection_vars:
                index = fnutils.get_index_by_fe_id(self.fes[i].ID, self.args_ann)
                self.fes_selection_vars[i].set(args_text[index])
                i += 1
                self.after(50, lambda: self.update_args_text())
                
    
if __name__ == '__main__':
    class FN():
        def __init__(self, name, id):
            self.name = name
            self.id = id
            
    options = {'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': [FN('Local', 1), FN('Tempo', 2), FN('Atacante', 3)],
               'title' : 'Elementos Anotados'   }
    fe_list =  FESelectedListFrame(options)
    
    fe_list.set_fes(options['fes'])
    fe_list.mainloop()
