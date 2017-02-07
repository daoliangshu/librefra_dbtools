import tkinter as tk
from tkinter import ttk

import lf_tools
from state import STATUS


class VocabBoxDesign(object):
    root = None

    def __init__(self, parent, msg):

        self.top = tk.Toplevel(parent)
        self.parent = parent

        self.word_choices = {}
        self.trans_map = {}  # retrieving trans_id using trans_str as key
        print('trans_map reset')
        self.current_item = None
        frm = tk.Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill=tk.BOTH, expand=True)

        frame_genre = tk.Frame(frm)
        self.strVar_voc_genre = tk.StringVar(frame_genre)

        ''' SET FROM WHICH TABLE THE WORD COMEs FROM '''
        self.current_workingtable = lf_tools.SUBST
        self.genre_map = {
            lf_tools.menu_global.find('labels').find('subst').text: lf_tools.SUBST,
            lf_tools.menu_global.find('labels').find('verb').text: lf_tools.VERB,
            lf_tools.menu_global.find('labels').find('other').text: lf_tools.OTHER
        }
        self.genre_list = [lf_tools.menu_global.find('labels').find('subst').text,
                           lf_tools.menu_global.find('labels').find('verb').text,
                           lf_tools.menu_global.find('labels').find('other').text
                           ]

        lb_genre = tk.Label(frame_genre,
                            text=lf_tools.menu_global.find('labels').find('genre').text)
        cb_genre = ttk.Combobox(frame_genre,
                                values=self.genre_list,
                                textvariable=self.strVar_voc_genre,
                                font=("Helvetica", 20))
        cb_genre.bind('<<ComboboxSelected>>', self.on_combobox_selected_genre)
        cb_genre.current(0)

        frame_fr = tk.Frame(frm)
        self.strvar_word = tk.StringVar(frame_fr)
        lb_fr_word = tk.Label(frame_fr,
                              text=lf_tools.menu_lesson.find('labels').find('content_fr').text)
        cb_fr_word = ttk.Combobox(frame_fr,
                                  textvariable=self.strvar_word,
                                  font=("Helvetica", 20))
        cb_fr_word.bind('<KeyRelease>', self.on_typing)
        cb_fr_word.bind("<<ComboboxSelected>>", self.on_combobox_selected_word)

        self.values1 = []
        cb_fr_word['values'] = self.values1
        self.wordbox = cb_fr_word
        ''' Selection of one of his translation (translations should
            be first given to the word
         '''
        frame_zh = tk.Frame(frm)

        lb_zh_word = tk.Label(frame_zh,
                              text=lf_tools.menu_lesson.find('labels').find('content_zh').text)

        self.strVar_currentTrans = tk.StringVar(frame_zh)
        self.cb_zh_word = ttk.Combobox(frame_zh,
                                       textvariable=self.strVar_currentTrans,
                                       font=("Helvetica", 20),
                                       state='readonly')
        self.cb_zh_word.bind("<<ComboboxSelected>>", self.on_combobox_selected_trans)

        self.values2 = []
        self.cb_zh_word['values'] = self.values2

        self.transbox = self.cb_zh_word

        b_cancel = tk.Button(frm, text='Cancel')
        b_cancel['command'] = self.top.destroy

        b_ok = tk.Button(frm,
                         text=lf_tools.menu_lesson.find('buttons').find('confirm').text)
        b_ok['command'] = self.confirm

        frame_genre.pack(side=tk.LEFT, expand=True)
        frame_fr.pack(side=tk.LEFT, expand=True)
        frame_zh.pack(side=tk.LEFT, expand=True)
        lb_genre.pack(side=tk.TOP, expand=True)
        cb_genre.pack(side=tk.TOP, expand=True)
        lb_fr_word.pack(side=tk.TOP)
        cb_fr_word.pack(side=tk.TOP)
        lb_zh_word.pack(side=tk.TOP)
        self.cb_zh_word.pack(side=tk.TOP)

        b_cancel.pack(side=tk.BOTTOM, padx=4, pady=4)
        b_ok.pack(side=tk.LEFT)

    def confirm(self):
        '''Should assign a et.Element representing the item in dialog_result'''
        self.parent.dialog_result = self.current_item
        self.top.destroy()

    def get_selection(self):
        word = self.wordbox.get()
        trans = self.transbox.get()
        trans_id_selected = None
        word_id = self.word_choices[word][0]

        for i in range(1, 4):
            if STATUS.dbHelper.get_translation_by_id(self.word_choices[word][i]) == trans:
                trans_id = self.word_choices[word][i]
        return (word_id, word), (trans_id, trans)

    def on_typing(self, event):
        if STATUS.dbHelper is None:
            return
        else:
            entries = STATUS.dbHelper. \
                get_entries_it(self.current_workingtable, event.widget.get())
            self.strvar_word = []
            self.word_choices = {}
            for row in entries:
                self.strvar_word.append(row['word'])  # word
                self.word_choices[row['word']] = (row['_id'], row['trans_id1'], row['trans_id2'], row['trans_id3'])
            event.widget['values'] = self.strvar_word

    def on_combobox_selected_genre(self, event):
        try:
            self.current_workingtable = self.genre_map[event.widget.get()]
            print('cur_working table is now: ' + str(self.current_workingtable))
        except:
            pass

    def on_combobox_selected_word(self, event):
        value = event.widget.get()  # retrieve word selected
        wid = self.word_choices[value][0]
        self.current_item = {}
        self.current_item['word'] = value
        self.current_item['wid'] = wid
        self.current_item['type'] = self.current_workingtable
        self.current_item['trans'] = -1
        self.current_item['tid'] = -1
        print('trans_map reset')
        self.trans_map = {}

        idx = 1
        self.new_cb_values = []
        while self.word_choices[value][idx] is not None:
            transids = self.word_choices[value][idx].split(',')
            cb_row = ''
            for i in range(0, len(transids)):
                if i != 0:
                    cb_row += ','
                trans_str = STATUS.dbHelper.get_translation_by_id(transids[i])
                cb_row += str(trans_str)

            self.new_cb_values.append(cb_row)
            self.trans_map[cb_row] = transids
            print('mapping --> ' + str(cb_row) + ' has id : ' + str(transids))
            print('map : ' + str(self.trans_map[cb_row]))
            idx += 1
            if idx == 4:
                break

            self.transbox['values'] = self.new_cb_values
        if len(self.new_cb_values) <= 0:
            self.transbox['values'] = []
            self.transbox.set('')
        else:
            self.transbox.current(0)
            self.current_item['trans'] = self.transbox.get()
            self.current_item['tid'] = self.trans_map[self.transbox.get()]

        print(self.new_cb_values)

    def on_combobox_selected_trans(self, event):
        trans = event.widget.get()
        if self.current_item['word'] is None:
            self.current_item['tid'] = -1
            self.current_item['trans'] = -1
            return
        else:
            self.current_item['trans'] = trans
            print((trans + ' --> map to : ' + str(self.trans_map[trans])))
            self.current_item['tid'] = self.trans_map[trans]
