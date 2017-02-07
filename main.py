import tkinter as tk
from tkinter.filedialog import askopenfilename

import db_helper
import lf_tools
from components import attribute_frames
from components import dic_entry_bottom_control_panel
from components import dic_entry_main_container
from components import dic_entry_top_control_panel
from components import translation_frames
from const_definitions import colors
from lesson import lesson_editor
from state import STATUS
from vocabulary_design import vocabulary_external_editor_


class MainWindow(tk.Frame):
    index_to_update = []
    STATUS.cur_workingtable = db_helper.SUBST

    lesson_designer_is_displayed = False
    vocab_designed_is_displayed = False

    vocab_designer = None
    lesson_designer = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        if master is not None:
            master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self['width'] = self.winfo_screenwidth() * 2 / 3
        self['height'] = self.winfo_screenheight() * 2 / 3
        tk.Pack.config(self)
        self.set_menu()
        self.left_frame = tk.Frame(self,
                                   width=self['width'] / 2, height=self['height'],
                                   bg=colors.LIGHT_GREEN_BLUE)
        self.right_frame = tk.Frame(self, width=self['width'] / 2,
                                    height=self['height'],
                                    bg=colors.LIGHT_GREEN_BLUE)

        # dic containing the list found in db of each category:
        self.entry_list = {}
        self.check_var = {}
        self.dump_flag = 0  # temporary, need to be implemented

        self.frame_entry = None
        self.frame_attr_grid = None

        self.MENU_TOP_PANEL = dic_entry_top_control_panel.SelectWordTypePanel(self.left_frame, self)

        # Frame containing french word list
        self.ENTRIES_FRAME = dic_entry_main_container.EntryFrame(self.left_frame, self)
        self.TRANSLATION_FRAME = tk.Frame(self.right_frame)
        self.TRANSLATION_FRAME['bg'] = 'red'
        self.ATTRIBUTE_FRAME = attribute_frames.AttributeFrame(self.left_frame)
        self.BUTTONS_FRAME = tk.Frame(self.right_frame)

        self.btn_writeDB = tk.Button(self.BUTTONS_FRAME,
                                     text=lf_tools.menu_global.find('buttons').find('write_db').text,
                                     command=self.write_db)

        '''   OPEN DataBase  '''
        self.btn_open = tk.Button(self.BUTTONS_FRAME,
                                  text=lf_tools.menu_global.find('buttons').find('open_db').text,
                                  background="black", foreground="white",
                                  command=self.choose_open_db)

        self.btn_quit = tk.Button(self.BUTTONS_FRAME,
                                  text=lf_tools.menu_global.find('buttons').find('quit').text,
                                  background='red',
                                  height=3,
                                  command=self.on_closing)
        self.btn_open.pack(expand=True)
        self.btn_writeDB.pack(expand=True)
        self.btn_quit.pack(expand=True)

        self.ENTRY_EDIT_PANEL = dic_entry_bottom_control_panel.ControlPanel(self.left_frame, self)
        self.ENTRY_EDIT_PANEL['bg'] = 'red'

        self.init_entry_canvas()
        self.init_translation_frame()
        self.init_position()

        self.choose_open_db(lf_tools.resource_path("res/_inner/dic_librefra.db"))
        # STATUS.dbHelper.repair_sentences()
        # STATUS.dbHelper.import_sentences()
        # STATUS.dbHelper.import_phonetic()
        # STATUS.dbHelper.display_phonetic()
        # STATUS.dbHelper._update_info()
        # STATUS.dbHelper.clean_sentences_db()
        # STATUS.dbHelper.remove_sentences_without_translations()

    def write_db(self):
        if STATUS.dbHelper is not None:
            STATUS.dbHelper.commit()

    def set_menu(self):
        # create a toplevel menu
        menubar = tk.Menu(self)
        menubar.add_command(label=lf_tools.menu_global.find('buttons').
                            find('new_lesson').text, command=self.launch_lesson_editor)
        menubar.add_command(label=lf_tools.menu_global.find('buttons').
                            find('quit').text, command=self.on_closing)
        menubar.add_command(label=lf_tools.menu_global.find('buttons').find('create_voc_list').text,
                            command=self.on_create_vocabulary_list)

        # display the menu
        root.config(menu=menubar)

    def on_create_vocabulary_list(self):
        if self.vocab_designed_is_displayed is True:
            return
        self.vocab_designed_is_displayed = True
        new_root = tk.Tk()
        width = 1200
        height = 500
        x = (new_root.winfo_screenwidth() // 2) - (width // 2)
        y = (new_root.winfo_screenheight() // 2) - (height // 2)
        new_root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        new_root.config(bd=1)
        new_root.title(lf_tools.menu_lesson.find('title').text)
        self.vocab_designer = vocabulary_external_editor_.VocabularyListEditor(new_root, self)

    def launch_lesson_editor(self):
        if self.lesson_designer_is_displayed is True:
            return
        self.lesson_designer_is_displayed = True
        new_root = tk.Tk()
        new_root.minsize(700, 500)
        width = 1200
        height = 500
        x = (new_root.winfo_screenwidth() // 2) - (width // 2)
        y = (new_root.winfo_screenheight() // 2) - (height // 2)
        new_root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        new_root.config(bd=1)
        new_root.title(lf_tools.menu_lesson.find('title').text)
        self.lesson_designer = lesson_editor.LessonFrame(new_root, self)

    def on_closing(self):
        if STATUS.dbHelper is not None:
            STATUS.dbHelper.close()
        if self.vocab_designer is not None:
            try:
                self.vocab_designer.destroy()
            except:
                print('vocab is already destoyed')
        if self.lesson_designer is not None:
            self.lesson_designer.destroy()
        self.destroy()
        self.quit()

    def init_entry_canvas(self):
        self.ENTRIES_FRAME.init_canvases()

    def get_search_text(self):
        return self.strVar_entry_searched.get()

    def init_translation_frame(self):
        STATUS.translationFrame = translation_frames. \
            TranslationMainContainer(self.TRANSLATION_FRAME, self)
        self.TRANSLATION_FRAME['width'] = '3i'
        self.TRANSLATION_FRAME['height'] = '4i'

    def fill_attributes(self, list, which_table):
        if which_table == "subst":
            tmp1 = list[1]
            tmp2 = list[0]
            if tmp1 is None:
                tmp1 = "None"
            if tmp2 is None:
                tmp2 = 10
            self.word_deu.insert(tk.END, tmp1)
            self.genre_deu.insert(tk.END, str(tmp2))

    def new_state_checkbox(self):
        pass

    def verbflag_change_state_combobox(self, event):
        tmpvalue = int(STATUS.currentSelectedFrame.nametowidget('type').
                       get(), 16)
        t = STATUS.currentSelectedFrame.nametowidget('type')
        tmpvalue &= ~lf_tools.V.MASK[event.widget._name]
        tmpvalue |= lf_tools.V.get_flag_int(event.widget.get(),
                                            event.widget._name)
        t.delete(0, tk.END)
        t.insert(0, hex(tmpvalue))

    def show_attributes(self):
        print('Current workingtable : ' + str(STATUS.cur_workingtable))
        if STATUS.cur_workingtable == db_helper.SUBST:
            self.ATTRIBUTE_FRAME.display(lf_tools.SUBST)

            # content_setter.subst_global_attributes(self)
        elif STATUS.cur_workingtable == db_helper.VERB:
            self.ATTRIBUTE_FRAME.display(lf_tools.VERB)
        self.ATTRIBUTE_FRAME.update()
        # content_setter.verb_global_attributes(self)
        # content_setter.verb_pattern_attributes(self.attributes_1)

    def _on_wheel_down_attr(self, event):
        self.attr_canvas.yview_scroll(5, "units")

    def _on_wheel_up_attr(self, event):
        self.attr_canvas.yview_scroll(-5, "units")

    def choose_open_db(self, str_default=None):
        fn = str_default
        if str_default is None:
            fn = askopenfilename(initialdir="./res")
        STATUS.dbHelper = db_helper.LF_SQLiteHelper(fn)
        # STATUS.dbHelper._clean_table_zh()
        print('[entered choose_open_db]')
        if STATUS.translationFrame is None:
            self.init_translation_frame()
        if str_default is None:
            STATUS.cur_workingtable = db_helper.SUBST
            self.set_content_subst('', False)
            self.ATTRIBUTE_FRAME.display(STATUS.cur_workingtable)

    def button_color_update(self, selected_btn):
        for k, v in self.MENU_TOP_PANEL.get_buttons_map().items():
            if k == selected_btn:
                v.config(bg=colors.BUTTON_SELECTED)
            else:
                v.config(bg=colors.BUTTON_NOT_SELECTED)

    '''Set the verb table'''

    def callback_display_verb(self):
        self.button_color_update('verb')
        STATUS.cur_workingtable = db_helper.VERB
        self.set_content_verb('', False)
        self.ATTRIBUTE_FRAME.display(lf_tools.VERB)

    def set_content_verb(self, str_to_search=None, processSearch=True):
        self.ENTRIES_FRAME.switch_table(db_helper.VERB)
        if processSearch is True:
            self.ENTRIES_FRAME.set_verb_table(STATUS.dbHelper, str_to_search)
            # self.propagate_binding(self.list_entry_canvas)

    '''Set the verb table'''

    def callback_display_other(self):
        self.button_color_update('other')
        STATUS.cur_workingtable = db_helper.OTHER
        self.set_content_other('', False)
        self.ATTRIBUTE_FRAME.display(lf_tools.OTHER)

    def set_content_other(self, str_to_search=None, processSearch=True):
        self.ENTRIES_FRAME.switch_table(db_helper.OTHER)
        if processSearch is True:
            self.ENTRIES_FRAME.set_other_table(STATUS.dbHelper, str_to_search)
            # self.propagate_binding(self.list_entry_canvas)

    def callback_reset_lesson(self):
        self.lesson_designer_is_displayed = False
        self.lesson_designer = None

    def callback_reset_vocab(self):
        self.vocab_designed_is_displayed = False
        self.vocab_designer = None

    ''' Set the subst table'''

    def callback_display_subst(self):
        self.button_color_update('noun')
        STATUS.cur_workingtable = db_helper.SUBST
        self.set_content_subst('', False)
        self.ATTRIBUTE_FRAME.display(lf_tools.SUBST)

    def set_content(self, db_table_code,
                    str_to_search=None, process_search=True):
        if db_table_code == db_helper.SUBST:
            self.set_content_subst(str_to_search, process_search)
        elif db_table_code == db_helper.VERB:
            self.set_content_verb(str_to_search, process_search)
        elif db_table_code == db_helper.OTHER:
            self.set_content_other(str_to_search, process_search)

    def set_content_subst(self, str_to_search=None, process_search=True):
        self.ENTRIES_FRAME.switch_table(db_helper.SUBST)
        if process_search:
            self.ENTRIES_FRAME.set_subst_table(STATUS.dbHelper, str_to_search)

    def on_search(self, str_to_search):
        """
        Triggered when a word is searched in top entry panel
        :param str_to_search:
        :return:
        """
        if STATUS.cur_workingtable is db_helper.SUBST:
            self.set_content_subst(str_to_search)
        elif STATUS.cur_workingtable is db_helper.VERB:
            self.set_content_verb(str_to_search)
        elif STATUS.cur_workingtable is db_helper.OTHER:
            self.set_content_other(str_to_search)
        self.ATTRIBUTE_FRAME.display(STATUS.cur_workingtable)

    def init_position(self):
        self.pack(fill=tk.BOTH, expand=True)
        # for widget in self.winfo_children():
        #    widget.place_forget()
        self.left_frame.place(relx=0.0, rely=0.0, relw=0.5, relh=1.0)
        self.right_frame.place(relx=0.5, rely=0.0, relw=0.5, relh=1.0)
        # for left_widget in self.left_frame.winfo_children():
        #    left_widget.place_forget()
        # for righ_widget in self.right_frame.winfo_children():
        #    righ_widget.place_forget()
        # in left_frame:
        self.MENU_TOP_PANEL.place(relx=0.0, rely=0.0, relw=1.0, relh=0.1)
        self.ENTRIES_FRAME.place(relx=0.0, rely=0.1, relw=1.0, relh=0.5)
        self.ENTRY_EDIT_PANEL.place(relx=0.0, rely=0.6, relw=1.0, relh=0.1)
        self.ATTRIBUTE_FRAME.place(relx=0.0, rely=0.7, relw=1.0, relh=0.3)
        # in right frame:
        self.TRANSLATION_FRAME.place(relx=0.0, rely=0.0, relw=1.0, relh=0.7)
        self.BUTTONS_FRAME.place(relx=0.0, rely=0.7, relw=1.0, relh=0.2)


root = tk.Tk()
test = MainWindow(root)
root.title('LibreFra_DBTool')
test.mainloop()
