from nltk.corpus import framenet as fn
from tkinter import *
import _thread, queue, time
import fnutils

from felistselectionframe import FEListSelectionFrame
from feselectedlistframe import FESelectedListFrame
#from db import ValArgANN


class FEColor():
    def __init__(self, fe, color):
        self.fe = fe
        self.color = color

    def fe_id(self):
        return self.fe.ID

class FESelection(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.colors =  ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC', '#B18904', '#2E9AFE', '#FA5858', '#A4A4A4', '#81F781', '#B18907', '#2E9AFD', '#FA5851', '#A18904', '#CE9AFE', '#DA5858', '#B1A907', '#2EAAFD', '#FAA851', '#A1A904', '#CEAAFE', '#DAA858', '#B1AB07', '#2EABFD', '#FAAB51', '#A1AB04', '#CEABFE', '#DAAB58']
        self.color_count = 0
        self.fes = {}
        self.args_ann = []
        self.arg_val_handler = None
        options['core_fes'] = {'title': 'Elementos Core' }
        options['peripheral_fes'] = {'title': 'Elementos peripheral'}
        options['selected_fes'] = {'title': 'Elementos anotados'}
        self.options = options
        self.fes_colors = {}
        self.selection_frame = None
        self.make_widgets()
        self.queue_args_text = queue.Queue()




    def set_arg_ann_remove_handler(self, func):
        self.fes_selection_list.set_arg_ann_remove_handler(func)
        
    def set_sentence_text(self, text):
        self.fes_selection_list.set_sentence_text(text)

    def set_args_ann(self, args_ann):
        self.fes_selection_list.set_args_ann(args_ann)


    def get_fe_color(self, fe_id):
        return self.fes_selection_list.get_fe_color(fe_id)


    def get_arg_fe(self, fe_id):
        return self.fes_selection_list.get_fe(fe_id)
    
    def get_radio_fe_and_color(self):
        if self.selection_frame:
           return  self.selection_frame.get_radio_fe_and_color()

    def cycle_selection_core_fe(self):
        self.core_selection_list.cycle_selection_fe()

    def cycle_selection_peripheral_fe(self):
        self.peripheral_selection_list.cycle_selection_fe()

    def cycle_selection_ann_fe(self):
        self.fes_selection_list.cycle_selection_fe()

    def set_on_fe_selection_handler(self, fn):
        self.on_fe_selection_handler = fn
        
    def on_fe_selection(self, selection_frame):
        self.selection_frame = selection_frame
        if self.on_fe_selection_handler:
            self.on_fe_selection_handler()

    def is_selected(self):
        return self.selection_frame is not None
    
    def _get_fe_color(self, fe):
        if fe.ID in self.fes_colors:
            return self.fes_colors.get(fe.ID)
        else:
            self.fes_colors[fe.ID] = FEColor(fe, self.colors[self.color_count])
            self.color_count += 1
            return self.fes_colors[fe.ID]
        
        
    def _set_fes(self, fes, fes_dict):
        for fe in fes:
            if fe.ID not in self.fes:
                fes_dict[fe.ID] = self._get_fe_color(fe)
                self.fes[fe.ID] = fes_dict[fe.ID]
                
    def set_core_fes(self, fes):
        core_fes = {}
        self._set_fes(fes, core_fes)
        self.core_selection_list.set_fes(core_fes)

    def set_peripheral_fes(self, fes):
        peripheral_fes = {}
        self._set_fes(fes, peripheral_fes)
        self.peripheral_selection_list.set_fes(peripheral_fes)

    def set_args_ann_fes(self, fes, args_ann, sentence_text):
        print('fes args ids %s' % [fe.ID for fe in fes])
        args_fes = {}
        self._set_fes(fes, args_fes)
        print('args_fes %s' % args_fes)
        self.fes_selection_list.set_args_fes(args_fes, args_ann, sentence_text)
        print('selection args_fes %s' % self.fes_selection_list.fes)

    
    def make_widgets(self):
        not_selected_row = Frame(self)

        self.core_selection_list = FEListSelectionFrame(self.options['core_fes'], parent=not_selected_row)
        self.peripheral_selection_list = FEListSelectionFrame(self.options['peripheral_fes'], parent=not_selected_row)
        
        self.core_selection_list.pack(side=TOP, expand=YES, fill=BOTH)
        self.peripheral_selection_list.pack(side=TOP, expand=YES, fill=BOTH)
        

        self.fes_selection_list = FESelectedListFrame(self.options['selected_fes'], parent=self)
        self.fes_selection_list.pack(side=LEFT, expand=YES, fill=BOTH)
        not_selected_row.pack(side=RIGHT, expand=YES, fill=BOTH)

        self.core_selection_list.set_on_press_radio_handler(self.on_fe_selection)
        self.peripheral_selection_list.set_on_press_radio_handler(self.on_fe_selection)
        self.fes_selection_list.set_on_press_radio_handler(self.on_fe_selection)

        
    def on_press_radio_arg(self):
        pick = self.var_fes.get()
        print('you pressed', pick)


    def _reset_fes_color(self):
        self.color_count = 0
        self.fes_colors = {}

    def update_fes(self):
        self.update_selections()
        self._reset_fes_color()
        
        
    def update_selections(self):
        self.clear_args_fes_rows()
        self.clear_core_fes_rows()
        self.clear_peripheral_fes_rows()
        self.fes = {}
        
    def clear_args_fes_rows(self):
        self.fes_selection_list.clear_fes_rows()

    def clear_core_fes_rows(self):
        self.core_selection_list.clear_fes_rows()
        
    def clear_peripheral_fes_rows(self):
        self.peripheral_selection_list.clear_fes_rows()
    
if __name__ == '__main__':
    options = {'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': ['Local', 'Tempo', 'Atacante']}
    FESelection(options).mainloop()
