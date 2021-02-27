from scrolledlist import ScrolledList
from tkinter import *
import _thread, queue, time
import datasource


class ProjectsFrame(Frame):

    def __init__(self, optinos, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.options = options
        self.make_widgets()
        self.load_content()

    def make_widgets(self):
        self.projects_scrolllist = ScrolledList(options['projects'], parent=self)
        top = Menu(win)
        win.config(menu=top)
        file = Menu(top)
        file.add_command(label='Novo...', command=self.create_project, underline=0)
        file.add_command(label='Sair...', command=self.annotator_logout, underline=0)
        top.add_cascade(label='Opções', menu=file, underline=0)

        
    def load_content(self):
        self.projects_queue = queue.Queue()
        self.projects = []
        _thread.start_new_thread(self.load_projects, ())


    def load_project(self, i, s):
        print('load project %s %s' % (i, s))
        if self.projects and len(self.projects) > i and self.on_load_project:
            self.on_load_project(self.projects[i])

    def set_on_load_project(self, fn):
        self.on_load_project = fn

    def annotator_logout(self):
        print('logout annotator')
        if self.on_annotator_logout:
            self.on_annotator_logout()
        
    def set_on_annotator_logout(self, fn):
        self.on_annotator_logout = fn

    def create_project(self):
        "Call dialog to create project"
        pass


    def annotator_logout(self):
        pass

    def load_projects(self):
        self.projects = datasource.load_projects(self.options['annotator'])
        self.projects_queue.put(self.projects)

    def update_projects_list(self):
        try:
            projects = self.projects_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            for project in projects:
                self.projects_scrolllist.add_line(END, project.name)
        self.after(50, self.update_projects_list)
