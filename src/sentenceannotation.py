from scrolledlist import ScrolledList
from scrolledtext import ScrolledText
from feselection import FESelection
from frameselection import FrameSelection
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import askquestion
import _thread, queue, time
import fnutils
from frameview import FrameView
from guiutils import show_text_dialog
from db import ArgANN
from copy import copy

class SentenceAnnotation(Frame):

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.options = options
        self.options['suggestion'] = {'title': 'Sugestões'}
        self.options['all'] = {'title': 'Todos' }
        self.sentence_queue = queue.Queue()
        self.events_queue = queue.Queue()
        self.vals_queue = queue.Queue()
        self.cur_event_ann = None
        self.make_widgets(self.options)
        self.load_content(self.options)
        self.load_default_modes()

    def load_default_modes(self):
        self.set_search_mode(False)
        self.to_delete_arg_ann = None
        self.set_delete_mode(False)
        self.set_delete_arg_mode(False)
        self.set_delete_event_type_mode(False)
        self.set_list_mode(False)
        self.to_view_arg_ann = None
        self.set_list_args_mode(False)
        self.set_select_text_mode(False)
        self.set_event_type_mode(False)
        self.set_event_type_suggestion_mode(False)
        self.set_event_type_all_mode(False)
        self.set_not_selected_fe_selection_mode(False)
        self.set_arg_fe_selection_mode(False)
        
    def middle_button_in_text(self):
        self.sentence_text_view.edit_undo()
        
    def make_widgets(self, options):
        left_frame = Frame(self)
        text = Text(left_frame)
        text.config(font=('courier', 15, 'normal'))
        text.config(width=20, height=12)
        text.pack(side=TOP, expand=YES, fill=BOTH)
        text.bind('<KeyPress>', lambda e: self.on_keyboard(e))
        #text.bind('<Key>', lambda e: 'break')
        #text.bind('<Button-2>', lambda e: self.middle_button_in_text)

        self.sentence_text_view = text


        mode_frame = Frame(left_frame)
        mode_frame.pack(side=TOP, expand=YES, fill=X)
        self.mode_frame = mode_frame

        arg_frame = Frame(mode_frame)
        self.fe_arg_list_var = StringVar()
        label_arg_fe = Label(arg_frame, text='', textvariable=self.fe_arg_list_var)
        label_arg_fe.pack(side=LEFT, expand=YES)
        self.label_arg_fe = label_arg_fe

        txt_arg_fe_def = Text(arg_frame, font=('times', 12), height=2)
        txt_arg_fe_def.pack(side=LEFT, expand=YES, fill=X)
        txt_arg_fe_def.bind('<KeyPress>', lambda e: self.on_keyboard(e))
        self.txt_arg_fe_def = txt_arg_fe_def

        arg_frame.pack_forget()
        self.arg_frame = arg_frame
        
        
        ann_frame = Frame(mode_frame)
        self.fe_arg_var = StringVar()
        label_fe =  Label(ann_frame, text='', textvariable=self.fe_arg_var)
        label_fe.pack(side=LEFT, expand=YES)
        self.label_fe = label_fe


        txt_fe_def = Text(ann_frame, font=('times', 12), height=2, width=50)
        txt_fe_def.pack(side=LEFT, expand=YES)
        txt_fe_def.bind('<KeyPress>', lambda e: self.on_keyboard(e))
        #txt_fe_def.bind('<Key>', lambda e: 'break')
        self.txt_fe_def = txt_fe_def


        btn_tag = Button(ann_frame, text='Anotar', command=self.annotate_arg)
        btn_tag.pack(side=RIGHT, expand=YES)
        ann_frame.pack_forget()
        self.ann_frame = ann_frame

        self.fe_selection = FESelection(options, parent=left_frame)
        self.fe_selection.pack(side=TOP, anchor=SW)
        self.fe_selection.set_arg_ann_remove_handler(self.ask_delete_cur_arg)#self.arg_ann_remove_handler)
        self.fe_selection.set_on_fe_selection_handler(self.set_fe_arg_label)

        #self.fe_selection.set_arg_val_handler(self.arg_val_handler)
        

        self.mode_str_var = StringVar()
        label_mode = Label(left_frame, text='', textvariable=self.mode_str_var, font=('times', 12))
        label_mode.pack(side=TOP, expand=YES, fill=X)
        left_frame.pack(side=LEFT, expand=YES, fill=BOTH)
        
        right_frame = Frame(self)
        self.frame_selection = FrameSelection(options, parent=right_frame)
        self.frame_selection.pack(side=TOP, anchor=NE)
        self.frame_selection.set_event_ann_type_selection_handler(self.event_type_selection_handler)
        self.frame_selection.set_event_ann_type_remove_handler(self.event_ann_type_remove_handler)
        self.frame_selection.set_binding_key_press(lambda e: self.on_keyboard(e))
        #self.frame_selection.set_event_val_handler(self.event_val_handler)
        

        # btn_frame = Frame(right_frame)

         
        
        # btn_save = Button(btn_frame, text='Salvar', command=self.save_annotation)
        # btn_save.pack(side=RIGHT, anchor=SE)

        # btn_preview = Button(btn_frame, text='Pré-visualizar', command=self.preview_annotation)
        # btn_preview.pack(side=LEFT, anchor=SE)
        # btn_frame.pack(side=TOP)
        right_frame.pack(side=RIGHT, expand=YES, fill=BOTH)
        self.parent.bind('<KeyPress>', self.on_keyboard)


        
    def load_view_frame_info(self):
        if self.cur_event_ann:
            frame = fnutils.frame_by_id(self.cur_event_ann.event_fn_id)
            if frame:
                win = Toplevel()
                frame_view = FrameView({'frame':frame}, win)
                win.focus_set()
                win.grab_set()
                win.wait_window()

        
    def load_content(self, options):
        _thread.start_new_thread(self.load_sentence, (options['sentence_id'], options['annotator_id']))
        self.sentence = None
        self.update_sentence_text()
        #self.update_val_ann()
        

    def load_sentence(self, sentence_id, annotator_id):
        self.events_ann = []
        sentence = fnutils.query_sentence_by(sentence_id)
        if sentence:
            events = fnutils.query_events_sentence(sentence)
            # from lome annotator
            events_ann = fnutils.query_events_ann(annotator_id, [e.id for e in events])
            if events_ann:
                self.events_ann = events_ann
                print('events ann recovered annotator_id: %s' % annotator_id)
            self.sentence_queue.put(sentence)
            self.events_queue.put(events)
            

    def save_annotation(self):
        # for event_ann in self.events_ann:
        #     event_ann.annotator_id = self.options['annotator_id']
        #     for arg_ann in event_ann.args_ann:
        #         arg_ann.annotator_id = self.options['annotator_id']
        #     fnutils.save_event_ann(event_ann)

        Frame.destroy(self.parent)

    def preview_annotation(self):
        pass

    def _find_arg_ann(self, args_ann, fe_id, start_at, end_at):
        for arg_ann in args_ann:
            if arg_ann.event_fe_id == fe_id and ((arg_ann.start_at <= start_at < end_at <= arg_ann.end_at) or (start_at <= arg_ann.start_at < arg_ann.end_at <= end_at)):

                return arg_ann
            

    def _is_alt_key(self, event):
        return event.state & 0x0008 or event.state & 0x0080

    def _is_ctrl_key(self, event):
        return event.state & 0x0004 or event.keysym == 'Control_L' or event.keysym == 'Control_R'



    def set_arg_fe_selection_mode(self, value):
        self.arg_fe_selection_mode = value

    def is_arg_fe_selection_mode(self):
        return self.arg_fe_selection_mode

    def set_not_selected_fe_selection_mode(self, value):
        self.not_selected_fe_selection_mode = value

    def is_not_selected_fe_selection_mode(self):
        return self.not_selected_fe_selection_mode

    def start_select_text_mode(self):
        self.print_mode_msg('modo de seleção de texto')
        cur_index = self.sentence_text_view.index(INSERT)
        if cur_index:
            self.sentence_text_view.tag_add(SEL, cur_index, cur_index)
        else:
            self.sentence_text_view.tag_add(SEL, "1.0", "1.0")
        self.show_ann_frame()
            
            

    def stop_select_text_mode(self):
        self._print_quit_mode_msg('modo de seleção de texto')
        self.sentence_text_view.tag_remove(SEL, '1.0', END)
        self.sentence_text_view.tag_delete(SEL, '1.0', END)
        self.hide_ann_frame()
    
    def _move_by_char_step(self, step_fn):
        cur_index = self.sentence_text_view.index(INSERT)
        end_index = self.sentence_text_view.index('1.end')
        end_pos = int(end_index.split('.')[1])
        print('cur_index %s end_pos %s' % (cur_index, end_pos))
        if cur_index and end_pos != 0:
            cur_pos = (int(cur_index.split('.')[1]) % end_pos)
            cur_pos = (cur_pos + step_fn(cur_pos)) % end_pos
            self.sentence_text_view.mark_set(INSERT, '%s.%s' % (cur_index.split('.')[0], cur_pos))
        else:
            self.sentence_text_view.mark_set(INSERT, '1.0')
            cur_pos = 0
        self.sentence_text_view.focus_set()
        self.sentence_text_view.see(INSERT)
        if self.is_select_mode():
            before_pos = (int(cur_index.split('.')[1]) % end_pos)
            try:
                sel_first = self.sentence_text_view.index(SEL_FIRST)
                sel_last = self.sentence_text_view.index(SEL_LAST)
            except:
                sel_first = '1.%s' % ((int(cur_index.split('.')[1])) % end_pos)
                sel_last = '1.%s' % ((int(cur_index.split('.')[1])) % end_pos)
            cur_index = self.sentence_text_view.index(INSERT)
            if cur_pos > before_pos:
                if sel_last > cur_index > sel_first:
                    self.sentence_text_view.tag_remove(SEL, '1.0', END)
                    self.sentence_text_view.tag_delete(SEL, '1.0', END)
                    self.sentence_text_view.tag_add(SEL, cur_index, sel_last)
                else:
                     self.sentence_text_view.tag_add(SEL, sel_first, cur_index)
            else:
                if  sel_last > cur_index > sel_first:
                    self.sentence_text_view.tag_remove(SEL, '1.0', END)
                    self.sentence_text_view.tag_delete(SEL, '1.0', END)
                    self.sentence_text_view.tag_add(SEL, sel_first, cur_index)
                else:
                    self.sentence_text_view.tag_add(SEL, cur_index, sel_last)
                

        
    def _move_by_char_forward(self):
        self._move_by_char_step(lambda cur_pos: 1)
        
    def _move_by_char_backward(self):
        self._move_by_char_step(lambda cur_pos: -1)

    def _move_to_sentence_start(self):
        self.sentence_text_view.mark_set(INSERT, '1.0')
        self.sentence_text_view.focus_set()
        self.sentence_text_view.see(INSERT)

    def _move_to_sentence_end(self):
        self.sentence_text_view.mark_set(INSERT, END)
        self.sentence_text_view.focus_set()
        self.sentence_text_view.see(INSERT)


    def _move_by_word(self, forwards=True):
        cur_index = self.sentence_text_view.index(INSERT)
        if not cur_index:
            self.sentence_text_view.mark_set(INSERT, '1.0')
            cur_index = '1.0'
            
        self.sentence_text_view.focus_set()
        self.sentence_text_view.see(INSERT)
        
        word_index = self.sentence_text_view.index('%s wordstart' % cur_index)
        end_word_index = self.sentence_text_view.search(' ', word_index, forwards=forwards)
        print('move by wrod cur_index %s' % cur_index)
        print('move by wrod word_index %s' % word_index)
        print('move by wrod end_word_index %s' % end_word_index)
        
        if forwards:
            if word_index == end_word_index:
                word_index = self.sentence_text_view.search('[^ ]', end_word_index, forwards=forwards, regexp=True)
                end_word_index = self.sentence_text_view.search(' ', word_index, forwards=forwards)
            self.sentence_text_view.mark_set(INSERT, end_word_index)
        else:
            if word_index == end_word_index or word_index == cur_index:
                word_index = self.sentence_text_view.search('[^ ]', word_index, backwards=True, regexp=True)
                print('move by new  word_index %s' % word_index)
                word_index = self.sentence_text_view.index('%s wordstart' % word_index)
                print('move by new  new word_index %s' % word_index)

            self.sentence_text_view.mark_set(INSERT, word_index)
        end_index = self.sentence_text_view.index('1.end')
        end_pos = int(end_index.split('.')[1])
        if self.is_select_mode():
            try:
                sel_first = self.sentence_text_view.index(SEL_FIRST)
                sel_last = self.sentence_text_view.index(SEL_LAST)
            except:
                sel_first = '1.%s' % ((int(cur_index.split('.')[1])) % end_pos)
                sel_last = '1.%s' % ((int(cur_index.split('.')[1])) % end_pos)
            before_index = cur_index
            cur_index = self.sentence_text_view.index(INSERT)
            if cur_index > before_index:
                if sel_last > cur_index > sel_first:
                    self.sentence_text_view.tag_remove(SEL, '1.0', END)
                    self.sentence_text_view.tag_delete(SEL, '1.0', END)
                    self.sentence_text_view.tag_add(SEL, cur_index, sel_last)
                else:
                    self.sentence_text_view.tag_add(SEL, sel_first, cur_index)
            else:
                if  sel_last > cur_index > sel_first:
                    self.sentence_text_view.tag_remove(SEL, '1.0', END)
                    self.sentence_text_view.tag_delete(SEL, '1.0', END)
                    self.sentence_text_view.tag_add(SEL, sel_first, cur_index)
                else:
                    self.sentence_text_view.tag_add(SEL, cur_index, sel_last)

            
    def _move_by_word_forward(self):
        self._move_by_word(forwards=True)

    def _move_by_word_backward(self):
        self._move_by_word(forwards=False)
        


    def set_select_text_mode(self, value):
        self.select_text_mode = value

    def is_select_mode(self):
        return self.select_text_mode
    
    def set_list_mode(self, value):
        self.list_mode = value

    def is_list_mode(self):
        return self.list_mode
    
    def set_list_args_mode(self, value):
        self.list_args_mode = value

    def is_list_args_mode(self):
        return self.list_args_mode
    
    def set_search_mode(self, value):
        self.search_mode = value
        self.search_str = ''

    def set_delete_event_type_mode(self, value):
        self.delete_event_type_mode = value

    def is_delete_event_type_mode(self):
        return self.delete_event_type_mode
    
    def set_delete_arg_mode(self, value):
        self.delete_arg_mode = value
        

    def is_delete_arg_mode(self):
        return self.delete_arg_mode
    
    def set_delete_mode(self, value):
        self.delete_mode = value

    def is_delete_mode(self):
        return self.delete_mode

    def set_event_type_suggestion_mode(self, value):
        self.event_type_suggestion_mode = value

    def is_event_type_suggestion_mode(self):
        return self.event_type_suggestion_mode

    def set_event_type_all_mode(self, value):
        self.event_type_all_mode = value

    def is_event_type_all_mode(self):
        return self.event_type_all_mode
    
    def set_event_type_mode(self, value):
        self.event_type_mode = value

    def is_event_type_mode(self):
        return self.event_type_mode
    
    def increment_search_str(self, char):
        self.search_str += char
        self.print_mode_msg('search string: %s' % self.search_str)
        self.frame_selection.search_frame(self.search_str)

    def decrement_search_str(self):
        self.search_str = self.search_str[:-1]
        self.print_mode_msg('search string: %s' % self.search_str)
        self.frame_selection.search_frame(self.search_str)
        
    def is_search_mode(self):
        return self.search_mode

    def is_cancel_cmd(self, event):
        pressed = event.keysym
        return  pressed == 'g' or (self._is_ctrl_key(event) and pressed == 'g')

    
    def on_keyboard(self, event):
        self._print_empty_mode_msg()
        pressed = event.keysym
     
        #self.bind_all('<Control-Key-f>', lambda e: Frame.destroy(self.parent))

        if self.is_select_mode():
            if self.is_cancel_cmd(event):
                self.set_select_text_mode(False)
                self.stop_select_text_mode()
            elif self._is_ctrl_key(event):
                if pressed == 'f':
                    self._move_by_char_forward()
                elif pressed == 'b':
                    self._move_by_char_backward()
                elif pressed == 'a':
                    self._move_to_sentence_start()
                elif pressed == 'e':
                    self._move_to_sentence_end()
            elif self._is_alt_key(event):
                if  pressed == 'e':
                    self.show_ann_frame()
                    self.fe_selection.cycle_selection_all_fe()
                elif pressed == 'a':
                    self.show_ann_frame()
                    self.fe_selection.cycle_selection_ann_fe()
                elif pressed == 'f':
                    self._move_by_word_forward()
                elif pressed == 'b':
                    self._move_by_word_backward()                    
            elif pressed == 'a':
                self.annotate_arg()
                self.set_select_text_mode(False)
                self.stop_select_text_mode()
            elif pressed == 'h':
                self.show_text_selection_mode_helper_dialog()
        elif self.is_list_mode():
            if pressed == 'a' or (self._is_ctrl_key(event) and pressed == 'a'):
                self.set_list_mode(False)
                self.set_list_args_mode(True)
                self.start_list_args_mode()
            elif self.is_cancel_cmd(event):
                self.set_list_mode(False)
                self._print_quit_mode_msg('modo de listagem de argumentos')
        elif self.is_list_args_mode():
            if pressed == 'n' or (self._is_ctrl_key(event) and pressed == 'n'):
                self.set_next_arg_ann_to_view()
            elif pressed == 'p' or (self._is_ctrl_key(event) and pressed == 'p'):
                self.set_previous_arg_ann_to_view()
            elif pressed == 'i':
                self.show_cur_arg_fe_definition_dialog()
            elif self.is_cancel_cmd(event):
                self.stop_list_args_mode()
                self.set_list_args_mode(False)
            elif pressed == 'h':
                self.show_list_args_mode_helper_dialog()
        elif self.is_delete_mode():
            if pressed == 'g':
                self.set_delete_mode(False)
            elif pressed == 'a':
                self.set_delete_mode(False)
                self.set_delete_arg_mode(True)
                self.start_delete_arg_mode()
            elif pressed == 't':
                self.set_delete_mode(False)
                #self.set_delete_event_type_mode(True)
                self.frame_selection.remove_event_type_handler()
                self.set_delete_event_type_mode(False)
                #self.ask_delete_cur_event_type()
        elif self.is_delete_arg_mode():
            if pressed == 'Return':
                self.ask_delete_cur_arg()
            elif pressed == 'g'or (self._is_ctrl_key(event) and pressed == 'g'):
                self.set_delete_arg_mode(False)
                self.stop_delete_arg_mode()
            elif pressed == 'n' or (self._is_ctrl_key(event) and pressed == 'n'):
                self.set_next_arg_ann_to_delete()
            elif pressed == 'p' or (self._is_ctrl_key(event) and pressed == 'p'):
                self.set_previous_arg_ann_to_delete()
            elif pressed == 'h':
                self.show_delete_args_mode_helper_dialog()
        elif self.is_search_mode():
            if self._is_ctrl_key(event):
                if  pressed == 'g':
                    self._print_quit_mode_msg('modo de pesquisa')
                    self.set_search_mode(False)
                    self.frame_selection.clear_search_frame()
                elif pressed == 'n':
                    self.frame_selection.select_next_frame_all_list()
                elif pressed == 'p':
                    self.frame_selection.select_previous_frame_all_list()
                elif pressed == 'i':
                    self.frame_selection.view_info_current_frame()
                elif pressed == 'h':
                    self.show_search_mode_helper_dialog()
            elif  pressed == 'Return':
                if self.frame_selection.select_event_type():
                    self.frame_selection.clear_search_frame()
                    self.set_search_mode(False)
                #self.ask_change_cur_event_type()
            else:
                if pressed == 'underscore':
                    pressed = '_'
                if pressed == 'BackSpace':
                    self.decrement_search_str()
                else:
                    self.increment_search_str(event.char)
        elif self.is_event_type_mode():
            if pressed == 's':
                self.set_event_type_mode(False)
                self.set_event_type_suggestion_mode(True)
            elif pressed == 'a':
                self.set_event_type_mode(False)
                self.set_event_type_all_mode(True)
            elif self.is_cancel_cmd(event):
                self.set_event_type_mode(False)
        elif self.is_event_type_suggestion_mode():
            if self._is_ctrl_key(event) and pressed == 'i':
                self.frame_selection.view_info_current_suggestion_frame()
            if pressed == 'n':
                self.frame_selection.select_next_frame_suggestion_list()
            elif pressed == 'p':
                self.frame_selection.select_previous_frame_suggestion_list()
            elif pressed == 'h':
                self.show_frame_selection_mode_helper_dialog()
            elif self.is_cancel_cmd(event):
                self.set_event_type_suggestion_mode(False)
            elif pressed == 'Return':
                if self.frame_selection.select_suggestion_event_type():
                    self.set_event_type_suggestion_mode(False)
        elif self.is_event_type_all_mode():
            if pressed == 'n':
                self.frame_selection.select_next_frame_all_list()
            elif pressed == 'p':
                self.frame_selection.select_previous_frame_all_list()
            elif pressed == 'h':
                self.show_frame_selection_mode_helper_dialog()
            elif self.is_cancel_cmd(event):
                self.set_event_type_all_mode(False)
            elif pressed == 'Return':
                if self.frame_selection.select_event_type():
                    self.set_event_type_all_mode(False)
        elif self.is_arg_fe_selection_mode():
            if pressed == 'n':
                self.fe_selection.cycle_next_selection_ann_fe()
            elif pressed == 'p':
                self.fe_selection.cycle_previous_selection_ann_fe()
            elif pressed == 'i':
                self.show_cur_selected_fe_definition_dialog()
            elif pressed == 'h':
                self.show_fes_selection_mode_helper_dialog()
            elif self.is_cancel_cmd(event):
                self.set_arg_fe_selection_mode(False)
                self.hide_ann_frame()
                self._print_quit__mode_msg('modo de selação de tipo do argumento') 
        elif self.is_not_selected_fe_selection_mode():
            if pressed == 'n':
                self.fe_selection.cycle_next_selection_all_fe()
            elif pressed == 'p':
                self.fe_selection.cycle_previous_selection_all_fe()
            elif pressed == 'i':
                self.show_cur_selected_fe_definition_dialog()
            elif pressed == 'h':
                self.show_fes_selection_mode_helper_dialog()
            elif self.is_cancel_cmd(event):
                self.set_not_selected_fe_selection_mode(False)
                self.hide_ann_frame()
                self._print_quit_mode_msg('modo de selação de tipo do argumento') 
        elif self._is_alt_key(event):
            if pressed == 'e':
                self.start_not_selected_fe_selection_mode()
                #self.fe_selection.cycle_selection_all_fe()
            # elif pressed == 'c':
            #     self.show_ann_frame()
            #     self.fe_selection.cycle_selection_core_fe()
            # elif pressed == 'p':
            #     self.show_ann_frame()
            #     self.fe_selection.cycle_selection_peripheral_fe()
            elif pressed == 'a':
                self.start_arg_fe_selection_mode()
                #self.fe_selection.cycle_selection_ann_fe()
            elif pressed == 'f':
                self._move_by_word_forward()
            elif pressed == 'b':
                self._move_by_word_backward()
        elif self._is_ctrl_key(event):
            print('contrl key pressed: %s' % pressed)
            if pressed == 's':
                self.set_search_mode(True)
                self.print_mode_msg('modo de pesquisa')
            elif pressed == 'g':
                print('cancel search mode')
                self.set_search_mode(False)
            elif pressed == 'd':
                print('delete mode')
                self.set_delete_mode(True)
            elif pressed == 't':
                self.set_event_type_mode(True)
            elif pressed == 'l':
                self.set_list_mode(True)
            elif pressed == 'f':
                self._move_by_char_forward()
            elif pressed == 'b':
                self._move_by_char_backward()
            elif pressed == 'a':
                self._move_to_sentence_start()
            elif pressed == 'e':
                self._move_to_sentence_end()
            elif pressed == 'space':
                self.set_select_text_mode(True)
                self.start_select_text_mode()
        else:
            if pressed == 'a':
                self.annotate_arg()
            elif pressed == 'i':
                self.load_view_frame_info()
            elif pressed == 'q':
                Frame.destroy(self.parent)
            elif pressed == 't':
                self.frame_selection.cycle_combobox_trigger()
            elif pressed == 'h':
                self.show_main_helper_dialog()

        return "break"



    def _print_empty_mode_msg(self):
        self.print_mode_msg('')
        
    def _print_quit_mode_msg(self, mode_name):
        self.print_mode_msg('cancelado %s' % mode_name)
        
    def print_mode_msg(self, msg):
        self.mode_str_var.set(msg)
    
    def set_fe_arg_ann_label(self, arg_ann):
        fe_color = self.fe_selection.get_fe_color(arg_ann.event_fe_id)
        fe = self.fe_selection.get_arg_fe(arg_ann.event_fe_id)
        self.fe_arg_list_var.set(fe.name)
        self.txt_arg_fe_def.delete('1.0', END)
        self.txt_arg_fe_def.insert('1.0', fe.definition)
        self.label_arg_fe.config(background=fe_color)
    
    def set_fe_arg_label(self):
        print('set_fe_arg_label')
        output = self.fe_selection.get_radio_fe_and_color()
        if output:
            fe, fe_color = output
            self.fe_arg_var.set(fe.name)
            self.txt_fe_def.delete('1.0', END)
            self.txt_fe_def.insert('1.0', fe.definition)
            self.label_fe.config(background=fe_color)
        else:
            self.fe_arg_var.set('')
            bg = self.cget("background")
            self.label_fe.config(background=bg)
            self.txt_fe_def.delete('1.0', END)
            self.txt_fe_def.insert('1.0', '')
        
    def annotate_arg(self):
        try:
            text = self.sentence_text_view.get(SEL_FIRST, SEL_LAST)
        except Exception:
            text = ''
        if text and self.fe_selection.is_selected():
            start_at = self.sentence_text_view.index(SEL_FIRST).split('.')[1]
            end_at = self.sentence_text_view.index(SEL_LAST).split('.')[1]
            output = self.fe_selection.get_radio_fe_and_color()
            if output:
                fe, fe_color = output
            else:
                return
                # fe can be None ?
            if self.cur_event_ann:

                arg_ann = self._find_arg_ann(self.cur_event_ann.args_ann, fe.ID, int(start_at), int(end_at))
                if arg_ann:
                    tag_name = '%s-%s-%s:%s' % (fe.ID, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
                    self.sentence_text_view.tag_remove(tag_name,'1.0', END)
                    previous_arg = arg_ann.copy()
                    arg_ann.start_at =  int(start_at)
                    arg_ann.end_at = int(end_at)
                    arg_ann.updated_at = fnutils.now()
                    fnutils.save_arg_ann(arg_ann)
                    fnutils.delete_arg_ann(previous_arg)

                    print('update arg_ann start_at %s end_at %s' % (arg_ann.start_at, arg_ann.end_at))
                else:
                    arg_ann = ArgANN(start_at=int(start_at),
                                     end_at=int(end_at),
                                     created_at=fnutils.now(),
                                     event_fe_id=fe.ID,
                                     event_ann_id=self.cur_event_ann.id,
                                     annotator_id=self.options['annotator_id'])
                    fnutils.save_arg_ann(arg_ann)
                    self.cur_event_ann.args_ann.append(arg_ann)
                    print('create arg_ann')
                tag_name = '%s-%s-%s:%s' % (fe.ID, self.cur_event_ann.id, start_at, end_at)
                self.sentence_text_view.tag_remove(tag_name,'1.0', END)
                self.sentence_text_view.tag_add(tag_name, '1.%s' % start_at, '1.%s' % end_at)
                self.sentence_text_view.tag_config(tag_name, background=fe_color)
                    
                self._update_fes_selections(self.cur_event_ann)
                                                     
            
        #sel_first_pos = SEL + '.first'
        #sel_last_pos = SEL + '.last'
        #print('annotate arg %s \n %s %s %s' % (text, str(self.sentence_text_view.index(sel_first_pos)), str(self.sentence_text_view.index(sel_last_pos)), str(len(self.sentence_text_view.get('0.0', END)))))


    def load_event_args_ann_tags(self):
        if self.cur_event_ann:
            for arg_ann in self.cur_event_ann.args_ann:
                self.load_arg_ann_tag(arg_ann)

    def load_arg_ann_tag(self, arg_ann):
        tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
        self.sentence_text_view.tag_remove(tag_name,'1.0', END)
        self.sentence_text_view.tag_add(tag_name, '1.%s' % arg_ann.start_at, '1.%s' % arg_ann.end_at)
        print('even_ann_id = %s event_fe_id %s' % (arg_ann.event_ann_id, arg_ann.event_fe_id))
        fe_color = self.fe_selection.get_fe_color(arg_ann.event_fe_id)
        self.sentence_text_view.tag_config(tag_name, background=fe_color)
        

    def highlight_event(self, event):
        if event:
            self.sentence_text_view.tag_delete('trigger', '1.0', END)
            self.sentence_text_view.tag_add('trigger','1.%s' % event.start_at, '1.%s' % event.end_at)
            self.sentence_text_view.tag_config('trigger', font=('times', 16, 'bold'))


    def show_ann_frame(self):
        self.arg_frame.pack_forget()
        self.ann_frame.pack(side=TOP, expand=YES, fill=X)
        self.set_fe_arg_label()

    def hide_ann_frame(self):
        self.ann_frame.pack_forget()

    def start_not_selected_fe_selection_mode(self):
        self.print_mode_msg('modo de seleção de tipo do argumento')
        self.set_not_selected_fe_selection_mode(True)
        self.show_ann_frame()
        self.fe_selection.cycle_next_selection_all_fe()
        self.fe_selection.cycle_previous_selection_all_fe()


    def start_arg_fe_selection_mode(self):
        self.print_mode_msg('modo de seleção de tipo do argumento')
        self.show_ann_frame()
        self.set_arg_fe_selection_mode(True)
        self.fe_selection.cycle_next_selection_ann_fe()
        self.fe_selection.cycle_previous_selection_ann_fe()
        
    def start_delete_arg_mode(self):
        self.print_mode_msg('modo de exclusão de argumentos')
        self.ann_frame.pack_forget()
        self.arg_frame.pack(side=TOP, expand=YES, fill=X)
        self.set_next_arg_ann_to_delete()


    def start_list_args_mode(self):
        self.print_mode_msg('modo de listagem de argumentos')
        self.ann_frame.pack_forget()
        self.arg_frame.pack(side=TOP, expand=YES, fill=X)
        self.set_next_arg_ann_to_view()

    def stop_list_args_mode(self):
        self._print_quit_mode_msg('modo de listagem de argumentos')
        self.arg_frame.pack_forget()
        self.to_view_arg_ann = None
        self.load_event_args_ann_tags()
        
    def stop_delete_arg_mode(self):
        self._print_quit_mode_msg('modo de exclusão de argumentos')
        self.arg_frame.pack_forget()
        self.to_delete_arg_ann = None
        self.load_event_args_ann_tags()
        

    def _set_step_arg_ann_to_delete(self, step_fn):
        if self.cur_event_ann and self.cur_event_ann.args_ann:
            args_ann = self.cur_event_ann.args_ann
            len_args = len(args_ann)
            if self.to_delete_arg_ann:
                try:
                    index = args_ann.index(self.to_delete_arg_ann)
                except ValueError:
                    self.to_delete_arg_ann = args_ann[0]
                    return
                self.to_delete_arg_ann = args_ann[step_fn(index) % len_args]
            else:
                self.to_delete_arg_ann = args_ann[0]

            self.delete_all_args_ann_tags()
            self.load_arg_ann_tag(self.to_delete_arg_ann)
            self.set_fe_arg_ann_label(self.to_delete_arg_ann)
        else:
            self.set_delete_arg_mode(False)

    def set_next_arg_ann_to_delete(self):
        self._set_step_arg_ann_to_delete(lambda i: i+1)
        
    def set_previous_arg_ann_to_delete(self):
        self._set_step_arg_ann_to_delete(lambda i: i-1)


        

    def _set_step_arg_ann_to_view(self, step_fn):
        if self.cur_event_ann and self.cur_event_ann.args_ann:
            args_ann = self.cur_event_ann.args_ann
            len_args = len(args_ann)
            if self.to_view_arg_ann:
                index = args_ann.index(self.to_view_arg_ann)
                self.to_view_arg_ann = args_ann[step_fn(index) % len_args]
            else:
                self.to_view_arg_ann = args_ann[0]

            self.delete_all_args_ann_tags()
            self.load_arg_ann_tag(self.to_view_arg_ann)
            self.set_fe_arg_ann_label(self.to_view_arg_ann)
        else:
            self.set_delete_arg_mode(False)

    def set_next_arg_ann_to_view(self):
        self._set_step_arg_ann_to_view(lambda i: i+1)

    def set_previous_arg_ann_to_view(self):
        self._set_step_arg_ann_to_view(lambda i: i-1)

    def show_cur_selected_fe_definition_dialog(self):
        output = self.fe_selection.get_radio_fe_and_color()
        if not output: return
        if output:
            fe, fe_color = output
        self.show_fe_definition_dialog(fe, fe_color)

    def show_cur_arg_fe_definition_dialog(self):
        if not self.to_view_arg_ann: return
        fe_id = self.to_view_arg_ann.event_fe_id
        fe_color = self.fe_selection.get_fe_color(fe_id)
        fe = self.fe_selection.get_arg_fe(fe_id)
        self.show_fe_definition_dialog(fe, fe_color)

    def show_fe_definition_dialog(self, fe, fe_color):
        win = Toplevel()
        win.title(fe.name)
        msg = Message(win, text=fe.definition)
        msg.config(bg=fe_color, font=('times', 16, 'italic'))
        msg.pack(fill=X, expand=YES)

        win.update()
        x_left = int(self.winfo_screenwidth()/2 - win.winfo_width()/2)
        y_top = int(self.winfo_screenheight()/2 - win.winfo_height()/2)
        
        win.geometry("+{}+{}".format(x_left, y_top))
         
        win.bind('<KeyPress-q>', lambda e: Frame.destroy(win))
        win.focus_set()
        win.grab_set()
        win.wait_window()

                          
            
    def ask_delete_cur_arg(self, to_delete_arg_ann=None):
        ans = askquestion('Pergunta', 'Você confirma a remoção do argumento?', parent=self)
        if ans == 'yes':
            if not to_delete_arg_ann:
               to_delete_arg_ann = self.to_delete_arg_ann
            self.arg_ann_remove_handler(to_delete_arg_ann)
            self.load_event_args_ann_tags()
            self.set_delete_arg_mode(False)
            self.stop_delete_arg_mode()


    def show_main_helper_dialog(self):
        help_msg = """
        t : próximo evento da sentença \n\n
        a : anotar argumento com o texto selecionado e tipo de FE atual \n\n
        i : visualizar informações do tipo/frame do evento atual \n\n
        h : visualizar atalhos do teclado para o modo atual\n\n
        q : fechar janela de anotação da sentença\n\n
        Ctrl-a : mover cursor para o início da sentença\n\n
        Ctrl-e : mover cursor para o fim da sentença\n\n
        Ctrl-f : mover cursor um caracter para frente
        Ctrl-b : mover cursor um caracter para trás
        Ctrl-s : inicia o modo de pesquisa de frame por nome\n\n
        Ctrl-Space : inicia modo de seleção de texto via movimento do cursor\n\n
        Ctrl-l a : inicia listagem de argumentos anotados \n\n
        Ctrl-d a : inicia modo de exclusão de argumentos \n\n
        Ctrl-d t : remove anotação do evento atual \n\n
        Ctrl-t s : inicia modo de seleção de tipo/frame na lista de sugestões \n\n
        Ctrl-t a : inicia modo de seleção de tipo/frame na lista de todos os frames \n\n
        Alt-e : inicia modo de seleção de FEs não anotados \n\n
        Alt-a : inicia modo de seleção de FEs já anotado \n\n
        Alt-f : mover cursor uma palavra para frente\n\n
        Alt-b : mover cursor uma palavra para trás\n\n
        """
        show_text_dialog(self, 'Ajuda', help_msg, font=('times', 14))


    def show_search_mode_helper_dialog(self):
        help_msg = """
        Ctrl-h : visualizar lista de combinações de teclas de atalho\n\n 
        Ctrl-g : sair do modo de busca de frames\n\n
        Ctrl-n : selecionar próximo frame da lista de resultados\n\n
        Ctrl-p : selecionar frame anterior da lista de resultados\n\n
        Ctrl-i : visualizar informações do frame selecionado\n\n
        enter : selecionar o frame como tipo do evento atual\n\n
        """
        show_text_dialog(self, 'Ajuda - modo de busca', help_msg, font=('times', 14))


    def show_list_args_mode_helper_dialog(self):
        help_msg = """
        n : seleciona próximo argumento anotado\n\n
        p : seleciona argumento anterior anotado\n\n
        g : sair do modo de listagem de argumentos anotados\n\n
        i : visualizar definição do tipo de FE do argumento selecionado\n\n
        h : visualizar lista de teclas de atalho\n\n
        """
        show_text_dialog(self, 'Ajuda - modo listagem de argumentos', help_msg, font=('times', 14))


    def show_fes_selection_mode_helper_dialog(self):
        help_msg = """
        g : sair do modo de seleção do tipo/FE do argumento\n\n
        n : selecionar próximo FE da lista\n\n
        p : selecionar FE anterior da lista \n\n
        i : visualizar definição do FE atual\n\n
        h : visualizar lista de teclas de atalho\n\n
        """
        show_text_dialog(self, 'Ajuda - modo seleção de FEs', help_msg, font=('times', 14))


    def show_delete_args_mode_helper_dialog(self):
        help_msg = """
        g : sair do modo de exclusão de argumento\n\n
        n : seleciona próximo argumento anotado\n\n
        p : seleciona argumento anterior anotado\n\n
        h : visualizar lista de teclas de atalho\n\n
        enter : exclui argumento atual\n\n
            """
        show_text_dialog(self, 'Ajuda - modo exclusão de argumento', help_msg, font=('times', 14))


    def show_frame_selection_mode_helper_dialog(self):
        help_msg = """
        g : sair do modo de seleção de tipo/frame de evento\n\n
        n : selecionar próximo frame da lista\n\n
        p : seleciona frame anterior da lista\n\n
        h : visualizar lista de teclas de atalho\n\n
        enter : selecionar frame como o tipo do evento atual\n\n 
        """
        show_text_dialog(self, 'Ajuda - modo seleção tipo/frame de evento', help_msg, font=('times', 14))

    def show_text_selection_mode_helper_dialog(self):
        help_msg = """
        a : anotar seleção de texto com o tipo atual\n\n
        g : sair do modo de seleção de texto\n\n
        h : visualizar lista de teclas de atalho\n\n
        Ctrl-a : mover cursor para o início da sentença\n\n
        Ctrl-e : mover cursor para o fim da sentença\n\n
        Ctrl-f : mover cursor um caracter para frente\n\n
        Ctrl-b : mover cursor um caracter para trás\n\n
        Alt-f : mover cursor uma palavra para frente\n\n
        Alt-b : mover cursor uma palavra para trás\n\n
        Alt-a : seleciona próximo tipo de FE na lista de argumentos\n\n
        Alt-e : seleciona próximo tipo de FE na lista de não anotados\n\n
        """
        show_text_dialog(self, 'Ajuda - modo de seleção de texto', help_msg, font=('times', 14))
        
    # def ask_delete_cur_event_type(self):
    #     ans = askquestion('Pergunta', 'Você confirma a remoção do tipo do evento?', parent=self)
    #     if ans == 'yes':
    #         self.frame_selection.remove_event_type_handler()
    #     self.set_delete_event_type_mode(False)

    # def ask_change_cur_event_type(self):
    #     if self.cur_event_ann:
    #         ans = askquestion('Pergunta', 'Você confirma a mudança do tipo do evento?', parent=self)
    #         if ans == 'yes':
                
    #             self.frame_selection.clear_search_frame()
    #             self.set_search_mode(False)
    #     else:
    #         self.frame_selection.select_event_type()
    #         self.frame_selection.clear_search_frame()
            
            
    def event_val_handler(self, val_event_ann):
        if self.cur_event_ann:
            val_event_ann.event_ann_id = self.cur_event_ann.id
            val_event_ann.annotator_id = self.options['annotator_id']
            _thread.start_new_thread(fnutils.save_val_event, (val_event_ann,))


    def arg_val_handler(self, val_arg_ann):
        if self.cur_event_ann:
            val_arg_ann.event_ann_id = self.cur_event_ann.id
            val_arg_ann.annotator_id = self.options['annotator_id']
            _thread.start_new_thread(fnutils.save_val_arg, (val_arg_ann,))





    def delete_arg_ann_tag(self, arg_ann):
        tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
        self.sentence_text_view.tag_delete(tag_name,'1.0', END)
        print('delete tag')

    def delete_all_args_ann_tags(self):
        if self.cur_event_ann:
            for arg_ann in self.cur_event_ann.args_ann:
                self.delete_arg_ann_tag(arg_ann)
    
    def event_type_selection_handler(self, event, event_ann, frame):
        self.delete_all_args_ann_tags()
            #if event_ann and self.cur_event_ann.event_fn_id != event_ann.event_fn_id:
            #    event_ann.args_ann = []
            #    print('set empty list')

        self.cur_event_ann = event_ann
        if event_ann and frame:
            print('Frame name: %s \n event_id: %s \n event_args %s' % (frame.name, event_ann.event_id, event_ann.args_ann))
            #self.fe_selection.set_args_ann(event_ann.args_ann)
            self.fe_selection.update_fes()
            self.fe_selection.set_args_ann_fes(fnutils.get_fes_from_args(event_ann, event_ann.args_ann), event_ann.args_ann , self.sentence.text)#get_args_ann_fes(event_ann.id, self.options['annotator_id']))
            self.fe_selection.set_all_fes(fnutils.frame_fes(frame))
            #self.fe_selection.set_core_fes(fnutils.filter_core_fes(frame))
            #self.fe_selection.set_peripheral_fes(fnutils.filter_peripheral_fes(frame))
            #_thread.start_new_thread(self.load_val_ann, (self.options['annotator_id'], event_ann.id)) 
        else:
            self.fe_selection.update_fes()
        self.highlight_event(event)
        self.load_event_args_ann_tags()
        self.set_fe_arg_label()
        _thread.start_new_thread(self.save_events_ann, ())


    def save_events_ann(self):
        for event_ann in self.events_ann:
            event_ann.annotator_id = self.options['annotator_id']
            for arg_ann in event_ann.args_ann:
                arg_ann.annotator_id = self.options['annotator_id']
            fnutils.save_event_ann(event_ann)

    def event_ann_type_remove_handler(self, event_ann):
        self.fe_selection.update_fes()
        if event_ann:
            for arg_ann in event_ann.args_ann:
                tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, event_ann.id, arg_ann.start_at, arg_ann.end_at)
                self.sentence_text_view.tag_delete(tag_name,'1.0', END)
                print('delete tag')
        self.cur_event_ann = None

    def arg_ann_remove_handler(self, arg_ann):
        if self.cur_event_ann and arg_ann:
            tag_name = '%s-%s-%s:%s' % (arg_ann.event_fe_id, self.cur_event_ann.id, arg_ann.start_at, arg_ann.end_at)
            self.sentence_text_view.tag_delete(tag_name,'1.0', END)
            self.cur_event_ann.args_ann.remove(arg_ann)
            fnutils.delete_arg_ann(arg_ann)
            self._update_fes_selections(self.cur_event_ann)
        
    def _update_fes_selections(self, event_ann):
        frame = fnutils.frame_by_id(event_ann.event_fn_id)
        if event_ann and frame:
            print('update_fes_selection frame id: %s' % frame.ID)
            self.fe_selection.update_selections()
            
            self.fe_selection.set_args_ann_fes(fnutils.get_fes_from_args(event_ann, event_ann.args_ann), event_ann.args_ann, self.sentence.text)
            self.fe_selection.set_all_fes(fnutils.frame_fes(frame))
            #self.fe_selection.set_core_fes(fnutils.filter_core_fes(frame))
            #self.fe_selection.set_peripheral_fes(fnutils.filter_peripheral_fes(frame))

        
    def update_sentence_text(self):
        try:
            self.sentence = self.sentence_queue.get(block=False)
            events = self.events_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.sentence_text_view.delete('1.0', END)
            self.sentence_text_view.insert('1.0', self.sentence.text)
            print([e.trigger for e in events])
            self.frame_selection.set_events(events)
            self.frame_selection.set_events_ann(self.events_ann)
        self.after(10, self.update_sentence_text)


    def load_val_ann(self, annotator_id, event_ann_id):
        val_event = fnutils.query_val_event(event_ann_id, annotator_id)
        val_args = fnutils.query_val_args(event_ann_id, annotator_id)
        self.vals_queue.put((val_event, val_args))
        
        
    def update_val_ann(self):
        try:
            val_event, vals_args = self.vals_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.frame_selection.set_val_event(val_event)
            self.fe_selection.set_val_args(vals_args)
        self.after(10, self.update_val_ann)
            

if __name__ == '__main__':
    options = {'annotator_id': 'anderson@gmail.com',
               'sentence_id': '6c8c7963-eaae-48bb-9e6e-b75828078e95',
               'triggers': ['falar', 'transferir'],
               'suggestion': {'title': 'Sugestões'},
               'all':{'title': 'Todos' },
               'fes_colors': ['#85E314', '#33E4CF', '#F14EAA', '#F1D54A', '#E67D57', '#F3BCBC'],
               'fes': ['Local', 'Tempo', 'Atacante']}
    fnutils.create_session()
    SentenceAnnotation(options).mainloop()
