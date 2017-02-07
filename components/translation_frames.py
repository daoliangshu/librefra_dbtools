import tkinter as tk
from tkinter import *
from tkinter import font

import db_helper
import lf_tools
from const_definitions import colors
from state import STATUS


class TranslationMainContainer(Frame):
    def __init__(self, master, root):
        Frame.__init__(self, master)
        tk.Pack.config(self, fill=tk.BOTH, expand=True)
        self.root = root
        self.frame_unit_height = 40
        upper_frame = Frame(self)
        upper_frame['bg'] = colors.LIGHT_PURPLE
        sub_frame = Frame(upper_frame)
        sub_frame['bg'] = colors.LIGHT_GREEN
        lbl = Label(sub_frame,
                    text=lf_tools.menu_global.find('labels').find('translation').text)
        lbl.place(relx=0.1, rely=0.1, relw=0.8, relh=0.8)

        sub_f = Frame(upper_frame)
        sub_f['height'] = '1i'
        sub_f['width'] = '2i'
        sub_f.grid(row=1, column=0, sticky=N + W + N + S)
        self.lb_selected_word = Label(sub_f, text='Nontext',
                                      relief=SUNKEN)
        self.lb_selected_word.place(relx=0.1, rely=0.1, relw=1.0, relh=0.8)

        sub_frame.grid(row=0, column=0)
        upper_frame.grid_columnconfigure(0, weight=3)
        self.strVar_transId = []
        self.strVar_transText = []
        self.strVar_transAnotate = []
        upper_frame.grid_rowconfigure(0, weight=1)
        upper_frame.grid_rowconfigure(1, weight=1)
        upper_frame.grid_rowconfigure(2, weight=1)

        '''Init upper frame showing:
                -translation words assigned to the current selected french word
                -translation ids corresponding to them
        '''
        for index in range(1, 4):
            sub_frame = Frame(upper_frame)
            sub_frame_bottom = Frame(upper_frame)
            sub_frame_annotate = Frame(upper_frame)
            sub_frame['bg'] = colors.TRANS_IDLE_BG
            sub_frame['height'] = '1i'
            sub_frame['width'] = '2i'
            sub_frame_bottom['height'] = '1i'
            sub_frame_bottom['width'] = '2i'
            sub_frame_annotate['height'] = '1i'
            sub_frame_annotate['width'] = '2i'
            # Annotation
            self.strVar_transAnotate.append(StringVar(upper_frame,
                                                      value=lf_tools.menu_global.find('labels').
                                                      find('empty').text))
            lb_anotate = Label(sub_frame_annotate,
                               text=lf_tools.menu_global.find('labels').find('info').text)
            e_anotate = Entry(sub_frame_annotate, textvariable=self.strVar_transAnotate[index - 1])
            lb_anotate.place(relx=0, rely=0, relw=0.2, relh=1)
            e_anotate.place(relx=0.2, rely=0, relw=0.8, relh=1)
            e_anotate.bind("<KeyRelease>", self.on_annotate)

            # add/remove tid buttons
            btn_addtid = Button(sub_frame)
            btn_addtid.id = 'transid_' + str(index - 1)
            btn_addtid.index = (index - 1)
            btn_addtid.bind("<Button-1>", self.on_add_tid)
            btn_remove_tid = Button(sub_frame)
            btn_remove_tid.id = 'transid_' + str(index - 1)
            btn_remove_tid.index = (index - 1)
            btn_remove_tid.bind("<Button-1>", self.on_remove_tid)
            strVar = StringVar(sub_frame)
            strVarText = StringVar(sub_frame_bottom)
            strVar.set('(null' + str(index) + ')')
            strVarText.set('Pas_de_traduction')
            self.strVar_transId.append(strVar)
            self.strVar_transText.append(strVarText)
            e_show_tid = Entry(sub_frame,
                               textvariable=strVar,
                               state='disable')
            e_show_tid.index = index - 1
            e_show_tid.bind('<Button-1>', self._on_trans_clicked)

            # Displaying selected trans_word here:
            label_display_translations = Label(sub_frame_bottom,
                                               textvariable=strVarText,
                                               anchor=NW,
                                               justify=CENTER,

                                               wraplength='5i')
            label_display_translations.index = index - 1
            label_display_translations.bind('<Button-1>', self._on_trans_clicked)
            f = font.Font(font=label_display_translations['font'])
            # print((f.actual()))
            f['size'] = int(f['size'] * (4 / 3))
            label_display_translations['font'] = f
            label_display_translations.place(relx=0.01, rely=0.01, relw=0.98, relh=0.98)
            btn_addtid.place(relx=0.0, rely=0.0, relw=0.2, relh=0.7)
            btn_remove_tid.place(relx=0.0, rely=0.73, relw=0.2, relh=0.25)
            e_show_tid.place(relx=0.23, rely=0.25, relw=0.7, relh=0.5)
            sub_frame_bottom['bg'] = '#000011'
            sub_frame_bottom.grid(row=0,
                                  column=index * 2,
                                  columnspan=2)

            sub_frame['bg'] = '#FF0000'
            sub_frame.grid(row=1, column=index * 2, columnspan=2)
            sub_frame_annotate.grid(row=2, column=index * 2, columnspan=2)
            upper_frame.grid_columnconfigure(index * 2, weight=1)
            upper_frame.grid_columnconfigure(index * 2 + 1, weight=1)
        self.canvas = None
        upper_frame.place(relx=0.0, rely=0.0, relw=1.0, relh=0.2)

        '''middle frame, where are displayed chinese entries'''
        self.middle_frame = tk.Frame(self)
        self.middle_frame.place(relx=0.0, rely=0.2, relw=1.0, relh=0.6)
        self.init_translation_canvas()

        bottom_frame = tk.Frame(self)
        search_translation_frame = tk.Frame(bottom_frame)
        add_translation_frame = tk.Frame(bottom_frame)
        search_translation_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        add_translation_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        label_search_translation = tk.Label(search_translation_frame,
                                            text=lf_tools.menu_global.find('labels').find('search').text)
        self.strVar_search = StringVar(bottom_frame)
        self.strVar_search.set('')
        entry_search_translation = tk.Entry(search_translation_frame, textvariable=self.strVar_search)
        button_launch_search = tk.Button(search_translation_frame,
                                         text=lf_tools.menu_global.find('buttons').find('launch').text)

        label_search_translation.pack(side=tk.LEFT)
        entry_search_translation.pack(side=tk.LEFT, fill=X, expand=TRUE)
        entry_search_translation.id = 'btn_search'
        entry_search_translation.bind('<Return>', self.on_click)
        button_launch_search.id = 'btn_search'
        button_launch_search.bind('<Button-1>', self.on_click)
        button_launch_search.pack(side=tk.LEFT, expand=True)

        label_add_trans = tk.Label(add_translation_frame,
                                   text=lf_tools.menu_global.find('labels').find('add').text)
        label_add_trans.pack(side=tk.LEFT, fill=tk.Y)
        self.var_add_trans = tk.StringVar(bottom_frame)
        self.entry_add_trans = tk.Entry(add_translation_frame,
                                        textvariable=self.var_add_trans)
        self.entry_add_trans.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_add_trans.bind('<Return>', self.__on_add_entry)
        self.cur_selected_translation = None
        bottom_frame.place(relx=0.0, rely=0.8, relw=1.0, relh=0.2)

    def on_annotate(self, event):
        tmp = ''
        count = 0
        for i in range(0, 3):
            if count > 0:
                tmp += ';'
            if self.strVar_transAnotate[i].get() is None or \
                            self.strVar_transAnotate[i].get() == 'None':
                tmp += ''
            else:
                tmp += self.strVar_transAnotate[i].get()
            count += 1
        STATUS.currentSelectedFrame[STATUS.cur_workingtable].set_info(tmp)

    def set_info(self, info_str):
        if info_str is not None and info_str != '':
            tmp = info_str.split(';')
            count = 0
            for b in tmp:
                if b != 'None':
                    self.strVar_transAnotate[count].set(b)
                else:
                    self.strVar_transAnotate[count].set('')
                count += 1
            if count != 3:
                print('<set_info:info count error> : ' + str(info_str))
        else:
            for i in range(0, 3):
                self.strVar_transAnotate[i].set('')

    def on_click(self, event):
        if event.widget.id == 'btn_search':
            self.set_translation_canvas(STATUS.dbHelper, self.get_search_text())

    def set_selected_word(self, sel_word):
        self.lb_selected_word['text'] = sel_word

    def get_search_text(self):
        return self.strVar_search.get()

    def init_translation_canvas(self):
        for ch in self.middle_frame.winfo_children():
            ch.destroy()
        canvas_container = tk.Frame(self.middle_frame, bg=colors.LIGHT_YELLOW)
        canvas_container.bind('<Configure>', self._on_resize)
        scroll_container = tk.Frame(self.middle_frame, bg=colors.CHOICE_CORRECT)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, anchor=tk.NW)
        scroll_container.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.NE)
        self.canvas = tk.Canvas(canvas_container,
                                background="black")
        # self.canvas.scrollX = tk.Scrollbar(scroll_container, orient=tk.HORIZONTAL)
        self.canvas.scrollY = tk.Scrollbar(scroll_container,
                                           orient=tk.VERTICAL,
                                           bg=colors.LIGHT_GREEN)
        self.canvas['yscrollcommand'] = self.canvas.scrollY.set
        self.canvas.scrollY['command'] = self.canvas.yview
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.scrollY.pack(side=tk.LEFT, fill=tk.BOTH)
        self.canvas.bind_all("<Button-4>", self.__on_wheel_up)
        self.canvas.bind_all("<Button-5>", self.__on_wheel_down)

    def get_canvas(self):
        return self.canvas

    def get_selected_trans(self):
        return self.cur_selected_translation

    def set_selected_trans(self, new_selection):
        self.cur_selected_translation = new_selection

    def set_tid(self, order, tid_coma_list, back_step=False):
        if 0 > order > 3:
            return
        self.strVar_transId[order].set(tid_coma_list)
        tmp_trans = ''
        if tid_coma_list is None or tid_coma_list == '':
            self.strVar_transText[order].set('')
            if back_step is True:
                STATUS.currentSelectedFrame[STATUS.cur_workingtable]. \
                    set_tid(order, tmp_trans)
            return
        tids_as_array = str(tid_coma_list).split(',')

        for fetched_tid in tids_as_array:
            fetched_trans = STATUS.dbHelper.get_translation_by_id(fetched_tid)
            if fetched_trans is not None and fetched_trans != "":
                if tmp_trans == '' or tmp_trans is None:
                    tmp_trans = fetched_trans
                else:
                    tmp_trans += ',' + fetched_trans
        # Display translations, separated by comma for a given cell ( 0 to 2)
        self.strVar_transText[order].set(tmp_trans)
        if back_step is True:
            STATUS.currentSelectedFrame[STATUS.cur_workingtable].set_tid(order, tid_coma_list)

    def add_tid(self, order, tid):
        """
        Add a tid to a cell in the selected world.
        Choose a cell from 0 to 2.
        :param order: index of the trans cell ( a cell represents a meaning of the word
        :param tid: translation id to associate with the trans cell of the world
        :return: None
        """
        if 0 > order > 3 or tid is None or int(tid) < 0:
            return
        if self.__check_tid_exists(order, tid) is False:
            tids = self.get_tid(order)
            if tids is not None and tids != 'None' and tids != '':
                tids += ',' + str(tid)
            else:
                tids = str(tid)
            self.set_tid(order, tids)

    def __check_tid_exists(self, order, tid):
        if 0 > order > 3:
            return True
        tids = self.strVar_transId[order].get()
        if tids is None or tids == '':
            return False
        tids_arr = tids.split(',')
        for t in tids_arr:
            if t == tid:
                return True
        return False

    def _on_trans_clicked(self, event):
        """
        Triggered when user click on translation. It search for pattern
        And set display translations accordingly
        Ignore if clicked trans is empty
        :param event: tid or trans from tid widget
        :return:
        """
        trans = self.strVar_transText[event.widget.index].get()
        if trans is not None and trans != '':
            self.set_translation_canvas(STATUS.dbHelper, trans)

    def set_translation_canvas(self, dbhelper, str_to_search=None):
        """
        Retrieves translations from the table_zh according to provided patter ( all if is None)
        Then displays them.
        :param dbhelper:
        :param str_to_search:  pattern to search
        :return:
        """
        cnt = 0
        self.init_translation_canvas()
        self.canvas.delete('all')
        for row in dbhelper.get_entries_it(db_helper.TRANS_ZH,
                                           str_to_search):
            frame_unit = TransFrameUnit(self.canvas,
                                        self,
                                        self.canvas['width'],
                                        self.frame_unit_height)
            ''' in order : _id, word, subst_trans_id, verb_trans_id '''
            frame_unit.set_tid_as_str(str(row['_id']))
            frame_unit.get_comp_by_name("_id"). \
                configure(activebackground="#33B5E5", relief=RAISED)
            frame_unit.set_trans_name(lf_tools.set_word(row['word']))
            frame_unit.set_wids(db_helper.SUBST, row['subst_trans_id'])
            frame_unit.set_wids(db_helper.VERB, row['verb_trans_id'])
            frame_unit.set_wids(db_helper.OTHER, row['other_trans_id'])
            frame_unit.config(cursor="dot", highlightbackground="red",
                              highlightcolor="black")
            self.canvas.create_window((0, cnt), anchor=NW, window=frame_unit)
            cnt += self.frame_unit_height
        print(self.canvas['width'])
        self.canvas['scrollregion'] = self.canvas.bbox('all')

    def get_tid(self, order):
        """
        Retrieves tid at ith bucket ( 0 to 2) of the current selected word
        :param order:
        :return: tid as str, or None if index error
        """
        if 0 <= order < 3:
            return self.strVar_transId[order].get()
        else:
            return None

    def on_add_tid(self, event):
        """
            This method is called when a new tid is set to to specific wid (word id)
        :param event:
        :return:
        """
        if self.cur_selected_translation is not None:
            self.add_tid(event.widget.index, self.cur_selected_translation.get_id_as_text())
            STATUS.currentSelectedFrame[STATUS.cur_workingtable]. \
                set_tid(event.widget.index,
                        self.get_tid(event.widget.index),
                        True)
            STATUS.currentSelectedFrame[STATUS.cur_workingtable].write_in_db()
            self.cur_selected_translation.add_id(STATUS.
                                                 currentSelectedFrame[STATUS.cur_workingtable].get_id_as_text())
            STATUS.dbHelper.update_translation_by_id(STATUS.cur_workingtable,
                                                     self.cur_selected_translation.get_id_as_text(),
                                                     self.cur_selected_translation.get_wids(STATUS.cur_workingtable))

    def on_remove_tid(self, event):
        """
            (1)Remove last entered tid for the specified word
            Check current tid associated, and extract the tid to remove
            Then call remove_tid
        :param event:
        :return:
        """
        if STATUS.currentSelectedFrame[STATUS.cur_workingtable] is None:
            return
        id_to_remove = ''
        ids = self.get_tid(event.widget.index)
        ids_array = ids.split(',')
        # Remove word_id in the trans entry :
        self.remove_tid(event.widget.index, ids_array[len(ids_array) - 1])

    def remove_tid(self, order, tid_to_remove):
        try:
            tids = self.get_tid(order).split(',')
            tmp = ''
            count = 0
            for s in tids:
                if s == tid_to_remove:
                    continue
                if count != 0:
                    tmp += ','
                tmp += s
                count += 1
            self.set_tid(order, tmp, True)
            ''' Reverse remove:Only if the french word does NOT have the given trans_id in ANY of
                of its trans_id_list
                Exp: A tid can be added one time in any of the trans id list. Each trans id list
                    represents a meaning for the word, that is, if a trans can represents two meaning
                    of a given word, its trans id can appear more than once.
                    When removing, a tid, it should then check whether the tid is still present
                    for another meaning of the word.
                Res: If the TID does not appear anymore -> reverse_remove:
                        Remove the word_id from the wid list associated to the translation.
            '''
            if self.__check_tid_exists_in_any(tid_to_remove) is False:
                self.remove_wid(tid_to_remove,
                                STATUS.currentSelectedFrame[STATUS.cur_workingtable].get_id(),
                                STATUS.cur_workingtable)
            STATUS.currentSelectedFrame[STATUS.cur_workingtable].remove_tid(order, tid_to_remove)
        except:
            return

    def __check_tid_exists_in_any(self, tid):
        for order in range(0, 3):
            tids = self.strVar_transId[order].get()
            if tids is None or tids == '':
                return False
            tids_arr = tids.split(',')
            for t in tids_arr:
                if t == tid:
                    return True
        return False

    def remove_wid(self, tid, wid_to_remove, db_table_code):
        word_ids = STATUS.dbHelper.get_translation_by_id(tid, db_table_code)
        new_wid = ''
        if tid is None or tid == '':
            return
        if word_ids is None or word_ids == '':
            STATUS.dbHelper.update_translation_by_id(db_table_code, tid, new_wid)
            if self.cur_selected_translation.get_id_as_text() == tid:
                self.cur_selected_translation.set_tid(db_table_code, new_wid)
            return
        wid_array = word_ids.split(',')
        new_wid = ''
        if wid_array is not None:
            count = 0
            for s in wid_array:
                if s == str(wid_to_remove) or s == '-1':
                    continue
                if count != 0:
                    new_wid += ','
                new_wid += s
                count += 1
            STATUS.dbHelper.update_translation_by_id(db_table_code, tid, new_wid)
            if self.cur_selected_translation.get_id_as_text() == tid:
                self.cur_selected_translation.set_tid(db_table_code, new_wid)

    def __on_wheel_down(self, event):
        self.canvas.yview_scroll(5, "units")

    def __on_wheel_up(self, event):
        self.canvas.yview_scroll(-5, "units")

    def __on_add_entry(self, event):
        map = {lf_tools.SUBST: 0,
               lf_tools.VERB: 1,
               lf_tools.OTHER: 2
               }
        if STATUS.dbHelper.check_exist(db_helper.TRANS_ZH,
                                       'word',
                                       self.var_add_trans.get()) is False:
            STATUS.dbHelper.insert_entry(db_helper.TRANS_ZH,
                                         [str(self.var_add_trans.get())])
            self.set_translation_canvas(STATUS.dbHelper,
                                        self.var_add_trans.get())
            if self.cur_selected_translation is not None:
                STATUS.dbHelper.update_translation_by_id(STATUS.cur_workingtable,
                                                         self.cur_selected_translation.get_id_as_text(),
                                                         self.cur_selected_translation.
                                                         strvar_wids[map[STATUS.cur_workingtable]].get())
        else:
            self.set_translation_canvas(STATUS.dbHelper, self.var_add_trans.get())

    def _on_resize(self, event):
        self.canvas.itemconfig('all', width=event.width)


