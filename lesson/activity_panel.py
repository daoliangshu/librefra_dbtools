import tkinter as tk
from copy import deepcopy

from lxml import etree as ET

import lf_tools
from activity_design import activity_main_container
from state import STATUS

''' This panel display the activities designed for a given unit,
    QCM -> choose between several choices'''


class ActivityPanel(tk.Frame):
    """
        Panel that displays the activities attached to the lesson.
        It takes ActivityFrameUnit for representing an activity

    """

    def __init__(self, master, activity_list_tree=None):

        tk.Frame.__init__(self, master)
        '''State variables'''
        self.canvas_cur_y = 0  # height at which at component
        self.voc_count = 0

        # TreeElement of <activity_list> in <unit> tag of a lesson:
        self.xml_activity_list_tree = activity_list_tree

        self.title_frame = tk.Frame(self, master)
        '''Title Panel init'''
        label = tk.Label(self.title_frame,
                         text=lf_tools.menu_lesson.find('labels').
                         find('activity').text)
        label.pack()
        self.content_frame = tk.Frame(self)
        self.control_frame = tk.Frame(self.title_frame)
        self.title_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.content_frame.pack(side=tk.TOP, anchor=tk.CENTER)
        self.control_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.list_entry_canvas = tk.Canvas(self.content_frame,
                                           background="red",
                                           )
        self.list_entry_canvas.scrollY = tk.Scrollbar(self.content_frame,
                                                      orient=tk.VERTICAL)
        self.list_entry_canvas['yscrollcommand'] = self.list_entry_canvas. \
            scrollY.set
        self.list_entry_canvas.scrollY['command'] = self.list_entry_canvas.yview
        self.list_entry_canvas.scrollY.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_entry_canvas['bd'] = 5
        self.list_entry_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if self.xml_activity_list_tree is None:
            self.xml_activity_list_tree = []
        else:
            self.load_activities()

        '''Control Panel init'''
        button_add = tk.Button(self.control_frame,
                               text=lf_tools.menu_lesson.find('buttons').
                               find('add').text)
        button_add['command'] = self.on_add_activity
        button_add.pack(side=tk.LEFT)

    def load_activities(self):
        """
        Load from the xml_activity_tree the activities.
        xml_activity_tree should be first assigned
        :return:
        """
        self.canvas_cur_y = 0
        self.voc_count = 0
        self.list_entry_canvas.delete('all')
        for act in self.xml_activity_list_tree.iter('activity'):
            frame_unit = ActivityFrameUnit(self, 20,
                                           self.list_entry_canvas['width'])
            frame_unit.set_index(int(act.get('index')))
            self.list_entry_canvas.create_window((0, self.canvas_cur_y),
                                                 anchor=tk.NW, window=frame_unit)
            self.canvas_cur_y += 20
            print('scroll region :' + str(self.list_entry_canvas.bbox('all')))
            self.list_entry_canvas['scrollregion'] \
                = self.list_entry_canvas.bbox('all')
            frame_unit.bind("<Button-4>", self._on_wheel_up)
            frame_unit.bind("<Button-5>", self._on_wheel_down)
            for w in frame_unit.winfo_children():
                w.bind("<Button-4>", self._on_wheel_up)
                w.bind("<Button-5>", self._on_wheel_down)
            print('[activity_panel->before set]')
            frame_unit.set(act)
            self.voc_count += 1
            print('add')

    def get_activity_list(self):
        """
        Get the activity list of the lesson as a et.Element tagged <activity_list>
        :return:
        """
        activity_list = ET.Element('activity_list')
        print('on_get_activity_list__')
        for act in self.winfo_children():
            if isinstance(act, ActivityFrameUnit):
                print('activity_found __')
                activity_list.append(act.get_activity())
        activity_list.getroottree().write('./_activity_list.xml',
                                          pretty_print=True)
        return activity_list

    def on_add_activity(self):
        """
        Add a new activity to activity panel
        :return:
        """
        frame_unit = ActivityFrameUnit(self,
                                       20,
                                       self.list_entry_canvas['width'])
        frame_unit.set_index(self.voc_count)
        self.list_entry_canvas.create_window((0, self.canvas_cur_y),
                                             anchor=tk.NW,
                                             window=frame_unit)
        self.canvas_cur_y += 20
        print(('scroll region :' + str(self.list_entry_canvas.bbox('all'))))
        self.list_entry_canvas['scrollregion'] \
            = self.list_entry_canvas.bbox('all')
        frame_unit.bind("<Button-4>", self._on_wheel_up)
        frame_unit.bind("<Button-5>", self._on_wheel_down)
        for w in frame_unit.winfo_children():
            w.bind("<Button-4>", self._on_wheel_up)
            w.bind("<Button-5>", self._on_wheel_down)
        new_activity = ET.Element('activity',
                                  dict(index=str(self.voc_count)))
        new_activity.set('type', 'multiplechoices')
        new_activity.append(ET.Element('title'))
        new_activity.append(ET.Element('title_zh'))
        self.xml_activity_list_tree.append(new_activity)
        frame_unit.set(self.xml_activity_list_tree[self.voc_count])
        self.voc_count += 1

    def set_tree_element(self, component_index, db_table_code, word_id, trans_id):
        for item in self.xml_activity_list_tree:
            if int(item.get('index')) == int(component_index):
                item.set('type', str(db_table_code))
                wid = ET.Element('wid')
                wid.text = str(word_id)
                tid = ET.Element('tid')
                tid.text = str(trans_id)
                item.append(wid)
                item.append(tid)

    def set(self, activity_list_tress):
        self.xml_activity_list_tree = activity_list_tress
        self.load_activities()

    def _on_wheel_down(self, event):
        self.list_entry_canvas.yview_scroll(5, "units")

    def _on_wheel_up(self, event):
        self.list_entry_canvas.yview_scroll(-5, "units")


