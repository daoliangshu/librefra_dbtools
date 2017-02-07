import tkinter as tk
from tkinter import ttk

import db_helper
import lf_tools
from const_definitions import colors
from db_service import db_update
from dictionary_entries.noun_entry_frame import SubstEntryFrameUnit
from dictionary_entries.other_entry_frame import OtherEntryFrameUnit
from dictionary_entries.verb_entry_frame import VerbEntryFrameUnit
from service import content_setter as cs
from state import STATUS

"""
author:daoliangshu
"""


class EntryFrame(tk.Frame):
    """
    Container for the dictionary entry, as well as its controls
    """

    def __init__(self, master, root):
        tk.Frame.__init__(self, master)
        self.root = root
        self.buffered_entries = {lf_tools.SUBST: None,
                                 lf_tools.VERB: None,
                                 lf_tools.OTHER: None}

        self.current_page = {lf_tools.SUBST: [1, 1],
                             lf_tools.VERB: [1, 1],
                             lf_tools.OTHER: [1, 1]}
        self.max_entries_per_page = 40

        self.subst_frame_units = {}
        self.verb_frame_units = {}
        self.other_frame_units = {}

        self.frame_unit_map = {lf_tools.SUBST: self.subst_frame_units,
                               lf_tools.VERB: self.verb_frame_units,
                               lf_tools.OTHER: self.other_frame_units}

        self.current_table_index = 0
        self.count_word = {lf_tools.SUBST: 0,
                           lf_tools.VERB: 0,
                           lf_tools.OTHER: 0}
        self.parent = master
        self.header = {lf_tools.SUBST: None,
                       lf_tools.VERB: None,
                       lf_tools.OTHER: None}
        self.canvas_dic = {lf_tools.SUBST: None,
                           lf_tools.VERB: None,
                           lf_tools.OTHER: None}
        self.content = {lf_tools.SUBST: None,
                        lf_tools.VERB: None,
                        lf_tools.OTHER: None}
        self.init_canvases()
        self.bind('<Configure>', self._on_resize)

    def init_canvases(self):
        """
        Initializes the canvases and their corresponding headers
        :return: None
        """
        for k in self.header.keys():
            self.header[k] = tk.Frame(self, height="0.3i", width="2i")
            self.content[k] = tk.Frame(self)
            self.canvas_dic[k] = tk.Canvas(self.content[k],
                                           width="500",
                                           height="300",
                                           background="white",
                                           scrollregion=(0, 0, "500", "900"))
            self.canvas_dic[k].scrollY = tk.Scrollbar(self.content[k], orient=tk.VERTICAL)
            self.canvas_dic[k]['yscrollcommand'] = self.canvas_dic[k].scrollY.set
            self.canvas_dic[k].scrollY['command'] = self.canvas_dic[k].yview
            self.canvas_dic[k].scrollY.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas_dic[k].pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._init_headers()

    def _init_headers(self):
        """
        Initializes the header frames for each type of entry word frame
        :return:
        """
        for k, header_frame in self.header.items():
            # Places headers in the corresponding header frame
            my_heads = []
            my_places = []
            my_heads = cs.get_headers(k, header_frame)
            my_places = cs.get_place(k)
            for i in range(0, len(my_heads)):
                my_heads[i].place(relx=my_places[i][0],
                                  rely=my_places[i][1],
                                  relw=my_places[i][2],
                                  relh=my_places[i][3],
                                  )

    def set_verb_table(self, my_db_helper, str_to_search=None):
        """
        :param my_db_helper:  the DBHelper object from which to query entries
        :param str_to_search: If none, then all the entries are queried
        :return: None
        """
        self.set_table(my_db_helper, str_to_search, db_helper.VERB)

    def set_other_table(self, my_db_helper, str_to_search=None):
        """
        :param my_db_helper:  the DBHelper object from which to query entries
        :param str_to_search: If none, then all the entries are queried
        :return: None
        """
        self.set_table(my_db_helper, str_to_search, db_helper.OTHER)

    def get_frame_unit(self, db_table_code):
        """
        :param db_table_code: code of the db_table, as defined in DBHelper
        :return: Return a new instance of a frame unit, according to the db_table_code
        """
        if db_table_code == db_helper.SUBST:
            return SubstEntryFrameUnit(self.canvas_dic[db_table_code],
                                       self.canvas_dic[db_table_code].winfo_reqwidth(),
                                       20)
        elif db_table_code == db_helper.VERB:
            return VerbEntryFrameUnit(self.canvas_dic[db_table_code],
                                      self.canvas_dic[db_table_code].winfo_reqwidth(),
                                      20)
        elif db_table_code == db_helper.OTHER:
            return OtherEntryFrameUnit(self.canvas_dic[db_table_code],
                                       self.canvas_dic[db_table_code].winfo_reqwidth(),
                                       20)
        else:
            return None

    def previous_page(self):
        """
        Goes to the previous page. To avoid lagging, the entry canvases are limited to
        display at once only a certain number of entries ( = a page)
        :return: None
        """
        tb = STATUS.cur_workingtable
        if self.current_page[tb][0] >= 0:
            self.unselect_frame(STATUS.currentSelectedFrame[STATUS.cur_workingtable])
            self.set_page(self.current_page[tb][0] - 1, tb)
            self.current_page[tb][0] -= 1

    def next_page(self):
        """
        Goes to the next page. To avoid lagging, the entry canvases are limited to
        display at once only a certain number of entries ( = a page)
        :return: None
        """
        tb = STATUS.cur_workingtable

        if self.current_page[tb][0] <= self.current_page[tb][1]:
            self.unselect_frame(STATUS.currentSelectedFrame[STATUS.cur_workingtable])
            self.set_page(self.current_page[tb][0] + 1, tb)
            self.current_page[tb][0] += 1

    def set_page(self, page_index, db_table_code):
        """
        :param page_index: page number desired
        :param db_table_code: in order to find the corresponding entry canvas
        :return:
        """
        STATUS.currentSelectedFrame[db_table_code] = None
        STATUS.previousSelectedFrame[db_table_code] = None
        previous_word_count = self.count_word[db_table_code]
        self.count_word[db_table_code] = 0
        if page_index >= self.current_page[db_table_code][1]:
            return
        self.root.ENTRY_EDIT_PANEL.set_page(str(page_index) +
                                            '/' +
                                            str(self.current_page[db_table_code][1]))
        b = self.buffered_entries[db_table_code]
        start_i = self.max_entries_per_page * page_index
        end_i = min(start_i + self.max_entries_per_page, len(b))

        for i in range(start_i, end_i):
            if self.count_word[db_table_code] >= previous_word_count:
                frame_unit = self.get_frame_unit(db_table_code)
                frame_unit.name = "frame_unit" + str(self.count_word[db_table_code])
                self.canvas_dic[db_table_code]. \
                    create_window(
                    (0, self.count_word[db_table_code] * 20),
                    anchor=tk.NW,
                    window=frame_unit,
                    tags="frame" + str(self.count_word[db_table_code]))
                self.frame_unit_map[db_table_code][str(self.count_word[db_table_code])] \
                    = frame_unit
            else:
                frame_unit \
                    = self.frame_unit_map[db_table_code][str(self.count_word[db_table_code])]
            frame_unit.set_common(b[i])
            if db_table_code is lf_tools.SUBST:
                # Set column that are specific to 'subst' table
                frame_unit.set_genre(b[i]['genre'])
            elif db_table_code is lf_tools.VERB:
                # Set column that are specific to 'verb' table
                try:
                    frame_unit.set_type(lf_tools.hex_to_int(b[i]['type']))
                except:
                    frame_unit.set_type(0)
            elif db_table_code is lf_tools.OTHER:
                # Set column that are specific to 'other' table
                frame_unit.set_type(b[i]['type'])
                pass
            self.count_word[db_table_code] += 1
            if self.count_word[db_table_code] > self.max_entries_per_page:
                break
        if self.count_word[db_table_code] < previous_word_count:
            for j in range(self.count_word[db_table_code], previous_word_count + 1):
                self.canvas_dic[db_table_code].delete("frame" + str(j))
        self.canvas_dic[db_table_code]['scrollregion'] \
            = self.canvas_dic[db_table_code].bbox('all')
        if self.canvas_dic[db_table_code] is not None and isinstance(self.canvas_dic[db_table_code], tk.Canvas):
            self.propagate_binding(self.canvas_dic[db_table_code])
        self._on_resize()

    def set_table(self, my_db_helper, str_to_search, db_table_code):
        """
        Set the entry canvas of the corresponding db_table
        :param my_db_helper: DBHelper instance for querying entries
        :param str_to_search: if None, then query all the entries in the table
        :param db_table_code: as defined in DBHelper
        :return:
        """
        self.buffered_entries[db_table_code] \
            = my_db_helper.get_entries_it(db_table_code, str_to_search)
        self.current_page[db_table_code][0] = 0
        if self.buffered_entries[db_table_code] is None:
            return None
        entry_num = len(self.buffered_entries[db_table_code])
        self.current_page[db_table_code][1] = entry_num // self.max_entries_per_page
        if (entry_num % self.max_entries_per_page) >= 1:
            self.current_page[db_table_code][1] += 1

        self.set_page(0, db_table_code)

    def set_subst_table(self, my_db_helper, str_to_search):
        """
        Set the subst canvas according the pattern to search
        :param my_db_helper:
        :param str_to_search:
        :return:
        """
        self.set_table(my_db_helper, str_to_search, db_helper.SUBST)

    def _on_wheel_down(self, event=None):
        """
        :param event:
        :return:
        """
        self.canvas_dic[STATUS.cur_workingtable].yview_scroll(5, "units")

    def _on_wheel_up(self, event=None):
        """
        :param event:
        :return:
        """
        self.canvas_dic[STATUS.cur_workingtable].yview_scroll(-5, "units")

    def propagate_binding(self, canvas):
        """
        :param canvas:
        :return:
        """
        for wid in canvas.winfo_children():
            wid.bind("<Button-1>", self.on_is_select)
            wid.bind("<Button-4>", self._on_wheel_up)
            wid.bind("<Button-5>", self._on_wheel_down)
            wid.bind("<Enter>", self.enter_selection)
            wid.bind("<Leave>", self.leave_selection)
            wid['bg'] = colors.IDLE_BG
            for w2 in wid.winfo_children():
                if isinstance(w2, tk.Button) is False:
                    w2.bind('<Button-1>', self.on_is_select)
                w2.bind("<Button-4>", self._on_wheel_up)
                w2.bind("<Button-5>", self._on_wheel_down)
                w2.bind("<Enter>", self.enter_selection)
                w2.bind("<Leave>", self.leave_selection)
                w2['background'] = colors.IDLE_BG
                if isinstance(w2, tk.Entry):
                    w2.bind("<Key>", self.set_update_status_false)

    def enter_selection(self, event):
        """
        Triggered when focus enters the frame
        :param event:
        :return:
        """
        if isinstance(event.widget, tk.Frame):
            select_frame = event.widget
        else:
            select_frame = event.widget.master
        select_frame['bg'] = colors.ON_MOUSE_BG
        for wid in select_frame.winfo_children():
            if isinstance(wid, tk.Button):
                pass
            else:
                wid['background'] = colors.ON_MOUSE_BG
        self.canvas_dic[STATUS.cur_workingtable].focus_set()

    def leave_selection(self, event):
        """
        Triggered when focus leaves
        :param event:
        :return:
        """
        if isinstance(event.widget, tk.Frame):
            select_frame = event.widget
        else:
            select_frame = event.widget.master

        if select_frame == STATUS.currentSelectedFrame[STATUS.cur_workingtable]:
            select_frame['bg'] = colors.SELECTED_BG
            for wid in select_frame.winfo_children():
                if isinstance(wid, tk.Button) or \
                        isinstance(wid, ttk.Combobox) or \
                        isinstance(wid, tk.Label) or \
                        isinstance(wid, tk.Frame):
                    pass
                else:
                    wid['background'] = colors.SELECTED_BG
                    try:
                        wid['foreground'] = colors.SELECTED_FG
                    except:
                        pass

        else:
            self.unselect_frame(select_frame)

    def unselect_frame(self, frame_to_unselect):
        """
        Manage the settings to unselect a frame, like giving the
        the colors specific for idle state
        :param frame_to_unselect:
        :return:
        """
        if frame_to_unselect is not None:
            frame_to_unselect['bg'] \
                = colors.IDLE_BG
            for w in frame_to_unselect.winfo_children():
                if isinstance(w, tk.Button) or isinstance(w, ttk.Combobox):
                    pass
                else:
                    w['bg'] = colors.IDLE_BG
                    try:
                        w['fg'] = colors.IDLE_FG
                    except:
                        pass

    def _on_resize(self, event=None):
        new_width = self.canvas_dic[lf_tools.SUBST].winfo_width()
        if event is not None:
            new_width = event.width
        for canvas in self.canvas_dic.values():
            print(str(new_width))
            if event is None:
                canvas.itemconfigure('all',
                                     width=int(new_width))
            else:
                canvas.itemconfigure('all',
                                     width=int(new_width) - canvas.scrollY.winfo_width())

    def on_is_select(self, event):
        """
        Triggered when user clicks on an word entry
        :param event:
        :return:
        """
        selected_frame = event.widget.master
        if isinstance(event.widget, tk.Button):
            pass
        if isinstance(event.widget, tk.Frame):
            selected_frame = event.widget
        self.is_select(selected_frame)

    def is_select(self, selected_frame):
        """
        To call when a new word entry is selected. It set the current_selected_frame and
            previous_selected_frame in STATUS.
        It also propagates the new selected word to translation panel and attributes panel for
        panel
        :param selected_frame: the new selected entry frame
        :return:
        """
        self.set_update_status_false(selected_frame)
        if STATUS.currentSelectedFrame[STATUS.cur_workingtable] is not None:
            STATUS.currentSelectedFrame[STATUS.cur_workingtable].write_in_db()
        selected_frame['bg'] = colors.SELECTED_BG
        for w in selected_frame.winfo_children():
            if isinstance(w, tk.Button) or isinstance(w, ttk.Combobox):
                pass
            else:
                w['bg'] = colors.SELECTED_BG
                w['fg'] = colors.SELECTED_FG
        if STATUS.previousSelectedFrame[STATUS.cur_workingtable] != selected_frame:
            #  Previous selected frame return to non-selected frame
            #  (update color state)

            STATUS.previousSelectedFrame[STATUS.cur_workingtable] \
                = STATUS.currentSelectedFrame[STATUS.cur_workingtable]
            self.unselect_frame(STATUS.previousSelectedFrame[STATUS.cur_workingtable])
        # Update the translation frame( displaying translations corresponding
        # to the selection
        STATUS.currentSelectedFrame[STATUS.cur_workingtable] = selected_frame
        self.set_trans_frame(STATUS.currentSelectedFrame[STATUS.cur_workingtable])

        self.root.show_attributes()

    @staticmethod
    def set_trans_frame(selected_frame):
        '''
        Set the translationFrame according to the new frame_Unit selected.
        :param selected_frame:
        :return:
        '''
        STATUS.translationFrame.set_selected_word(selected_frame.
                                                  get_word())
        STATUS.translationFrame.set_tid(0,
                                        selected_frame.get_tid(0))
        STATUS.translationFrame.set_tid(1,
                                        selected_frame.get_tid(1))
        STATUS.translationFrame.set_tid(2,
                                        selected_frame.get_tid(2))
        STATUS.translationFrame.set_info(selected_frame.get_info())

    @staticmethod
    def update_entry_in_db(event):
        """
        :param event: the widget that called the event is a frame unit,
        and will be updated in db.
        :return:
        """
        db_update.send_update(event)

    def switch_table(self, cur_working_table_code):
        """
        Switch to the table corresponding to the code
        :param self:
        :param cur_working_table_code: as defined in DBHelper
        :return:
        """
        for k in self.header.keys():
            if k is not cur_working_table_code:
                self.header[k].pack_forget()
                self.content[k].pack_forget()
        self.header[cur_working_table_code].pack(side=tk.TOP, fill=tk.X, expand=True)
        self.content[cur_working_table_code].pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def set_update_status_false(self, selected_frame):
        if isinstance(selected_frame, tk.Frame):
            self.change_state_frame(selected_frame.nametowidget('_id'),
                                    lf_tools.NON_UPDATED)

    @staticmethod
    def change_state_frame(btn, lf_tools_state):
        """
        Change the indicator to inform wether the entry has been updated in db or not
        Indicator is simply the color of the id bucket in frame unit
        :param btn:
        :param lf_tools_state: lf_tools.UPDATED/NON_UPDATED
        :return:
        """
        if lf_tools_state == lf_tools.UPDATED:
            btn.config(background='#00AA00')
        elif lf_tools_state == lf_tools.NON_UPDATED:
            btn.config(background='#AA0000')
