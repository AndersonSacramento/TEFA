from nltk.corpus import framenet as fn
from tkinter import *
import _thread, queue, time
import fnutils



class FESelection(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.fes_colors =  ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC']
        self.fes = []
        self.args_ann = []
        self.make_list_fes(options)
        self.options = options


    def set_args_ann(self, args_ann):
        self.args_ann = args_ann

    def set_fes(self, fes):
        self.fes = fes
        self.create_fes_radios()
        
    def make_list_fes(self, options):
        canv = Canvas(self, bg='white', relief=SUNKEN)
        canv.config(width=300, height=200)
        canv.config(scrollregion=(0, 0, 300, 200)) #50+len(fes)*50))
        canv.config(highlightthickness=0)

        sbar = Scrollbar(self)
        sbar.config(command=canv.yview)
        canv.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canv.pack(side=LEFT, expand=YES, fill=BOTH)

        self.canv = canv
        self.rows_ids = []
        self.create_fes_radios()
        

    def on_press_radio_arg(self):
        pick = self.var_fes.get()
        print('you pressed', pick)

    def get_radio_fe_and_color(self):
        fe_name = self.var_fes.get()
        if fe_name and self.fes and self.fes_names:
            fe_index = self.fes_names.index(fe_name)
            return (self.fes[fe_index], self.fes_colors[fe_index])
        else:
            return None
        
    def create_fes_radios(self):
        self.clear_args_rows()
            
        self.var_fes = StringVar() #IntVar(0)
        #fes = options['fes']
        self.fes_names = [fe.name for fe in self.fes]
        if self.fes_names:
            self.var_fes.set(self.fes_names[0])
            self.canv.config(scrollregion=(0, 0, 300, 50+len(self.fes)*50))

        self.fes_selection_vars = []
        
        for i in range(len(self.fes)):
            row = Frame(self)
            row_content = Frame(row)
            rad = Radiobutton(row_content, text=str(self.fes_names[i]), value=self.fes_names[i], variable=self.var_fes, command=self.on_press_radio_arg, bg=self.fes_colors[i])
            rad.pack(side=LEFT)

            lab_content = Label(row_content)
            lab_content.pack(side=LEFT, fill=X)
            row_content.pack(side=TOP, expand=YES, fill=X)

            #msg = Message(row, text=self.fes[i].definition)
            #msg.config(font=('times', 12, 'normal'))
            #msg.pack(side=TOP, expand=YES, fill=X)
            
            var = StringVar()
            lab_content.config(textvariable=var)
            self.fes_selection_vars.append(var)

            self.rows_ids.append(self.canv.create_window(10,50+(i*50), anchor=W, window=row))

    def clear_args_rows(self):
        for row_id in self.rows_ids:
            self.canv.delete(row_id)

    
if __name__ == '__main__':
    options = {'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': ['Local', 'Tempo', 'Atacante']}
    FESelection(options).mainloop()