class ActivityFrameUnit(tk.Frame):
    """
    Graphic row representation of an 'activity' into the activity panel
    It gives basis information :
        -Activity title
        -type
    As well as buttons to edit/show xml_content
    'get_activity()' should be used to retrieve the activity as
    et.Element
    """

    def __init__(self, master=None, h=20, w=100):
        tk.Frame.__init__(self, master)
        self.root = master

        self.activity_tree = ET.Element('activity')
        self.activity_tree.append(ET.Element('title'))
        self.result = self.activity_tree  # Obtain dialog result
        self.cur_activity_element = self.activity_tree
        self.index = -1
        self['height'] = h
        self['width'] = w
        self.dialog_result = None
        self.strVar_index = tk.StringVar(self)
        self.strVar_index.set('[not set]')

        self.strVar_type = tk.StringVar(self)
        self.strVar_type.set('[not set]')

        self.trans_index = 0
        self.cur_activity_element = ET.Element('activity')

        self.lb_index = tk.Label(self, textvariable=self.strVar_index)
        self.lb_index.place(relx=0.0, rely=0.1, relw=0.1, relh=0.8)

        self.lb_type = tk.Label(self, textvariable=self.strVar_type)
        self.lb_type.place(relx=0.1, rely=0.1, relw=0.1, relh=0.8)

        # Title fr=0 zh=1
        self.strvar_title_fr_zh = [tk.StringVar(self), tk.StringVar(self)]
        self.lb_title_fr_zh = [tk.Label(self, textvariable=self.strvar_title_fr_zh[0]),
                               tk.Label(self, textvariable=self.strvar_title_fr_zh[1])]

        for i in range(0, 2):
            self.strvar_title_fr_zh[i].set('[not set]')
            self.lb_title_fr_zh[i].tag = i
            self.lb_title_fr_zh[i].bind("<Button-1>", self.on_switch_title_display)
        self.title_rel_place = [0.2, 0.1, 0.3, 0.8]
        self.lb_title_fr_zh[0].place(relx=self.title_rel_place[0],
                                     rely=self.title_rel_place[1],
                                     relw=self.title_rel_place[2],
                                     relh=self.title_rel_place[3])

        '''Show button'''
        self.btn_show = tk.Button(self,
                                  text=lf_tools.menu_lesson.find('buttons').find('show').text)
        self.btn_show['command'] = self.on_show
        self.btn_show.place(relx=0.6, rely=0.1, relw=0.2, relh=0.8)

        '''Edit button'''
        self.btn_edit = tk.Button(self,
                                  text=lf_tools.menu_lesson.find('buttons').find('edit').text)
        self.btn_edit['command'] = self.on_show
        self.btn_edit.place(relx=0.8, rely=0.1, relw=0.2, relh=0.8)

    def set(self, activity_tree):
        """
        :param activity_tree: Load settings of  an already existing activity, is et.Element
        :return:
        """
        self.cur_activity_element = deepcopy(activity_tree)
        self.result = self.cur_activity_element
        activity_type = lf_tools.menu_lesson. \
            find('activity').find('type'). \
            find(str(self.result.get('type'))).text
        self.strVar_type.set(activity_type)
        try:
            print(('title : ' + self.result.find('title').text))
            self.set_title(self.result.find('title').text, STATUS.TAG_FR)
            self.set_title(self.result.find('title_zh').text, STATUS.TAG_ZH)
        except:
            print('error : no title attribute in activity tree')
        self.strVar_index.set(self.result.get('index'))

    def set_index(self, index_int):
        self.index = index_int

    def set_title(self, title_str, tag_index=STATUS.TAG_FR):
        """
        :param title_str: Activity new title
        :param tag_index: fr=0, zh=1
        :return:
        """
        if 0 < tag_index > 1:
            print("Error:<activity_panel.py:set_title> index out of bound: " + str(tag_index))
            return
        self.strvar_title_fr_zh[tag_index].set(title_str)

    def get_title(self, tag_index=STATUS.TAG_FR):
        """
        Get the title according to the tag: fr=0, zh=1
        :return: Given title of the activity
        """
        if 0 < tag_index > 1:
            print("Error:<activity_panel.py:get_title> index out of bound: " + str(tag_index))
            return None
        return self.strvar_title_fr_zh[tag_index].get()

    def set_type(self, new_type):
        self.strVar_type.set(new_type)

    def get_type(self):
        return self.strVar_type.get()

    def get_activity(self):
        """
        :return: the activity as an et.Element
        """
        return self.result

    def on_switch_title_display(self, event):
        """
        Switch title fr<->zh when user click on title
        tag: fr=0, zh=1
        :param event:
        :return:
        """
        self.lb_title_fr_zh[event.widget.tag].place_forget()
        self.lb_title_fr_zh[1 - event.widget.tag].place(relx=self.title_rel_place[0],
                                                        rely=self.title_rel_place[1],
                                                        relw=self.title_rel_place[2],
                                                        relh=self.title_rel_place[3])

    def on_show(self):
        """
        Launch the dialog for designing activities
        Result of the dialog is stored in the self.result attribute
        :return: None
        """
        self.result = None
        mb = activity_main_container. \
            ActivityDesignBox(self, self.cur_activity_element)
        if self.result is None:
            '''
                result is given only if changed has been confirmed in dialog
                if canceled -> result is assigned the previous element
            '''
            self.result = self.cur_activity_element
        self.wait_window(mb.top)
        self.result.getroottree(). \
            write('./res/_show_after.xml',
                  pretty_print=True)
        self.set(self.result)
