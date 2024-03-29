"a simple text or file viewer component"
print('PP4E scrolledtext')

from tkinter import *

class ScrolledText(Frame):
    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makewidgets()
        self.settext(text, file)
        
    def makewidgets(self):
        sbar = Scrollbar(self)
        text = Text(self, relief=SUNKEN)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        self.text = text

    def config(self, **config):
        self.text.config(**config)
        
    def get_text_widget(self):
        return self.text

    def settext(self, text='', file=None):
        if file:
            text = open(file, 'r').read()
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()


    def gettext(self):
        return self.text.get('1.0', END+'-1c')


    def scroll_text_up(self):
        self.scroll_text(-1)

    def scroll_text_down(self):
        self.scroll_text(1)

    def scroll_text(self, direction):
        self.text.yview_scroll(direction, UNITS)

if __name__ == '__main__':
    root = Tk()
    if len(sys.argv) > 1:
        st = ScrolledText(file=sys.argv[1])
    else:
        st = ScrolledText(text='Words\ngo here')
    def show(event):
        print(repr(st.gettext()))
        root.bind('<Key-Escape>', show)
        root.mainloop()    
