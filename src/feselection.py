from nltk.corpus import framenet as fn
from tkinter import *
import _thread, queue, time
import fnutils



class FESelection(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.make_list_fes(options)
        self.options = options


    def make_list_fes(self, options):
        var_fes = StringVar() #IntVar(0)
        fes = options['fes']
        var_fes.set(fes[0])

        canv = Canvas(self, bg='white', relief=SUNKEN)
        canv.config(width=300, height=200)
        canv.config(scrollregion=(0, 0, 300, 50+len(fes)*50))
        canv.config(highlightthickness=0)

        sbar = Scrollbar(self)
        sbar.config(command=canv.yview)
        canv.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canv.pack(side=LEFT, expand=YES, fill=BOTH)

        
        self.fes_variables = []
        for i in range(len(fes)):
            row = Frame(self)
            rad = Radiobutton(row, text=str(fes[i]), value=fes[i], variable=var_fes, bg=options['fes_colors'][i])
            rad.pack(side=LEFT)

            lab_content = Label(row)
            lab_content.pack(side=LEFT, fill=X)
            var = StringVar()
            lab_content.config(textvariable=var)
            self.fes_variables.append(var)

            canv.create_window(10,50+(i*50), anchor=W, window=row)


    
if __name__ == '__main__':
    options = {'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': ['Local', 'Tempo', 'Atacante']}
    FESelection(options).mainloop()
