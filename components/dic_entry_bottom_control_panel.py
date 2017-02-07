import tkinter as tk

import lf_tools
from const_definitions import colors
from state import STATUS


class ControlPanel(tk.Frame):
    def __init__(self, master, root):
        tk.Frame.__init__(self, master)
        self.root = root
        self.strVar_add = tk.StringVar(self)
        self.strVar_add.set('')
        self.bottom_frame = tk.Frame(self, bg=colors.LIGHT_PURPLE)
        self.lbl_1 = tk.Label(self.bottom_frame,
                              text=lf_tools.menu_global.find('labels').
                              find('add').text,
                              background=colors.LIGHT_GREEN)

        '''Change entry PAGE'''
        self.top_frame = tk.Frame(self, bg=colors.LIGHT_GREEN)
        self.strVar_page_num = tk.StringVar(self.top_frame, value='0')
        self.btn_prev_page = tk.Button(self.top_frame,
                                       text=lf_tools.menu_global.find('buttons').find('previous').text,
                                       command=self.root.ENTRIES_FRAME.previous_page)
        self.lb_page_num = tk.Label(self.top_frame,
                                    textvariable=self.strVar_page_num,
                                    background=colors.LIGHT_YELLOW)
        self.btn_next_page = tk.Button(self.top_frame,
                                       text=lf_tools.menu_global.find('buttons').find('next').text,
                                       command=self.root.ENTRIES_FRAME.next_page)
        # self.btn_next_page['state'] = tk.DISABLED
        # self.btn_prev_page['state'] = tk.DISABLED

        self.e_word_to_add = tk.Entry(self.bottom_frame, textvariable=self.strVar_add)
        self.e_word_to_add.bind('<Return>', self.on_add_entry)
        print('control_comp created')
        self.btn_prev_page.pack(side=tk.LEFT)
        self.lb_page_num.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_next_page.pack(side=tk.RIGHT)
        self.top_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.bottom_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.lbl_1.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.e_word_to_add.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def set_page(self, page_num):
        """
        update the current page index display
        :param page_num:
        :return:
        """
        self.strVar_page_num.set(str(page_num))

    def get_page(self):
        """
        Retrieve current page index
        :return:
        """
        return int(self.strVar_page_num.get())

    def set_add_value(self, str_value):
        self.strVar_add.set(str_value)

    def get_add_value(self):
        return self.strVar_add.get()

    def getcomponent_add_label(self):
        return self.lbl_1

    def on_add_entry(self, event):
        value_to_add = event.widget.get()
        res = STATUS.dbHelper.check_exist(STATUS.cur_workingtable,
                                          'word', value_to_add)
        print(('Exist ? : ' + str(res)))
        if res is False:
            print(value_to_add)
            insert_bundle = [value_to_add, 0, 0]  # [1],[2] useless
            STATUS.dbHelper.insert_entry(STATUS.cur_workingtable, insert_bundle)
        else:
            print('value_to_add : this word already exist')
        self.set_add_value('')
        self.root.set_content(STATUS.cur_workingtable, value_to_add)
