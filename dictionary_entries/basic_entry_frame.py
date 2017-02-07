import tkinter as tk

import lf_tools
from db_service import db_update
from state import STATUS


class BaseEntryFrameUnit(tk.Frame):
    """
    Base Frame Unit for Any word entry:
        All the frame units should inherit from it
    """

    def __init__(self, master, w, h):
        tk.Frame.__init__(self, master)
        self['height'] = h
        self['width'] = w
        self['bd'] = 1
        self['relief'] = tk.SUNKEN
        # StringVar for base attributes of entries
        self.strvar_info = tk.StringVar(self)
        self.strvar_button_name = tk.StringVar(self, value="null")
        self.strvar_word_name = tk.StringVar(self, value="null")
        self.strvar_cat_name = tk.StringVar(self, value="no_loaded")
        self.strvar_translation = tk.StringVar(self, value="null")
        self.strvar_level = tk.StringVar(self)  # Not implemented: +store frequency of the word

        self.config(cursor="dot",
                    highlightbackground="red",
                    highlightcolor="black")
        self.trans_id = ['', '', '']
        self.label_id = tk.Button(self,
                                  textvariable=self.strvar_button_name,
                                  anchor=tk.CENTER,
                                  name="_id")
        self.label_id.configure(activebackground="#33B5E5", relief=tk.RAISED)
        self.label_id.bind("<Button-1>", db_update.send_update)
        self.label_word = tk.Entry(self,
                                   textvariable=self.strvar_word_name,
                                   name="word")
        self.label_word['background'] = "red"
        self.label_trans = tk.Label(self,
                                    textvariable=self.strvar_translation,
                                    name="trans")
        self.label_trans.config(justify=tk.CENTER)
        self.label_cat_flag = tk.Button(self,
                                        textvariable=self.strvar_cat_name,
                                        anchor=tk.CENTER,
                                        name="cat")
        self.label_cat_flag.tag = 'cat'

    def set_update_state(self, is_updated):
        if is_updated is False:
            self.label_id.config(background='#AA0000')
        else:
            self.label_id.config(background='#00AA00')

    # ---------------Getters -----------------#
    def get_comp_by_name(self, component_name):
        return self.nametowidget(component_name)

    def get_id(self):
        """
        :return: wid as an integer
        """
        return int(self.strvar_button_name.get())

    def get_id_as_text(self):
        """
        :return: wid as an string
        """
        return str(self.strvar_button_name.get())

    def get_word(self):
        """
        Retrieves the word.
        :return: word
        """
        return self.strvar_word_name.get()

    def remove_tid(self, order, tid_to_remove):

        if order is not None and \
                                0 <= order < 3 and \
                        self.trans_id[order] is not None and \
                        self.trans_id[order] != '':
            ids = []
            if ',' in self.trans_id[order]:
                ids = self.trans_id[order].split(',')
            else:
                ids = [self.trans_id[order]]
            if tid_to_remove in ids:
                ids.remove(tid_to_remove)

    def get_tid(self, order):
        """
        tids are separated in 3 buckets ( each containing a list of tids)
        A buck represents 1 meaning of a word
        :param order: which bucket, from 0 to 2
        :return:
        """
        if 0 <= order < 3:
            return self.trans_id[order]
        return None

    def get_categories_int(self):
        """
        :return: category flag as an integer
        """
        cat = self.strvar_cat_name.get()
        return lf_tools.hex_to_int(cat)

    def get_info(self):
        """
        Retrieve informations associated with each meaning of the word
        informations per meaning are a string, separated by ';'
        ex:  'comments for meaning 1 ; {math.} comments for meaning 2; {fam.} no comments
            for meaning 3'
        :return:
        """
        return self.strvar_info.get()

    # ------------Setters --------------#
    def set_common(self, row):
        """
        Retrieve from a row of a query in db the columns that are common to all
        the entry frame units
        :param row: row from db
        :return: None
        """
        self.set_id_as_text(str(row['_id']))
        self.set_word(lf_tools.set_word(row['word']))
        self.set_categories(lf_tools.get_hex(row['categories_flag']))
        self.set_tid(0, row['trans_id1'])
        self.set_tid(1, row['trans_id2'])
        self.set_tid(2, row['trans_id3'], True)
        self.set_info(row['info'])

    def set_info(self, info_str):
        """
        Set the informations associated with the translations for the given word
        info_str should separates the meaning ( 0 to 2)  by ';'
        :param info_str:
        :return:
        """
        if info_str is None or info_str == '' or info_str == 'None':
            self.strvar_info.set(';;')
        else:
            self.strvar_info.set(info_str)

    def set_id_as_text(self, new_str):
        """
        :param new_str:
        :return: word id as a str
        """
        self.strvar_button_name.set(new_str)

    def set_word(self, new_str):
        """
        Set the word
        :param new_str:
        :return:
        """
        self.strvar_word_name.set(new_str)

    def set_tid(self, order, value, update_display=False):
        """
        Set the trans_ids for a meaning bucket (0 to 2)

        :param order:
        :param value: a string of trans_ids separated by ','
        :param update_display: ask to display the new value in the frame
        :return:
        """
        if 0 > order or order > 3:
            return
        self.trans_id[order] = value
        if update_display is True:
            self.update_trans_display()

    def set_categories(self, new_str):
        self.strvar_cat_name.set(new_str)

    def set_trans(self, new_str):
        self.strvar_translation.set(new_str)

    # ----------Updates/Events -------------#
    def write_in_db(self):
        db_update.send_update(self)

    @staticmethod
    def change_state_frame(btn, lf_tools_state):
        if lf_tools_state == lf_tools.UPDATED:
            btn.config(background='#00AA00')
        elif lf_tools_state == lf_tools.NON_UPDATED:
            btn.config(background='#AA0000')

    def update_trans_display(self):
        if self.trans_id[0] is None:
            self.strvar_translation.set(None)
            return
        trans_array = self.trans_id[0].split(',')
        temp_trans = ''
        cnt = 0
        for wor in trans_array:
            res = STATUS.dbHelper.get_translation_by_id(wor)
            if res is None:
                continue
            if cnt != 0:
                temp_trans += ','
            temp_trans += res
            cnt += 1
            self.strvar_translation.set(temp_trans)
