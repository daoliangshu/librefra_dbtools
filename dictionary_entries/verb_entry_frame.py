import tkinter as tk
from tkinter import ttk

import lf_tools
from components import verb_design_dialog
from dictionary_entries.basic_entry_frame import BaseEntryFrameUnit


class VerbEntryFrameUnit(BaseEntryFrameUnit):
    def __init__(self, master, w, h):
        super().__init__(master, w, h)

        self.flag_type = None
        tmp = lf_tools.menu_subst.find('genre')
        s = int(tmp.find('size').text)
        var = []
        for index in range(0, s):
            var.append(tmp.find('str' + str(index + 1)).text)
        self.strvar_genre = tk.StringVar(self)
        self.combo_genre = ttk.Combobox(self,
                                        values=var,
                                        name='genre',
                                        textvariable=self.strvar_genre)
        self.btn_show_verb = tk.Button(self, text="Montrer",
                                       name='btn_showverb',
                                       command=self.show_verb)
        self.label_id.place(relx=0.0, rely=0.0, relw=0.1)
        self.label_word.place(relx=0.1, rely=0.0, relw=0.2)
        self.label_cat_flag.place(relx=0.3, rely=0.0, relw=0.1)
        self.btn_show_verb.place(relx=0.4, rely=0.0, relw=0.2)
        self.label_trans.place(relx=0.7, rely=0.0, relw=0.28)

    # ---------Events/ Updates ------------#
    def show_verb(self):
        verb_design_dialog.VerbBoxDesign(self, self.strvar_word_name.get())

    # ----------Getters -----------#
    def get_genre_as_text(self):
        return self.combo_genre.get()

    def get_type(self):
        if self.flag_type is None:
            return 1
        else:
            return self.flag_type

    # -----------Setters ---------------#
    def set_type(self, new_type):
        self.flag_type = new_type
