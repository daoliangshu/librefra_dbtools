import tkinter as tk
from tkinter import ttk

import lf_tools
from const_definitions import categories
from const_definitions import colors
from state import STATUS


class AttributeFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.config(bg=colors.LIGHT_PURPLE)
        self.frames = {lf_tools.SUBST: SubstGlobalAttribute(self),
                       lf_tools.VERB: VerbGlobalAttribute(self),
                       lf_tools.OTHER: OtherGlobalAttribute(self)}

    def display(self, word_table_type):
        if STATUS.currentSelectedFrame[word_table_type] is None:
            return
        for k, fra in self.frames.items():
            if k is not word_table_type:
                fra.pack_forget()
            self.frames[word_table_type].pack(fill=tk.BOTH, expand=True)
            if word_table_type == lf_tools.VERB:
                self.frames[word_table_type]. \
                    set_flags(STATUS.
                              currentSelectedFrame[word_table_type].
                              get_type())

    def update(self):
        if STATUS.currentSelectedFrame[STATUS.cur_workingtable] is None:
            return
        self.frames[STATUS.cur_workingtable].update()


class VerbGlobalAttribute(tk.Frame):
    """
    Displays attributes of entry belonging to verb type
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.top_frame = tk.Frame(self)
        self.btn_category = tk.Button(self.top_frame,
                                      text=lf_tools.menu_global.
                                      find('buttons').
                                      find('category').text,
                                      name='category')
        self.btn_category.tag = 'category'
        self.btn_category.pack(side=tk.LEFT, expand=True)
        self.btn_category.bind('<Button-1>', self.on_click)
        self.btn_flags = tk.Button(self.top_frame,
                                   text=lf_tools.
                                   menu_global.find('buttons').
                                   find('flags').text,
                                   name='flags')
        self.btn_flags.pack(side=tk.LEFT, expand=True)
        self.btn_flags.tag = 'flags'
        self.btn_flags.bind('<Button-1>', self.on_click)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.content_frame = {
            'category': CategoryFrame(self),
            'flags': VerbFlagFrame(self)
        }
        self.content_frame['flags'].pack(fill=tk.X, expand=True)

    def set_flags(self, flag_type):
        self.content_frame['flags'].set(flag_type)

    def set_categories_int(self, category_flag_int):
        self.content_frame['category'].set(category_flag_int)

    def on_click(self, event):
        for key, frame in self.content_frame.items():
            if key is not event.widget.tag:
                frame.pack_forget()
        print(event.widget.tag)
        self.content_frame[event.widget.tag].pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def update(self):
        cur = STATUS.currentSelectedFrame[STATUS.cur_workingtable]
        if cur is None:
            return
        self.set_categories_int(cur.get_categories_int())


class SubstGlobalAttribute(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.top_frame = tk.Frame(self)
        self.btn_category = tk.Button(self.top_frame, text='CATEGORY', name='cat_btn')
        self.btn_category.pack(side=tk.LEFT, expand=True)
        self.btn_category = tk.Button(self.top_frame, text='AUTRES', name='other_btn')
        self.btn_category.pack(side=tk.LEFT, expand=True)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.content_frame = []
        self.content_frame.append(CategoryFrame(self))
        self.content_frame.append(CategoryFrame(self))
        self.content_frame[0].pack(fill=tk.X, expand=True)

    def set_categories_int(self, category_flag_int):
        self.content_frame[0].set(category_flag_int)

    def update(self):
        cur = STATUS.currentSelectedFrame[STATUS.cur_workingtable]
        if cur is None:
            return
        self.set_categories_int(cur.get_categories_int())


class OtherGlobalAttribute(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.top_frame = tk.Frame(self, bg=colors.LIGHT_PURPLE)
        self.btn_category = tk.Button(self.top_frame, text='CATEGORY', name='cat_btn')
        self.btn_category.pack(side=tk.LEFT, expand=True)
        self.btn_category = tk.Button(self.top_frame, text='AUTRES', name='other_btn')
        self.btn_category.pack(side=tk.LEFT, expand=True)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.content_frame = []
        self.content_frame.append(CategoryFrame(self))
        self.content_frame.append(CategoryFrame(self))
        self.content_frame[0].pack(fill=tk.X, expand=True)

    def set_categories_int(self, category_flag_int):
        self.content_frame[0].set(category_flag_int)

    def update(self):
        cur = STATUS.currentSelectedFrame[STATUS.cur_workingtable]
        if cur is None:
            return
        self.set_categories_int(cur.get_categories_int())


class CategoryFrame(tk.Frame):
    """
    Frame in which user can select categories for a selected word
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.type = "SUBST"
        row_index = 0
        self.todisplay = ['categories1', 'categories2', 'categories3', 'categories4']

        self.var = []
        self.order = {}
        tmp = lf_tools.menu_subst.find(self.todisplay[0])
        s = int(tmp.find('size').text)
        index = 0
        tmp_cat = lf_tools.menu_global.find('categories')
        if s == -1:
            '''for k, v in categories.categories.items():
                self.order[v] = int(index)
                self.var.append(k)
                index += 1'''
            for cat_unit in tmp_cat.iter():
                if cat_unit.tag == 'categories':
                    continue
                print(cat_unit.text)
                self.order[int(cat_unit.get('index'))] = index

                self.var.append(cat_unit.text)
                index += 1
        else:
            '''not used yet ( categorys uses the s = -1 tag)'''
            for index in range(0, s):
                self.var.append(tmp.find('str' + str(index + 1)).text)

        index = 0
        self.strVar_Combobox = []
        self.category_combobox = []
        for flag_name in self.todisplay:
            label_flag1 = tk.Label(self, text='category ' + str(index))
            label_flag1.grid(row=row_index, column=0)
            self.strVar_Combobox.append(tk.StringVar())
            entry_flag1 = ttk.Combobox(self, values=self.var, name=flag_name, textvariable=self.strVar_Combobox[index])
            entry_flag1.bind('<<ComboboxSelected>>', self._on_categories_changed)
            entry_flag1.grid(row=row_index, column=1)
            self.category_combobox.append(entry_flag1)
            row_index += 1
            index += 1

    def get_frame_type(self):
        """
        returns as a string the type of the word : 'SUBST', 'VERB', 'OTHER'
        :return:
        """
        return self.type

    def set(self, category_flag_int):
        """
        Parse category informations contained in the flag
        and displays it
        :param category_flag_int: is an integer
        :return: None
        """
        for index in range(0, len(self.todisplay)):
            cat = self.nametowidget(self.todisplay[index])
            cat.current(self.order[(category_flag_int >> index * 4) & int('1111', 2)])

    def _on_categories_changed(self, event):
        """
        Trigger when user change a category
        :param event:
        :return:
        """
        if STATUS.currentSelectedFrame[STATUS.cur_workingtable] is not None:
            tmp = 0
            for i in range(0, 4):
                cat_keyword = self.category_combobox[i].get()

                for cat_it in lf_tools.menu_global.find('categories').iter():
                    if cat_it.text == cat_keyword:
                        cat_keyword = cat_it.tag.upper()
                tmp += ((categories.categories[cat_keyword] & int('1111', 2)) << i * 4)
            STATUS.currentSelectedFrame[STATUS.cur_workingtable].set_categories(lf_tools.get_hex(tmp))


class VerbFlagFrame(tk.Frame):
    """
    Depreciated
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.todisplay = ['transitivity',
                          'prepositional',
                          'impersonal_passif',
                          'impersonal_norm']
        row_index = 0
        for flag_name in self.todisplay:
            col_index = 0
            tmp = lf_tools.menu_verb.find(flag_name)
            label_flag1 = tk.Label(self, text=tmp.find('head').text)
            label_flag1.grid(row=row_index, column=col_index)
            col_index += 1
            var = []
            self.cb_flag1 = []
            for index in range(0, int(tmp.find('size').text)):
                var.append(tmp.find('str' + str(index + 1)).text)
            cb_flag1 = ttk.Combobox(self,
                                    values=var,
                                    name=flag_name)
            cb_flag1.grid(row=row_index, column=col_index)
            row_index += 1

    def set(self, flag_type):
        for flag_name in self.todisplay:
            self.nametowidget(flag_name). \
                current((flag_type & lf_tools.V.MASK[flag_name]) >> lf_tools.V.SHIFT[flag_name])
