import tkinter as tk
from tkinter import ttk

import lf_tools
from dictionary_entries.basic_entry_frame import BaseEntryFrameUnit


class OtherEntryFrameUnit(BaseEntryFrameUnit):
    """
    Represents a frame displaying informations about  a word in  "other" table
    "other" table contains words that are nor substantives nor verbs
    """

    def __init__(self, master, w, h):
        super().__init__(master, w, h)

        self.strVar_type = tk.StringVar(self)
        var = []

        # Type are mapped from xml file for internationalization
        self.type_map = {}
        for tx in lf_tools.menu_global.find('var').find('subtype_list').iter():
            # adj, pro, prep, expr, prov, .. are standard english abbreviations used as keys
            if tx.tag != 'subtype_list':
                # .text is the local correspondance to the type
                tmp = [tx.text, tx.get('code')]  # code is the standard letter used for the type (ex 'a' for adj)
                self.type_map[tx.tag] = tmp
                var.append(tx.text)
        self.cb_type = ttk.Combobox(self, textvariable=self.strVar_type, values=var)
        self.cb_type.current(0)
        self.init_position()

    def init_position(self):
        self['width'] = self.master.winfo_width()
        # for widget in self.winfo_children():
        #    widget.place_forget()
        self.label_id.place(relx=0.0, rely=0.0, relw=0.1)
        self.label_word.place(relx=0.1, rely=0.0, relw=0.2)
        self.label_cat_flag.place(relx=0.3, rely=0.0, relw=0.1)
        self.cb_type.place(relx=0.4, rely=0.0, relw=0.3)
        self.label_trans.place(relx=0.7, rely=0.0, relw=0.3)

    def set_type(self, type_char):
        """
        Set the type of the word, according to the self..type_map
        :param type_char:
        :return:
        """
        for _, type_to_check in self.type_map.items():
            if type_to_check[1] == type_char:
                self.cb_type.set(type_to_check[0])

    def get_type(self):
        """
        Get the type of the word ( adjective, adverbe , etc )
        Note: if the word can have more than one type,
                the additionnal type can be informed in the info panel using form {+type_the_type.}
        :return:
        """
        for _, retrieved_type in self.type_map.items():
            if retrieved_type[0] == self.strVar_type.get():
                return retrieved_type[1]
        return None
