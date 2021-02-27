from nltk.corpus import framenet as fn
from tkinter import *
import _thread, queue, time
import fnutils

from db import ValArgANN


class FESelection(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.fes_colors =  ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC', '#B18904', '#2E9AFE', '#FA5858', '#A4A4A4', '#81F781']
        self.fes = []
        self.args_ann = []
        self.arg_val_handler = None
        self.make_list_fes(options)
        self.options = options
        self.queue_args_text = queue.Queue()


    def set_args_ann(self, args_ann):
        self.args_ann = args_ann

    def set_fes(self, fes):
        self.fes = fes
        self.create_fes_radios()
        #_thread.start_new_thread(self.load_args_text, ())
        #self.update_args_text()

    def set_val_args(self, vals_args):
        if vals_args and self.fes:
            for val_arg in vals_args:
                i = self._get_index_by_fe_id(val_arg.event_fe_id)
                print('set_val_args %s' % i)
                print('set_val fe_id  %s' % val_arg.event_fe_id)
                if i != None:
                    if val_arg.is_type_wrong():
                        self.type_selection_vars[i].set('Errado')
                        print('set type wrong')
                    else:
                        self.type_selection_vars[i].set('Certo')
                        print('set type right')
                    if val_arg.is_span_wrong():
                        self.ident_selection_vars[i].set('Errado')
                        print('set span wrong')
                    else:
                        self.ident_selection_vars[i].set('Certo')
                        print('set span right')


    def _get_index_by_fe_id(self, fe_id):
        i = 0
        for fe in self.fes:
            print('fe n-%s :: %s' % (i, fe.ID))
            if int(fe_id) == fe.ID:
                return i
            i += 1
        return None
            
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
        


    def on_press_type_radio_arg(self, i, ans):
        print('type radio position %d ans: %s' % (i, ans))
        if self.arg_val_handler:
            if self.fes:
                self.arg_val_handler(ValArgANN(status_type=ans,
                                               event_fe_id=self.fes[i].ID))

        

    def on_press_ident_radio_arg(self, i, ans):
        print('ident radio position %d ans: %s' % (i, ans))
        if self.arg_val_handler:
            if self.fes:
                self.arg_val_handler(ValArgANN(status_span=ans,
                                               event_fe_id=self.fes[i].ID))

    def set_arg_val_handler(self, func):
        self.arg_val_handler = func
            
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

    def get_fe_color(self, fe_id):
        i = 0
        for fe in self.fes:
            if fe.ID == fe_id:
                break
            i += 1
        return self.fes_colors[i]
        
    def create_fes_radios(self):
        self.clear_args_rows()
            
        self.var_fes = StringVar() #IntVar(0)
        #fes = options['fes']
        self.fes_names = [fe.name for fe in self.fes]
        if self.fes_names:
            self.var_fes.set(self.fes_names[0])
            self.canv.config(scrollregion=(0, 0, 300, 80+len(self.fes)*80))

        self.fes_selection_vars = []

        self.type_selection_vars = []
        self.ident_selection_vars = []
        
        for i in range(len(self.fes)):
            self.type_selection_vars.append(StringVar())
            self.ident_selection_vars.append(StringVar())
            
            row = Frame(self)
            row_type = Frame(row)
            lab_type = Label(row)
            lab_type.config(text=self.fes_names[i])
            lab_type.config(bg=self.fes_colors[i])
            lab_type.pack(side=TOP)


            lab_type_qs = Label(row_type)
            lab_type_qs.config(text='Tipo está: ')
            lab_type_qs.pack(side=LEFT)

            
            rad_type_right = Radiobutton(row_type, text='Certo',  value='Certo', variable=self.type_selection_vars[i], command=(lambda i=i: self.on_press_type_radio_arg(i, 'right')))
            rad_type_right.pack(side=RIGHT)
            
            rad_type_wrong = Radiobutton(row_type, text='Errado', value='Errado', variable=self.type_selection_vars[i], command=(lambda i=i: self.on_press_type_radio_arg(i, 'wrong')))
            rad_type_wrong.pack(side=RIGHT)

            row_type.pack(side=TOP, expand=YES, fill=X)


            #lab_ident = Label(row)
            #lab_ident.config(bg=self.fes_colors[i])
            #lab_ident.pack(side=LEFT)

            #var = StringVar()
            #lab_ident.config(textvariable=var)
           # self.fes_selection_vars.append(var)
            
            row_content = Frame(row)


            lab_ident_qs = Label(row_content)
            lab_ident_qs.config(text='Trecho está: ')
            lab_ident_qs.pack(side=LEFT)
            
            rad_ident_right = Radiobutton(row_content, text='Certo',  value='Certo', variable=self.ident_selection_vars[i], command=(lambda i=i: self.on_press_ident_radio_arg(i, 'right')))
            rad_ident_right.pack(side=RIGHT)
            
            rad_ident_wrong = Radiobutton(row_content, text='Errado', value='Errado', variable=self.ident_selection_vars[i], command=(lambda i=i: self.on_press_ident_radio_arg(i, 'wrong')))
            rad_ident_wrong.pack(side=RIGHT)

            row_content.pack(side=TOP, expand=YES, fill=X)
            

            self.rows_ids.append(self.canv.create_window(10,80+(i*80), anchor=W, window=row))

    def clear_args_rows(self):
        for row_id in self.rows_ids:
            self.canv.delete(row_id)

    
if __name__ == '__main__':
    options = {'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': ['Local', 'Tempo', 'Atacante']}
    FESelection(options).mainloop()
