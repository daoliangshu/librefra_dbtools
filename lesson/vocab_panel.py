import tkinter as tk
from copy import deepcopy
from tkinter import ttk

from lxml import etree as et

import db_helper
import lf_tools
import vocabulary_design.vocabulary_designer
from const_definitions import colors
from state import STATUS


class VocabularyPanel(tk.Frame):
    def __init__(self, master):
        """
        This Panel shows the current vocabularies in the vocabulary list,
        and provides control buttons to add and remove entries
        :param master:
        """
        self.vocabulary_tree = None
        self.vocab_list = []
        self.voc_count = 0
        tk.Frame.__init__(self, master)
        self.title_frame = tk.Frame(self, master)
        label = tk.Label(self.title_frame,
                         text=lf_tools.menu_lesson.find('labels').
                         find('vocabulary_title').text)
        label.pack()

        self.content_frame = tk.Frame(self)
        self.control_frame = tk.Frame(self.title_frame)
        # self.pack(fill=tk.BOTH, expand=True)
        self.title_frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.content_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.control_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.X)
        self.canvas = tk.Canvas(self.content_frame,
                                background=colors.LIGHT_GREEN_BLUE,
                                )
        self.canvas.scrollY = tk.Scrollbar(self.content_frame,
                                           orient=tk.VERTICAL,
                                           bg=colors.LIGHT_PURPLE)
        self.canvas['yscrollcommand'] = self.canvas.scrollY.set
        self.canvas.scrollY['command'] = self.canvas.yview
        self.canvas.scrollY.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.X)

        '''Control Panel init'''
        button_add = tk.Button(self.control_frame,
                               text=lf_tools.menu_lesson.find('buttons').find('add').text)
        button_add['command'] = self.on_add_vocab
        button_add.pack(side=tk.LEFT)
        # (1)Config category/thematic of the list (predefined in xml res)
        frame_thematic = tk.Frame(self.control_frame)
        self.strvar_category = tk.StringVar(frame_thematic)
        self.lb_thematic = tk.Label(frame_thematic, text="thematic")
        self.cb_choose_list_theme = ttk.Combobox(frame_thematic,
                                                 textvariable=self.strvar_category,
                                                 state='readonly')
        frame_thematic.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lb_thematic.pack(side=tk.LEFT)
        self.cb_choose_list_theme.pack(side=tk.LEFT, fill=tk.X, expand=True)
        values = []
        self.cat_map = {}
        default_cat_index = -1

        count = 0
        for value in lf_tools.menu_global.find('categories').iter():
            if value.tag == 'categories':
                continue
            if value.tag == 'no':
                default_cat_index = count
            self.cat_map[value.text] = value.tag
            values.append(value.text)
            count += 1
        print(self.cat_map)
        self.cb_choose_list_theme.config(values=values)
        self.cb_choose_list_theme.current(default_cat_index)
        self.cb_choose_list_theme.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.bind('<Configure>', self._on_resize)

    def on_add_vocab(self, item=None):
        print('list_size : ' + str(len(self.vocab_list)))
        frame_unit = VocabFrameUnit(self, 20, self.canvas.winfo_width())
        print('add : ' + str(len(self.vocab_list)))
        if item is not None:
            frame_unit.set(item)
        else:
            frame_unit.set_index(self.voc_count)
        self.canvas.create_window((0, len(self.vocab_list) * 20),
                                  anchor=tk.NW,
                                  window=frame_unit,
                                  tags=lambda x=self.voc_count: str(x))
        self.canvas['scrollregion'] = self.canvas.bbox('all')
        frame_unit.bind("<Button-4>", self._on_wheel_up)
        frame_unit.bind("<Button-5>", self._on_wheel_down)
        for w in frame_unit.winfo_children():
            w.bind("<Button-4>", self._on_wheel_up)
            w.bind("<Button-5>", self._on_wheel_down)
        self.voc_count += 1
        self.vocab_list.append(frame_unit)
        pass

    def set(self, vocabulary_tree):
        self.voc_count = 0
        self.canvas.delete('all')
        self.vocabulary_tree = deepcopy(vocabulary_tree)
        if self.vocabulary_tree is None:
            return
        for item in self.vocabulary_tree.iter('item'):
            self.on_add_vocab(item)

    def get_vocabulary_tree(self):
        """
        :return: an ET.Element representing the vocabulary tree
        """
        vocabulary_tree = et.Element('vocabulary')
        for w in self.winfo_children():
            if isinstance(w, VocabFrameUnit):
                item = w.get_item()
                if item is not None:
                    vocabulary_tree.append(item)
        if vocabulary_tree.find('category') is None:
            cat = et.Element('category')
            cat.text = self.cat_map[self.strvar_category.get()]
            vocabulary_tree.append(cat)
        else:
            vocabulary_tree.find('category').text = \
                self.cat_map[self.strvar_category.get()]
        return vocabulary_tree

    def _on_wheel_down(self, event):
        self.canvas.yview_scroll(5, "units")

    def _on_wheel_up(self, event):
        self.canvas.yview_scroll(-5, "units")

    def on_remove(self, vocab_unit):
        for i in range(0, len(self.vocab_list)):
            if self.vocab_list[i] == vocab_unit:
                if i == len(self.vocab_list) - 1:
                    self.vocab_list[-1].destroy()
                    self.voc_count -= 1
                    self.vocab_list.pop()
                else:
                    vocab_unit.clone(self.vocab_list[len(self.vocab_list) - 1])
                    self.vocab_list[-1].destroy()
                    self.voc_count -= 1
                    self.vocab_list.pop()
                return

    def _on_resize(self, event):
        self.canvas.itemconfig('all', width=event.width)


