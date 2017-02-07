import tkinter as tk
from tkinter import ttk

from lxml import etree as et

import lf_tools
from const_definitions import colors


class QCMSettingUnit(tk.Frame):
    """
        Represents a wave in an activity of type <multiplechoices>
        The method 'get_wave_tree' should be used in order to retrieve a wave
    """

    def __init__(self, master=None, height=90, width=50):
        tk.Frame.__init__(self, master)
        '''correct : the indexes of correct answers, separated by ,'''
        self['height'] = height
        self['width'] = width
        self.master = master
        self.index = -1

        self.question = tk.Text(self, wrap=tk.WORD, bg='red')

        # Hint frame ( provide hint for choosing the answer)
        self.fr_hint_frame = tk.Frame(self)
        self.strvar_hint = tk.StringVar(self.fr_hint_frame)
        self.lb_hint = tk.Label(self.fr_hint_frame,
                                text=lf_tools.menu_global.
                                find('labels').find('hint').text)
        self.hint = tk.Entry(self.fr_hint_frame, textvar=self.strvar_hint)

        # Info frame ( provide info. about the answer)
        self.fr_info_frame = tk.Frame(self)
        self.strvar_info = tk.StringVar(self.fr_info_frame)
        self.lb_info = tk.Label(self.fr_info_frame,
                                text=lf_tools.menu_global.
                                find('labels').find('info').text)
        self.info = tk.Entry(self.fr_info_frame,
                             textvar=self.strvar_info)

        # Speed ( relative speed from 1 to 5, 5 is faster)
        self.strvar_speed = tk.StringVar(self)
        var = [1, 2, 3, 4, 5]
        self.lb_speed = tk.Label(self,
                                 text=lf_tools.menu_global.find('labels').
                                 find('speed').text)
        self.cb_speed = ttk.Combobox(self,
                                     value=var,
                                     textvariable=self.strvar_speed)
        self.cb_speed.current(0)

        # Choices
        self.choices_count = 4
        self.choice_frame_list = []  # each frame contain the widgets to display for a choice
        self.choice_tree = []
        self.choice_correctness_list = []  # value of correctness associated with each choice(in checkbox)
        self.correctness = ''
        self.text_choice_list = []  # each choice take as parent the corresponding choice frame

        r = 4
        r_w = 0.6 / (r / 2)
        r_h = 0.35
        self.question.place(relx=0.0, rely=0.0, relw=0.40, relh=0.8)

        self.fr_info_frame.place(relx=0.0, rely=0.7, relw=0.8, relh=0.15)
        self.info.place(relx=0.2, rely=0.0, relw=0.8, relh=1.0)
        self.lb_info.place(relx=0.0, relw=0.2)

        self.fr_hint_frame.place(relx=0.0, rely=0.85, relw=0.8, relh=0.15)
        self.hint.place(relx=0.2, rely=0.0, relw=0.8, relh=1.0)
        self.lb_hint.place(relx=0.0, relw=0.2)
        self.lb_speed.place(relx=0.8, rely=0.7, relw=0.2, relh=0.1)
        self.cb_speed.place(relx=0.8, rely=0.8, relw=0.2, relh=0.2)
        self.checkbox_choices_list = []
        for i in range(0, 4):
            index = int(i)
            self.choice_frame_list.append(tk.Frame(self))
            self.choice_frame_list[i].index = i
            fl = 0.4 + i % (r / 2) * r_w
            fl2 = 0.0
            if i >= r / 2:
                fl2 = r_h

            self.choice_frame_list[i].place(relx=fl, rely=fl2, relw=r_w, relh=r_h)
            self.choice_frame_list[i]['bg'] = 'red'
            self.choice_correctness_list.append(tk.IntVar(self))
            self.choice_tree.append(et.Element('item'))
            self.choice_correctness_list[index].set(0)
            lb = tk.Label(self.choice_frame_list[i], text=str(i + 1))
            lb.pack(side=tk.LEFT)
            checkbox_choice = tk.Checkbutton(self.choice_frame_list[i],
                                             text='',
                                             variable=self.choice_correctness_list[index],
                                             onvalue=1,
                                             offvalue=0
                                             )
            checkbox_choice.index = index
            checkbox_choice['bg'] = 'red'
            # Associate the checkbox with the event self.on_check
            checkbox_choice['command'] = lambda x=index: self.on_check(x)
            checkbox_choice.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.checkbox_choices_list.append(checkbox_choice)
            self.choice_tree[i].set('index', str(i))
            self.text_choice_list.append(tk.Text(self.choice_frame_list[i],
                                                 wrap=tk.WORD,
                                                 ))
            self.text_choice_list[i].index = i
            self.text_choice_list[i].pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def update_correctness(self):
        """
        Occurs when the correctness of one of the choices changed.
        It concatenates the correct choice indexes in a string, separated by a comma ','
        :return: None
        """
        total_correctness = ''
        for i in range(0, 4):
            if self.choice_correctness_list[i].get() == 1:
                if total_correctness != '':
                    total_correctness += ','
                total_correctness += str(i)
        self.correctness = total_correctness

    def set_correctness(self, str_correct):
        """
        Set the <self.correctness> ( string )
            and each choice <self.choice_correctness[i]> IntVar,
            which is binded which each CheckBox
        :param str_correct: string of correct choice index, separated by comma ','
        :return: None
        """
        print('correct : ' + str_correct)
        self.correctness = str_correct
        if self.correctness is not None:
            tmp = self.correctness.split(',')
            for index in tmp:
                if 0 <= int(index) < 4:
                    self.choice_correctness_list[int(index)].set(1)
        for i in range(0, 4):
            self.on_check(i)

    def set_speed(self, speed_str):
        """
        Set the speed of a wave. the greater is the speed, lesser is time provided to answer.
        :param speed_str: speed as a string, which should be between 0 and 5
        :return:
        """
        if speed_str is not None and 0 < int(speed_str) < 6:
            self.cb_speed.set(speed_str)

    def get_speed(self):
        return self.strvar_speed.get()

    def on_check(self, index):
        """
        Triggered by a combobox when its status has changed,
        That is when the correctness status of the choice has been changed by the user.
        Can also the trigger independently, just giving the index to update
        :param index:
        :return:
        """
        if 0 > index > 3:
            return  # index out of range
        check_status = self.choice_correctness_list[index].get()
        self.update_correctness()
        col = colors.CHOICE_INCORRECT
        if check_status == 1:
            # Is a correct choice
            col = colors.CHOICE_CORRECT
        for w in self.choice_frame_list[index].winfo_children():
            if isinstance(w, tk.Checkbutton):
                w['bg'] = col

    def set_index(self, index):
        self.index = index

    def set_title(self, str_title):
        """
        :param str_title: This is the message that is provide with a wave, can be an instruction,
                            question, etc...
        :return: None
        """
        self.question.delete(1.0, tk.END)
        self.question.insert(1.0, str_title)

    def set_choice(self, str_choice, index):
        """
        Set the choice text content pointed by the index
        :param str_choice:
        :param index:
        :return:
        """
        if 0 > index > 4:
            print('Err: <qcm_wave_designer.py;set_choice>->index out of bound: ' + str(index))
            return
        for w in self.choice_frame_list[index].winfo_children():
            if isinstance(w, tk.Text):
                w.delete(1.0, tk.END)
                w.insert(1.0, str_choice)

    def set_hint(self, hint_str):
        """
        Not mandatory
        :param hint_str: A message that provides helps to find the correct answer(s)
        :return:
        """
        self.strvar_hint.set(hint_str)

    def set_info(self, info_str):
        """
        Not mandatory
        :param info_str: A message providing information when user gives a bad answer.
        :return:
        """
        self.strvar_info.set(info_str)

    def get_wave_tree(self):
        """
        Create an Element tagged 'wave' with values currently set.
        attributes : index, correct <-- all str
        subelements : title, item (<-- a choice)
        """
        wave_tree = et.Element('wave')
        wave_tree.set('index', str(self.index))
        wave_tree.set('correct', self.correctness)
        wave_tree.set('type', lf_tools.TYPE_MULTCHOICES)
        wave_tree.set('spd', self.strvar_speed.get())
        q = et.Element('title')
        q.text = self.question.get(1.0, tk.END)

        hint = et.Element('hint')
        hint.text = self.hint.get()

        info = et.Element('info')
        info.text = self.info.get()

        wave_tree.append(q)
        wave_tree.append(hint)
        wave_tree.append(info)
        for i in range(0, 4):
            c = et.Element('item')
            c.set('index', str(i))
            c.text = self.text_choice_list[i].get(1.0, tk.END)
            wave_tree.append(c)
        return wave_tree

    def get_title(self):
        return self.question.get(1.0, tk.END)
