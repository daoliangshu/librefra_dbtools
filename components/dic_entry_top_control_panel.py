import tkinter as tk

import db_helper
import lf_tools
from const_definitions import colors


class SelectWordTypePanel(tk.Frame):
    def __init__(self, master, root):
        tk.Frame.__init__(self, master)
        self.root = root
        self.top_frame = tk.Frame(self, bg=colors.LIGHT_GREEN)
        self.bottom_frame = tk.Frame(self)

        self.btn_choose_verb = tk.Button(self.top_frame,
                                         text=lf_tools.menu_global.
                                         find('buttons').find('verb').text,
                                         command=self.root.callback_display_verb)
        self.btn_choose_subst = tk.Button(self.top_frame,
                                          text=lf_tools.menu_global.find('buttons').
                                          find('subst').text,
                                          command=self.root.callback_display_subst)
        self.cur_workingtable = db_helper.SUBST
        self.btn_choose_adj = tk.Button(self.top_frame,
                                        text=lf_tools.menu_global.find('buttons').
                                        find('others').text,
                                        command=self.root.callback_display_other)
        # Map word type <-> corresponding button
        self.buttons = {'noun': self.btn_choose_subst,
                        'verb': self.btn_choose_verb,
                        'other': self.btn_choose_adj
                        }

        self.edit_frame = tk.Frame(self.bottom_frame, bg=colors.LIGHT_YELLOW)
        self.label_search = tk.Label(self.edit_frame,
                                     text=lf_tools.menu_global.
                                     find('labels').find('search').text,
                                     bg=colors.LIGHT_YELLOW)
        self.strVar_entry_searched = tk.StringVar(self.edit_frame)
        self.entry_search = tk.Entry(self.edit_frame,
                                     textvariable=self.strVar_entry_searched)

        self.entry_search.bind('<Return>',
                               lambda event: self.root.on_search(self.
                                                                 strVar_entry_searched.get()))
        self.btn_search = tk.Button(self.edit_frame,
                                    text=lf_tools.menu_global.
                                    find('buttons').find('launch').text)
        self.btn_search.id = 'btn_search'
        self.btn_search.bind("<Button-1>",
                             lambda event: self.root.on_search(self.
                                                               strVar_entry_searched.get()))
        # self.bind('<Configure>', self.init_position)

        self.init_position()

    def get_buttons_map(self):
        return self.buttons

    def init_position(self):
        # for widget in self.winfo_children():
        #    widget.pack_forget()

        self.top_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        # for top_widget in self.top_frame.winfo_children():
        #    top_widget.pack_forget()
        # for bottom_widget in self.bottom_frame.winfo_children():
        #    bottom_widget.pack_forget()

        self.btn_choose_verb.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.btn_choose_subst.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.btn_choose_adj.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.edit_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # for edit_widget in self.edit_frame.winfo_children():
        #    edit_widget.pack_forget()
        self.label_search.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.entry_search.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.btn_search.pack(side=tk.LEFT, fill=tk.Y, expand=True)
