from tkinter import *
from tkinter import ttk
#import datasource



class CreateTaskDialog(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.options = options
        self.make_widgets()



    def make_widgets(self):
        row_name = Frame(self)
        lab_name = Label(row_name, text='Nome')
        ent_name = Entry(row_name)

        row_name.pack(side=TOP, fill=X)
        lab_name.pack(side=LEFT)
        ent_name.pack(side=RIGHT, expand=YES, fill=X)

        self.ent_name = ent_name

        row_desc = Frame(self)
        lab_desc = Label(row_desc, text='Descrição')
        ent_desc = Text(row_desc, height=5)

        row_desc.pack(side=TOP, fill=X)
        lab_desc.pack(side=LEFT)
        ent_desc.pack(side=RIGHT, expand=YES, fill=X)

        self.ent_desc = ent_desc

        row_type = Frame(self)
        lab_type = Label(row_type, text='Tipo')
        type_comb = ttk.Combobox(row_type)
        type_comb.bind('<<ComboboxSelected>>', self.task_type_selected_handler)
        type_comb.config(values=['Anotação', 'Revisão'])
        
        self.type_var = StringVar()
        self.type_var.set('Selecione o tipo')
        type_comb.config(textvariable=self.type_var)

        row_type.pack(side=TOP, fill=X)
        lab_type.pack(side=LEFT)
        type_comb.pack(side=RIGHT, expand=YES, fill=X)


        row_visib = Frame(self)
        lab_visib = Label(row_visib, text='Visibilidade')
        comb_visib = ttk.Combobox(row_visib)
        comb_visib.bind('<<ComboboxSelected>>', self.task_visibility_selected_handler)
        comb_visib.config(values=['Público', 'Privado'])

        
        self.visibility_var = StringVar()
        self.visibility_var.set('Selecione a visibilidade')
        comb_visib.config(textvariable=self.visibility_var)

        row_visib.pack(side=TOP, fill=X)
        lab_visib.pack(side=LEFT)
        comb_visib.pack(side=RIGHT, expand=YES, fill=X)


    def task_type_selected_handler(self, event):
        task_type = self.type_var.get()
        print('task type %s' % task_type)


    def task_visibility_selected_handler(self, event):
        task_visibility = self.visibility_var.get()
        print('task visibility %s' % task_visibility)



if __name__ == '__main__':
    options = {}
    CreateTaskDialog(options).mainloop()
