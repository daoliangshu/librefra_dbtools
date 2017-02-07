import tkinter as tk
from tkinter import ttk

from lxml import etree as et

import lf_tools
from activity_design import qcm_activity_designer


class ActivityDesignBox(object):
    """
    Dialog for designing an activity
    Common to all activities : title, type
    Settings are specifics for each kind of types:
        ->QCMSetting for multiplechoices type
    """

    def __init__(self, parent, current_activity):
        """
        current_activity is an et.Element from which it takes activity
            setting.
        When this dialog is close with 'confirm' button, current_activity is
        updated with new current activity xml_content (confirm method)
        :param parent:
        :param current_activity:
        """

        self.top = tk.Toplevel(parent)
        self.root = parent
        self.cur_activity_element = current_activity
        if self.cur_activity_element is None:
            print('error : activity tree not provided in ActivityDesignBox')
            return

        frm = tk.Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill='both', expand=True)

        # Top panel init
        self.top_frame = tk.Frame(frm)
        self.top_frame.pack(expand=True, fill=tk.BOTH)
        lb_title = tk.Label(self.top_frame,
                            text=lf_tools.menu_lesson.find('labels').find('title').text)
        lb_title.pack()
        self.strvar_title = []
        tmp_frame = []
        for i in range(0, 2):
            tmp_frame.append(tk.Frame(self.top_frame))
            tmp_frame[i].pack(side=tk.LEFT)
            self.strvar_title.append(tk.StringVar(tmp_frame[i]))
            title_entry = tk.Entry(tmp_frame[i],
                                   textvariable=self.strvar_title[i])
            title_entry.pack()

        lb_type = tk.Label(self.top_frame,
                           text=lf_tools.menu_lesson.find('labels').find('type').text)
        lb_type.pack()

        # Type combobox initialization
        self.type_map = {}
        self.cb_values = []  # combobox type values
        self.strvar_activity_type = tk.StringVar(self.top_frame)
        for i in lf_tools.menu_lesson.find('activity').find('type').iter():
            if i.tag == 'type':
                continue
            self.type_map[i.tag] = i.text
            self.cb_values.append(i.text)
        self.cb_type = ttk.Combobox(self.top_frame,
                                    values=self.cb_values,
                                    textvariable=self.strvar_activity_type,
                                    state='readonly'
                                    )
        self.cb_type.bind("<<ComboboxSelected>>", self._on_type_selected)
        self.cb_type.pack()

        self.cb_type.current(self.get_type_index())

        """
        setting_frame : Contains current activity type specific xml_content
        ->QCM_Settings for ''multiplechoice' type
        """
        self.settings_frame = tk.Frame(self.top)
        self.current_panel = None
        self.panel = qcm_activity_designer. \
            QCM_Settings(self.settings_frame)
        self.settings_frame.pack(expand=True, fill=tk.BOTH)

        confirm_button = tk.Button(frm,
                                   text=lf_tools.menu_lesson.find('buttons').
                                   find('confirm').text,
                                   command=self.confirm)
        confirm_button.pack()
        self.strvar_title[0].set(self.cur_activity_element.find('title').text)
        self.strvar_title[1]. \
            set(self.cur_activity_element.find('title_zh').text)
        multiplechoices_t = lf_tools.menu_lesson.find('activity'). \
            find('type'). \
            find('multiplechoices').text
        if self.strvar_activity_type.get() == multiplechoices_t:
            self.current_panel = self.panel
        if self.current_panel is not None:
            self.current_panel.set(self.cur_activity_element)
        self._on_type_selected()

    def set(self, new_current_tree):
        """
        Not yetimplemented
        :param new_current_tree:
        :return:
        """
        # self.cur_activity_element
        self.cb_type.current(self.get_type_index())

    def get_type_index(self):
        """
        Type index is used to choose the correct panel to edit
        :return:
        """
        activity_type = self.type_map[self.cur_activity_element.get('type')]
        for i in range(0, len(self.cb_values)):
            if self.cb_values[i] == activity_type:
                return i

    def get_title(self, index=0):
        """
         index = 0 represents the french title of the activity, whereas 1 is
         the chinese one.
        :param index:
        :return:
        """
        return self.strvar_title[index].get()

    def confirm(self):
        """
        Close the dialog, assigning the new status of the activity to its parent
        :return:
        """
        self.cur_activity_element = self.current_panel.get_activity_tree()
        title_fr = et.Element('title')
        title_zh = et.Element('title_zh')
        title_fr.text = self.get_title(0)
        title_zh.text = self.get_title(1)
        self.cur_activity_element.insert(0, title_fr)
        self.cur_activity_element.insert(1, title_zh)
        self.cur_activity_element.getroottree(). \
            write('./res/newactivity_hudada.xml', pretty_print=True)
        self.root.result = self.cur_activity_element
        print('passed by confirm')
        self.print_information(self.cur_activity_element)
        self.top.destroy()

    @staticmethod
    def print_information(activity_element):
        """
        Print the top first tree level of the activity_element
        :param activity_element:
        :return:
        """
        for child in activity_element:
            print(child.tag, child.attrib, child.text)
            for child2 in child:
                print('___ ' + child2.tag, child2.attrib, child2.text)

    def get_selection(self):
        pass

    def _on_type_selected(self, event=None):
        """
        Trigger when user changed activity type
        :param _:
        :return:
        """
        value = self.strvar_activity_type.get()
        for key, item_value in self.type_map.items():
            if item_value == value:
                for frame_child in self.settings_frame.winfo_children():
                    frame_child.pack_forget()
                self.settings_frame.pack_forget()
                if key == 'multiplechoices':
                    # display setting for multiplechoices type ( qcm)
                    for child in self.settings_frame.winfo_children():
                        if isinstance(child,
                                      qcm_activity_designer.QCM_Settings):
                            child.pack(expand=True, fill=tk.BOTH)
                            self.current_panel = child
                else:
                    # Display other kind of activity
                    for child in self.settings_frame.winfo_children():
                        if not isinstance(child,
                                          qcm_activity_designer.QCM_Settings):
                            child.pack(expand=True, fill=tk.BOTH)
                            self.current_panel = child
        self.settings_frame.pack(expand=True, fill=tk.BOTH)
