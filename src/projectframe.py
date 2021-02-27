from scrolledlist import ScrolledList
from tkinter import *
import _thread, queue, time
import datasource


class ProjectFrame(Frame):

    def __init__(self, optinos, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.options = options
        self.make_widgets()
        self.load_content()

    def _is_annotator_project_owner(self):
        return self.options['annotator'].id == self.options['project'].owner_id
    
        
    def make_widgets(self):

        self.tasks_scrolllist = ScrolledList(options['tasks'], parent=self)
        btn_new_task = Button(self, text='Nova tarefa', command=self.create_task)
        self.annotators_scrollist = ScrolledList(option['annotators'], parent=self)
        self.searchannotator = SearchAnnotatorFrame(None, parent=self)

        self.tasks_scrolllist.pack(side=TOP, expand=YES, fill=BOTH)
        btn_new_task.pack(side=TOP, anchor=SW, expand=YES)
        self.annotators_scrollist.pack(side=TOP, expand=YES, fill=BOTH)
        self.searchannotatorframe.pack(side=TOP, expand=YES, fill=BOTH)
        
        
        top = Menu(win)
        win.config(menu=top)
        self.project_menu = Menu(top)

        if self._is_annotator_project_owner():
            self.project_menu.add_command(label='Nova Tarefa...', command=self.create_task, underline=0)
            self.project_menu.add_command(label='Novo Anotador...', command=self.add_annotator, underline=0)
            
        self.project_menu.add_command(label='Voltar...', command=self.project_logout, underline=0)
        top.add_cascade(label='Opções', menu=self.tasks_menu, underline=0)

        
    def load_content(self):
        self.tasks_queue = queue.Queue()
        self.tasks = []
        _thread.start_new_thread(self.load_tasks, ())


    def create_task(self):
        "Call dialog to create task"
        pass

    def add_annotator(self):
        pass
    
    def project_logout(self):
        print('logout project')
        if self.on_project_logout:
            self.on_project_logout()

    def set_on_project_logout(self, fn):
        self.on_project_logout = fn

    def load_tasks(self):
        self.tasks = datasource.load_tasks(self.options['annotator'])
        self.tasks_queue.put(self.tasks)

    def update_tasks_list(self):
        try:
            tasks = self.tasks_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            for task in tasks:
                self.tasks_scrolllist.add_line(END, task.name)
                self.after(50, self.update_tasks_list)