class VocabFrameUnit(tk.Frame):
    """
    Represents a vocabulary entry in the vocabulary panel
    """

    def __init__(self, master=None, h=20, w=50):
        tk.Frame.__init__(self, master)
        self.root = master
        self.index = -1
        self['height'] = h
        self['width'] = w
        self.dialog_result = None

        self.btn_remove = tk.Button(self,
                                    text='X',
                                    command=self.on_remove)
        self.strVar_type = tk.StringVar(self)
        '''type is SUBST by default (other not yet implemented)'''
        self.strVar_type.set(str(db_helper.SUBST))
        self.strVar_wid = tk.StringVar(self)
        self.strVar_tid = tk.StringVar(self)
        self.strVar_word = tk.StringVar(self)
        self.strVar_word.set('[not set]')

        self.strVar_translation = tk.StringVar(self)
        self.strVar_translation.set('[not set]')

        self.trans_index = 0

        self.lab1 = tk.Label(self, textvariable=self.strVar_word)
        self.lab2 = tk.Label(self, textvariable=self.strVar_translation)
        self.lb_type = tk.Label(self, textvariable=self.strVar_type)
        self.btn_assign = tk.Button(self, text=lf_tools.menu_lesson.find('buttons').
                                    find('assign').text)
        self.btn_assign['command'] = self.on_assign

        self.btn_remove.place(relx=0.0, rely=0.1, relw=0.1, relh=0.8)
        self.lab1.place(relx=0.1, rely=0.1, relw=0.3, relh=0.8)
        self.lab2.place(relx=0.4, rely=0.1, relw=0.3, relh=0.8)
        self.lb_type.place(relx=0.7, rely=0.1, relw=0.1, relh=0.8)
        self.btn_assign.place(relx=0.8, rely=0.1, relw=0.2, relh=0.8)

    def set(self, item_element):
        self.set_index(item_element.get('index'))
        wid_and_type = item_element.find('wid').text.split(',')
        ''' type should be first set, as when setting the wid, it needs to fetch the word
            ( = need to provide the the DB_TYPE )
        '''
        if len(wid_and_type) <= 1:
            self.set_type(lf_tools.SUBST)  # by default
        else:
            self.set_type(wid_and_type[1])
        self.set_wid(wid_and_type[0])  # at last set wid
        self.set_tid(item_element.find('tid').text)

    def clone(self, vocab_unit):
        self.set_type(vocab_unit.get_type())
        self.set_index(vocab_unit.get_index)
        self.set_wid(vocab_unit.get_wid())
        self.set_tid(vocab_unit.get_tid())

    def set_type(self, str_type):

        if str_type is None:
            # Default type is substantiv
            print(('warning : default type assign for voc_item'))
            self.strVar_type.set(str(db_helper.SUBST))
        else:
            print('set_type : ' + str_type)
            self.strVar_type.set(str_type)
        print('after _set_type: ' + self.strVar_type.get())

    def get_type(self):
        return self.strVar_type.get()

    def set_wid(self, wid):
        DB_TYPE = int(self.strVar_type.get())
        wid_int = 0
        tmp = None
        try:
            wid_int = int(wid)
            print('type : ' + str(DB_TYPE))
            tmp = STATUS.dbHelper.get_entry_by_id(DB_TYPE, int(wid))
        except:
            pass
        if tmp is None:
            print('failed to retrive entry from wid')
            self.strVar_wid.set(wid)
            return
        self.strVar_wid.set(wid)
        self.set_word(tmp['word'])

    def set_tid(self, tids):
        if tids is not None:
            tids_str = tids
            tids_list = tids
            if isinstance(tids, str):
                tids_list = tids.split(',')
            else:
                tids_str = self._list_to_str(tids)
            trans_str = ''
            for i in range(0, len(tids_list)):
                tmp = str(STATUS.dbHelper.get_translation_by_id(tids_list[i]))
                if tmp is None or tmp == '':
                    break
                if i != 0:
                    trans_str += ','
                trans_str += tmp
            self.strVar_tid.set(tids_str)
            self.strVar_translation.set(trans_str)
        else:
            self.strVar_tid.set(-1)
            self.strVar_translation.set(-1)

    def set_index(self, index_int):
        self.index = index_int

    def get_index(self):
        return self.index

    def set_word(self, word_str):
        self.strVar_word.set(word_str)

    def get_word(self):
        return self.strVar_word.get()

    def set_translation(self, trans_str):
        self.strVar_translation.set(trans_str)

    def get_translation(self):
        return self.strVar_translation.get()

    def get_wid_and_type(self):
        return self.strVar_wid.get() + ',' + self.strVar_type.get()

    def get_wid(self):
        return self.strVar_wid.get()

    def get_tid(self):
        return self.strVar_tid.get()

    def _list_to_str(self, mylist):
        tmp = ''
        for i in range(0, len(mylist)):
            if i != 0:
                tmp += ','
            tmp += mylist[i]
        return tmp

    def _check_is_valid(self):
        if self.get_wid() is None or int(self.get_wid()) < 0:
            return False
        if self.get_tid() is None or self.get_tid() == '' or self.get_tid() == '-1':
            return False
        return True

    def get_item(self):

        if self._check_is_valid() is False:
            return None

        ''' Retrieve item value as a et.Element'''
        item_tree = et.Element('item')
        wid = et.Element('wid')
        wid.text = self.get_wid_and_type()
        tid = et.Element('tid')
        tid.text = self.get_tid()
        item_tree.set('index', str(self.index))
        item_tree.append(wid)
        item_tree.append(tid)
        return item_tree

    def on_assign(self):
        mbox = vocabulary_design.vocabulary_designer.VocabBoxDesign(self, 'hudada')
        self.wait_window(mbox.top)
        print('after dialog')
        if self.dialog_result is not None:
            print('dialog_res : ' + str(self.dialog_result))
            self.strVar_type.set(self.dialog_result['type'])
            self.set_wid(self.dialog_result['wid'])
            self.set_tid(self.dialog_result['tid'])
            print(self.dialog_result)

    def on_remove(self):
        self.root.on_remove(self)
