from scrolledtext import ScrolledText
from tkinter import *


def show_text_dialog(parent_win, title, text, **config):
    win = Toplevel()
    win.title(title)
    msg = ScrolledText(parent=win, text=text)
    msg.config(**config)
    msg.pack(fill=X, expand=YES)
    
    win.update()
    x_left = int(parent_win.winfo_screenwidth()/2 - win.winfo_width()/2)
    y_top = int(parent_win.winfo_screenheight()/2 - win.winfo_height()/2)
    
    win.geometry("+{}+{}".format(x_left, y_top))
    
    win.bind('<KeyPress-q>', lambda e: Frame.destroy(win))
    win.bind('<Up>', lambda e: msg.scroll_text_up())
    win.bind('<Prior>', lambda e: msg.scroll_text_up())
    win.bind('<Alt-v>', lambda e: msg.scroll_text_up())
    win.bind('<Down>', lambda e: msg.scroll_text_down())
    win.bind('<Next>', lambda e: msg.scroll_text_down())
    win.bind('<Control-v>', lambda e: msg.scroll_text_down())
    win.focus_set()
    win.grab_set()
    win.wait_window()
        