class TransFrameUnit(Frame):
    """
    This class represent a graphic component to insert in a scroll frame, which display
    informations about a translation,such as:
        (1) its ID (tid)
        (2) its name ( I avoid to say 'word', in order to not be confused with the source word
        (3) Three list of wids ( word ids), one list corresponding to the table in which it
            can be found.
    """

    def __init__(self, master, frame_root, w, h):
        Frame.__init__(self, master)
        self.papa = frame_root
        self['height'] = h
        self['width'] = w
        self.strvar_btn_tid = StringVar(self, value="null")
        self.strvar_trans_name = StringVar(self, value="null")
        self.strvar_wids = []  # Contains the word ids, according to their genre
        self.map_index = {
            db_helper.SUBST: 0,
            db_helper.VERB: 1,
            db_helper.OTHER: 2
        }
        self.strVar_genreName = StringVar(self, value="no_genre")
        self.strVar_catName = StringVar(self, value="no_loaded")

        label_tid = Button(self, textvariable=self.strvar_btn_tid,
                           anchor=W, name="_id")
        label_tid.configure(activebackground="#33B5E5", relief=RAISED)

        label_word = Label(self,
                           textvariable=self.strvar_trans_name,
                           anchor=W, name="word")
        f = font.Font(font=label_word['font'])
        f['size'] = int(f['size'] * (4 / 3))
        label_word['font'] = f

        self['background'] = colors.TRANS_IDLE_BG
        self.config(cursor="dot", highlightbackground="red",
                    highlightcolor="black")

        for index in range(0, 3):
            self.strvar_wids.append(StringVar(self, value=''))
            label_wid = Label(self,
                              textvariable=self.strvar_wids[index],
                              name="trans_id_" + str(index))
            label_wid.place(relx=0.4 + 0.2 * index,
                            rely=0, relw=0.2, relh=1.0)

        label_tid.place(relx=0.0, rely=0.0, relw=0.1, relh=1.0)
        label_word.place(relx=0.1, rely=0.0, relw=0.3, relh=1.0)
        self.bind("<Button-1>", self._on_click)
        for wd in self.winfo_children():
            wd['background'] = colors.TRANS_IDLE_BG
            wd['foreground'] = colors.TRANS_IDLE_FG
            wd.bind('<Button-1>', self._on_click)

    def set_tid_as_str(self, new_str):
        """
        Assign a tid to this frame unit
        :param new_str: tid should be given as a str
        :return: None
        """
        self.strvar_btn_tid.set(new_str)

    def set_trans_name(self, new_str):
        """ Set the name of this translation"""
        self.strvar_trans_name.set(new_str)

    def add_id(self, id_to_insert):
        index = self.map_index[STATUS.cur_workingtable]
        if STATUS.currentSelectedFrame[STATUS.cur_workingtable] is not None:
            tmp = self.strvar_wids[index].get()
            if self.check_exist(tmp, id_to_insert) is True:
                return
            if tmp == '' or tmp is None or tmp == 'None':
                tmp = str(id_to_insert)
            else:
                tmp += ',' + str(id_to_insert)
            self.strvar_wids[index].set(tmp)

    def remove_id(self, id_to_remove):
        index = self.map_index[STATUS.cur_workingtable]
        tmp = self.strvar_wids[index].get()
        tmp2 = ''
        count = 0
        for s in tmp:
            if tmp == id_to_remove:
                continue
            if count != 0:
                tmp2 += ','
            tmp2 += s
        self.strvar_wids[index].set(tmp2)

    @staticmethod
    def check_exist(id_comma_list, new_id):
        tmp = id_comma_list.split(',')
        if tmp == '' or tmp is None:
            return False
        for s in tmp:
            if s == new_id:
                return True
        return False

    def get_comp_by_name(self, component_name):
        return self.nametowidget(component_name)

    def get_id_as_text(self):
        return self.strvar_btn_tid.get()

    def get_trans_name(self):
        return self.strvar_trans_name.get()

    def get_wids(self, db_table_code):
        """
        :param db_table_code: Table from which to retrieve associated wids
        :return: A string containing the word ids, separated by ','
        """
        map = {lf_tools.SUBST: 0,
               lf_tools.VERB: 1,
               lf_tools.OTHER: 2
               }
        res = self.strvar_wids[map[db_table_code]].get()
        return res

    def set_wids(self, db_table_code, value):
        """
        :param db_table_code: Table for which to set the wids
        :param value: A string with wids, separated by ','
        :return:
        """
        map = {
            lf_tools.SUBST: 0,
            lf_tools.VERB: 1,
            lf_tools.OTHER: 2
        }
        self.strvar_wids[map[db_table_code]].set(value)

    def _on_click(self, event):
        prev = self.papa.get_selected_trans()
        if prev is not None:
            prev.set_color(colors.TRANS_IDLE_BG, colors.TRANS_IDLE_FG)
        for wd in self.winfo_children():
            wd['bg'] = colors.TRANS_SELECTED_BG
            wd['fg'] = colors.TRANS_SELECTED_FG
        self.papa.set_selected_trans(self)

    def set_color(self, new_bg, new_fg):
        try:
            for wd in self.winfo_children():
                wd['bg'] = new_bg
                wd['fg'] = new_fg
        except Exception as e:
            pass
