from scrolledlist import ScrolledList
from tkinter import *
import _thread, queue, time
import datasource


class TasksFrame(Frame):

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
        top = Menu(win)
        win.config(menu=top)
        self.tasks_menu = Menu(top)

        if self._is_annotator_project_owner():
            self.tasks_menu.add_command(label='Nova...', command=self.create_task, underline=0)
        self.tasks_menu.add_command(label='Voltar...', command=self.project_logout, underline=0)
        top.add_cascade(label='Opções', menu=self.tasks_menu, underline=0)

        
    def load_content(self):
        self.tasks_queue = queue.Queue()
        self.tasks = []
        _thread.start_new_thread(self.load_tasks, ())


    def create_task(self):
        "Call dialog to create task"
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
