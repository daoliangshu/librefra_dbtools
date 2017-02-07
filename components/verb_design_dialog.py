# -*- coding: utf-8 -*-
import tkinter as tk

import lf_tools


class VerbBoxDesign(object):
    root = None

    def __init__(self, parent, verb_str):
        self.top = tk.Toplevel(parent)
        self.top.minsize(600, 400)
        self.parent = parent
        self.verb = verb_str
        frm = tk.Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill='both', expand=True)

        self.display = ['present',
                        'simple_past',
                        'imparfait',
                        'futur'
                        ]

        self.frames = []
        count = 0
        for i in self.display:
            print(i)
            self.frames.append(VerbDisplayer(frm, self.verb, i))
            self.frames[count].pack(side=tk.LEFT, expand=True)
            count += 1

    def confirm(self):
        self.top.destroy()
        pass

    def get_selection(self):
        pass

    def on_typing(self, event):
        pass

    def on_combobox_selected_word(self, event):
        pass

    def on_combobox_selected_trans(self, event):
        pass


class VerbDisplayer(tk.Frame):
    """
    Displays conjugated forms of a verb
    """

    def __init__(self, parent, verb, tense_str):
        """
        :param parent: VerbBoxDesign class
        :param verb: verb to conjugate
        :param tense_str: tense
        """
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.tag = tense_str
        self.config(borderwidth=4, relief='ridge')
        label_title = tk.Label(self)
        label_title['text'] = lf_tools.menu_verb.find('term'). \
            find(tense_str).find('name').text
        label_title['background'] = "#000000"
        label_title['foreground'] = "#FFFF00"
        label_title.grid(row=0, column=0, columnspan=2, sticky=tk.W + tk.E)
        persons = ['je', 'tu', 'elle', 'nous', 'vous', 'ils']
        conj = None

        if tense_str == 'present':
            conj = lf_tools.V.conjugate_present(verb)
        elif tense_str == 'simple_past':
            conj = lf_tools.V.conjugate_simple_past(verb)
        elif tense_str == 'imparfait':
            conj = lf_tools.V.conjugate_imparfait(verb)
        elif tense_str == 'futur':
            conj = lf_tools.V.conjugate_futur(verb)
        for i in range(1, 7):
            c = conj

            l_person = tk.Label(self, text=persons[i - 1])
            l_conjugation = tk.Label(self, text=c[i - 1])
            l_person.grid(row=i, column=0)
            l_conjugation.grid(row=i, column=1)
