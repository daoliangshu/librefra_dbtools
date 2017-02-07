import tkinter as tk

from lxml import etree as et

import lf_tools
from activity_design.order_wave_designer import OrderSettingUnit
from activity_design.qcm_wave_designer import QCMSettingUnit


class QCM_Settings(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.unit_height = 110
        '''state variables'''
        self.waves = []
        self.activity_wave_trees = []
        self.activity_tree = None
        self.yscroll_count = 0
        self.wave_count = 0
        self.activity_index = -1
        self.content_frame = tk.Frame(self, background='red')
        self.content_frame.pack(expand=True, fill=tk.X)

        self.canvas = tk.Canvas(self.content_frame)
        self.canvas.scrollY = tk.Scrollbar(self.content_frame,
                                           orient=tk.VERTICAL,
                                           background='blue')

        self.canvas['yscrollcommand'] = self.canvas.scrollY.set
        self.canvas.scrollY['command'] = self.canvas.yview
        self.canvas.scrollY.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas['bd'] = 1
        self.canvas.pack(expand=True, fill=tk.BOTH, anchor=tk.NE)

        self.control_frame = tk.Frame(self)
        self.control_frame.pack(expand=True, fill=tk.BOTH)
        btn_add_qcm = tk.Button(self.control_frame,
                                text=lf_tools.menu_lesson.find('buttons').find('add_qcm').text,
                                command=self.on_add_qcm)
        btn_add_order = tk.Button(self.control_frame,
                                  text=lf_tools.menu_lesson.find('buttons').find('add_order').text,
                                  command=self.on_add_order)
        btn_remove = tk.Button(self.control_frame,
                               text=lf_tools.menu_lesson.find('buttons').find('remove').text,
                               command=self.on_remove)
        btn_add_qcm.pack()
        btn_add_order.pack()
        btn_remove.pack()
        self.canvas.bind("<Configure>", self.on_resize)

    def propagate(self, setting_unit):
        setting_unit.bind('<Button-4>', self.on_wheel_up)
        setting_unit.bind('<Button-5>', self.on_wheel_down)
        for w in setting_unit.winfo_children():
            if isinstance(w, tk.Text) is False:
                w.bind("<Button-4>", self.on_wheel_up)
                w.bind("<Button-5>", self.on_wheel_down)
            if isinstance(w, tk.Frame):
                for w2 in w.winfo_children():
                    w.bind("<Button-4>", self.on_wheel_up)
                    w.bind("<Button-5>", self.on_wheel_down)

    def set(self, current_activity):
        """
        Forms the activity from an element tree given as parameter
        :param current_activity: the element tree from which to form the activity
        :return: None
        """
        self.activity_index = current_activity.get('index')

        for wave in current_activity.iter('wave'):
            self.on_add(None, wave)

    def set_index(self, activity_index):
        """
        Set the activity index
        :param activity_index:
        :return:
        """
        self.activity_index = activity_index

    def on_add(self, type, wave_tree=None):
        """
        Add an wave in the current activity
        :param wave_tree:
        :return:
        """
        self.canvas_width = self.master['width']
        bounds = self.canvas.bbox('all')  # returns a tuple like (x1, y1, x2, y2)
        if wave_tree is not None:

            if wave_tree.get('type', None) == lf_tools.TYPE_ORDER:
                setting_unit = OrderSettingUnit(self.content_frame,
                                                self.unit_height,
                                                self.canvas.winfo_width())
                setting_unit.set_wave_order(wave_tree.get('order'))
            else:
                setting_unit = QCMSettingUnit(self.content_frame,
                                              self.unit_height,
                                              self.canvas.winfo_width())
                setting_unit.set_correctness(wave_tree.get('correct'))
            self.waves.append(setting_unit)
            setting_unit.set_index(self.wave_count)
            setting_unit.set_speed(wave_tree.get('spd'))
            setting_unit.set_title(wave_tree.find('title').text)
            setting_unit.set_hint(wave_tree.find('hint').text)
            if wave_tree.find('hint') is None:
                print('hint empty')
            else:
                setting_unit.set_hint(wave_tree.find('hint').text)
            try:
                setting_unit.set_info(wave_tree.find('info').text)
            except:
                pass

            for activity_item in wave_tree.iter('item'):
                setting_unit.set_choice(activity_item.text,
                                        int(activity_item.get('index')))
            self.canvas.create_window((0,
                                       self.wave_count * self.unit_height),
                                      anchor=tk.NW,
                                      window=setting_unit)
            self.canvas['scrollregion'] = self.canvas.bbox('all')

            self.propagate(setting_unit)
            self.wave_count += 1
        else:
            if type == lf_tools.TYPE_ORDER:
                setting_unit = OrderSettingUnit(self.content_frame,
                                                self.unit_height,
                                                self.canvas.winfo_width())
            else:
                setting_unit = QCMSettingUnit(self.content_frame,
                                              self.unit_height,
                                              self.canvas.winfo_width())
            self.waves.append(setting_unit)
            setting_unit.set_index(self.wave_count)
            self.canvas.create_window((0, self.wave_count * self.unit_height),
                                      anchor=tk.NW, window=setting_unit)
            self.yscroll_count += self.unit_height
            self.canvas['scrollregion'] = self.canvas.bbox('all')
            self.propagate(setting_unit)
            self.wave_count += 1

    def on_resize(self, event):
        if self.canvas is None:
            return
        self.canvas.itemconfigure('all', width=self.canvas.winfo_width())

    def get_activity_tree(self):
        """Create a Element tagged 'activity', retrieves the current xml_content
            and return it.
            attrib: index, type(<---defined on menu_str.xml:'multiplechoices')
            subelements: title, wave

            note: title is added in the general ActivityDesignBox
        """
        activity_element = et.Element('activity')
        activity_element.set('type', 'multiplechoices')
        activity_element.set('index', str(self.activity_index))

        '''Append waves'''
        for w in self.content_frame.winfo_children():
            if isinstance(w, QCMSettingUnit) or isinstance(w, OrderSettingUnit):
                print('printing wave title = ' + w.get_title())
                activity_element.append(w.get_wave_tree())

        '''Debug log'''
        activity_element.getroottree().write('./res/testactivity.xml',
                                             pretty_print=True)
        return activity_element

    def on_remove(self):
        if len(self.waves) > 0:
            self.waves[len(self.waves) - 1].destroy()
            self.waves.remove(self.waves[len(self.waves) - 1])
            self.canvas['scrollregion'] = self.canvas.bbox('all')

    def on_wheel_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def on_wheel_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def on_add_qcm(self):
        self.on_add(lf_tools.TYPE_MULTCHOICES)

    def on_add_order(self):
        self.on_add(lf_tools.TYPE_ORDER)
