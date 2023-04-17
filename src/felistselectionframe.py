from tkinter import *
import fnutils
import _thread, queue, time


class FEListSelectionFrame(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.options = options
        self.fes = {}
        self.fes_colors = []
        self.make_widgets()

    def set_fes(self, fes):
        self.fes = fes
        self.fes_colors = list(fes.values())
        self.create_fes_radios_list()

    def cycle_selection_fe(self):
        if self.fes_colors:
            cur_fe_name = self.var_fes.get()
            self.var_fes.set(self._get_next_fe_name(cur_fe_name))
            self.on_press_radio_arg()
    
    def cycle_step_selection_fe(self, step_func):
        if self.fes_colors:
            cur_fe_name = self.var_fes.get()
            self.var_fes.set(step_func(cur_fe_name))
            self.on_press_radio_arg()
            
    def cycle_next_selection_fe(self):
        self.cycle_step_selection_fe(self._get_next_fe_name)

    def cycle_previous_selection_fe(self):
        self.cycle_step_selection_fe(self._get_previous_fe_name)
        
    def _get_previous_fe_name(self, fe_name):
        return self._get_step_fe_name(fe_name, lambda i : i-1)
    
    def _get_next_fe_name(self, fe_name):
        return self._get_step_fe_name(fe_name, lambda i : i+1)

    def _get_step_fe_name(self, fe_name, step_func):
        i = 0
        for fe_color in self.fes_colors:
            if fnutils.fe_name_type(fe_color.fe) == fe_name:
                break
            i += 1

        i = step_func(i)
        i = i % len(self.fes_colors)
        return fnutils.fe_name_type(self.fes_colors[i].fe)
        

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
            for fe_color in self.fes_colors:
                if fnutils.fe_name_type(fe_color.fe) == fe_name:
                    return (fe_color.fe, fe_color.color)
            return None
        else:
            return None

    def get_fe_color(self, fe_id):
        return self.fes.get(fe_id).color

    def get_fe(self, fe_id):
        return self.fes.get(fe_id).fe

    def create_fes_radios_list(self):
        self.clear_fes_rows()
            
        self.var_fes = StringVar()

        if self.fes:
            self.canv.config(scrollregion=(0, 0,
                                           150, 30+len(list(self.fes.values()))*30))

        self.fes_selection_vars = []

        for i, fe_color in enumerate(self.fes_colors):
            row = Frame(self)
            row_type = Frame(row)
            rad_type = Radiobutton(row_type, fg='black',
                                   text=fnutils.fe_name_type(fe_color.fe),
                                   value=fnutils.fe_name_type(fe_color.fe),
                                   variable=self.var_fes,
                                   command=self.on_press_radio_arg,
                                   bg=fe_color.color)
            rad_type.pack(side=TOP)
            row_type.pack(side=TOP, expand=YES, fill=X)
            self.rows_ids.append(self.canv.create_window(10,30+(i*30),
                                                         anchor=W, window=row))


    def clear_fes_rows(self):
        for row_id in self.rows_ids:
            self.canv.delete(row_id)
    

    def make_widgets(self):
        lab = Label(self, text=self.options['title'])
        lab.pack(side=TOP, fill=X)
        canv = Canvas(self, bg='white', relief=SUNKEN)
        canv.config(highlightthickness=0)
        canv.config(width=150, height=100)

        sbar = Scrollbar(self)
        sbar.config(command=canv.yview)
        canv.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canv.pack(side=LEFT, expand=YES, fill=BOTH)

        self.canv = canv
        self.rows_ids = []
        self.create_fes_radios_list()


    def _get_index_by_fe_id(self, fe_id):
        i = 0
        for fe in self.fes:
            print('fe n-%s :: %s' % (i, fe.ID))
            if int(fe_id) == fe.ID:
                return i
            i += 1
        return None
    
if __name__ == '__main__':
    class FN():
        def __init__(self, name, id):
            self.name = name
            self.id = id
            
    options = {'fes_colors': ['#85E314', '#33E4CF',
                              '#F14EAA', '#F1D54A',
                              '#E67D57', '#F3BCBC'],
               'fes': [FN('Local', 1), FN('Tempo', 2), FN('Atacante', 3)],
               'title' : 'Elementos Core'   }
    fe_list = FEListSelectionFrame(options)
    
    fe_list.set_fes(options['fes'])
    fe_list.mainloop()
