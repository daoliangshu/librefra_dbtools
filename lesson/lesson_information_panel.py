import tkinter as tk
from tkinter import ttk

import lf_tools


class LessonInformationPanel(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        lesson_theme_subframe = tk.Frame(self)
        self.lb_theme = tk.Label(lesson_theme_subframe,
                                 text=lf_tools.menu_lesson.
                                 find('labels').
                                 find('theme').text)
        self.strvar_theme = tk.StringVar(self)
        self.e_theme = tk.Entry(lesson_theme_subframe, textvariable=self.strvar_theme)

        lesson_theme_subframe.pack(side=tk.LEFT)
        self.lb_theme.pack()
        self.e_theme.pack()

        # Lesson level frame
        lesson_level_subframe = tk.Frame(self)
        self.lb_level = tk.Label(lesson_level_subframe,
                                 text=lf_tools.menu_global.find('labels').find('level').text)
        var_level = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        self.strvar_level = tk.StringVar(lesson_level_subframe)
        self.cb_level = ttk.Combobox(lesson_level_subframe,
                                     values=var_level,
                                     textvariable=self.strvar_level)
        self.cb_level.current(0)
        lesson_level_subframe.pack(side=tk.LEFT)
        self.lb_level.pack()
        self.cb_level.pack()

        lesson_type_subframe = tk.Frame(self)
        self.lb_type = tk.Label(lesson_type_subframe,
                                text=lf_tools.menu_lesson.find('labels').
                                find('type').text)
        self.strvar_current_type = tk.StringVar(self)
        self.map_types = {}  # local language as key, canonic english correspondance as value
        self.var_types = []
        # (2) Associate translations of content types to the standard names
        for content_type in lf_tools.menu_lesson.find('type_list').iter():
            if content_type.tag == 'type_list':
                # Ignore the nodes tagged like parent node
                continue
            self.map_types[content_type.text] = content_type.tag  # ex: key:dialogue mapped to value:dialog
            self.var_types.append(content_type.text)
        self.cb_type = ttk.Combobox(lesson_type_subframe,
                                    values=self.var_types,
                                    textvariable=self.strvar_current_type)
        self.cb_type.bind("<<ComboboxSelected>>", self._on_type_changed)
        for k, value in self.map_types.items():
            if value == 'normal':
                for i in range(0, len(self.var_types)):
                    if self.var_types[i] == k:
                        self.cb_type.current(i)
                        break
                break
        lesson_type_subframe.pack(side=tk.LEFT)
        self.lb_type.pack()
        self.cb_type.pack()

    def get_type(self):
        return self.map_types[self.strvar_current_type.get()]

    def get_level(self):
        level = self.strvar_level.get()
        if level.startswith('A'):
            return 0
        elif level.startswith('B'):
            return 1
        elif level.startswith('C'):
            return 2
        return 0

    def get_theme(self):
        return self.strvar_theme.get()

    def set_type(self, selected_type):
        for key, value in self.map_types.items():
            if selected_type == value:
                self.strvar_current_type.set(key)

    def set_level(self, new_level):
        if new_level is not None and 0 <= int(new_level) <= 3:
            self.cb_level.current(int(new_level))

    def _on_type_changed(self, event=None):
        """
        Triggered when user chooser a content type ( dialog, normal , peotry ?)
        :param event:
        :return:
        """
        selected_type = self.map_types[self.strvar_current_type.get()]
        if event is not None:
            selected_type = self.map_types[event.widget.get()]
        self.master.set_type(selected_type)
