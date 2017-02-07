import tkinter as tk
from tkinter import ttk

import lf_tools
from dictionary_entries.basic_entry_frame import BaseEntryFrameUnit
from service import content_setter as cs


class SubstEntryFrameUnit(BaseEntryFrameUnit):
    """
    Represents a frame displaying infomations of a word in "subst" table
    """

    def __init__(self, master, w, h):
        super().__init__(master, w, h)
        self.genre_index = -1
        tmp = lf_tools.menu_subst.find('genre')
        s = int(tmp.find('size').text)
        var = []
        for index in range(0, s):
            var.append(tmp.find('str' + str(index + 1)).text)

        index = 0
        self.strVar_Combobox = tk.StringVar(self)
        self.combo_genre = ttk.Combobox(self,
                                        values=var,
                                        name='genre',
                                        textvariable=self.strVar_Combobox)
        self.combo_genre.config(justify=tk.CENTER)
        self.combo_genre.bind('<<ComboboxSelected>>', self.on_genre_changed)

        my_places = cs.get_place(lf_tools.SUBST)
        my_widgets = [self.label_id,
                      self.label_word,
                      self.label_cat_flag,
                      self.label_trans,
                      self.combo_genre]
        for i in range(0, len(my_widgets)):
            my_widgets[i].place(relx=my_places[i][0],
                                rely=my_places[i][1],
                                relw=my_places[i][2],
                                relh=my_places[i][3])

    # -----------Setters -------------#
    def set_genre(self, int_id):
        self.genre_index = int_id
        self.combo_genre.current(int_id)

    # ------------Getters -----------#
    def get_genre_as_text(self):
        return self.combo_genre.get()

    def get_genre(self):
        return self.combo_genre.current()

    # -----------Events/ Updates -----#
    def on_genre_changed(self, event):
        self.genre_index = event.widget.current()
