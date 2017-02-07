import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

from lxml import etree as ET

import lf_tools
from lesson import vocab_panel


class VocabularyListEditor(tk.Frame):
    def __init__(self, master, root):
        """
        This is the vocabulary editor, independent of the lesson editor,
        it contains the VocabularyPanel (contained also in the lesson view),
        but add some configuration like custom configuration like:
            title ( fr and zh), thematic, and level
        :param master:
        """
        tk.Frame.__init__(self, master)
        tk.Pack.config(self, fill=tk.BOTH, expand=True)
        self.root = root
        self.attr_frame = tk.Frame(self)
        self.filename = None

        '''
        Configuration of the list
        '''
        # (0)Give a title to the list (to be easily retrieved in app)
        common_title_frame = tk.Frame(self.attr_frame)

        temp_title_fr_frame = tk.Frame(common_title_frame)
        self.strvar_title_fr = tk.StringVar(temp_title_fr_frame)
        self.lb_title_fr = tk.Label(temp_title_fr_frame, text="titre:")
        self.entry_title_fr = tk.Entry(temp_title_fr_frame, textvariable=self.strvar_title_fr)
        self.lb_title_fr.pack(side=tk.LEFT)
        self.entry_title_fr.pack(side=tk.LEFT, fill=tk.X, expand=True)
        temp_title_fr_frame.pack(fill=tk.X)

        temp_title_zh_frame = tk.Frame(common_title_frame)
        self.strvar_title_zh = tk.StringVar(temp_title_zh_frame)
        self.lb_title_zh = tk.Label(temp_title_zh_frame, text="title_zh:")
        self.entry_title_zh = tk.Entry(temp_title_zh_frame, textvariable=self.strvar_title_zh)
        self.lb_title_zh.pack(side=tk.LEFT)
        self.entry_title_zh.pack(side=tk.LEFT, expand=True, fill=tk.X)
        temp_title_zh_frame.pack(fill=tk.X)
        common_title_frame.pack(side=tk.TOP, fill=tk.X)

        # (1)Config category/thematic of the list (predefined in xml res)
        frame_thematic = tk.Frame(self.attr_frame)
        self.strvar_category = tk.StringVar(frame_thematic)
        self.lb_thematic = tk.Label(frame_thematic, text="thematic")
        self.cb_choose_list_theme = ttk.Combobox(frame_thematic,
                                                 textvariable=self.strvar_category,
                                                 state='readonly')
        frame_thematic.pack(side=tk.TOP, fill=tk.X)
        self.lb_thematic.pack(side=tk.LEFT)
        self.cb_choose_list_theme.pack(side=tk.LEFT, fill=tk.X, expand=True)
        values = []
        self.cat_map = {}
        default_cat_index = -1

        count = 0
        for value in lf_tools.menu_global.find('categories').iter():
            if value.tag == 'categories':
                continue
            if value.tag == 'no':
                default_cat_index = count
            self.cat_map[value.text] = value.tag
            values.append(value.text)
            count += 1
        print(self.cat_map)
        self.cb_choose_list_theme.config(values=values)
        self.cb_choose_list_theme.current(default_cat_index)
        self.cb_choose_list_theme.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # (2)Config difficulty level
        frame_level = tk.Frame(self.attr_frame)
        self.strvar_level = tk.IntVar(frame_level)
        self.lb_level = tk.Label(frame_level, text="level:")
        varLevel = ['初級', '中級', '高級']
        self.cb_choose_list_level = ttk.Combobox(frame_level,
                                                 value=varLevel,
                                                 textvariable=self.strvar_level,
                                                 state='readonly')
        self.cb_choose_list_level.current(0)

        self.lb_level.pack(side=tk.LEFT)
        self.cb_choose_list_level.pack(side=tk.LEFT)
        frame_level.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.main_frame = tk.Frame(self)
        self.vocab_list_panel = vocab_panel. \
            VocabularyPanel(self.main_frame)

        ''' packing'''
        self.attr_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.vocab_list_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.xml_root = ET.Element('root')

        self.set_toplevel_menu()

    def set_toplevel_menu(self):
        menu_strings = lf_tools.menu_lesson.find('menu').find('file')
        print(menu_strings.find('open').text)
        # create a toplevel menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar)
        print(self.master)
        filemenu.add_command(label=menu_strings.find('new').text,
                             command=self.quit)
        filemenu.add_command(label=menu_strings.find('open').text,
                             command=self.on_open_file)
        filemenu.add_command(label=menu_strings.find('save').text,
                             command=self.on_save)
        filemenu.add_command(label=menu_strings.find('saveas').text,
                             command=self.on_save_as)
        filemenu.add_command(label=menu_strings.find('quit').text,
                             command=self.quit)
        menubar.add_cascade(label=menu_strings.find('tag').text,
                            menu=filemenu)
        # display the menu
        self.master.config(menu=menubar)

    def on_open_file(self):
        self.filename = askopenfilename(initialdir="./res/")
        self.xml_root = ET.parse(self.filename)
        self.xml_root = self.xml_root.getroot()
        self.display_file()

    def on_save(self):
        pass

    def on_save_as(self):
        """
        Save the vocabulary list in a user defined file
        :return: None
        """
        fn = asksaveasfilename(initialdir="./res/")
        if fn is None:
            return
        self.filename = fn

        if self.xml_root.find('category') is None:
            cat = ET.Element('category')
            cat.text = self.cat_map[self.strvar_category.get()]
            self.xml_root.append(cat)
        else:
            self.xml_root.find('category').text = self.cat_map[self.strvar_category.get()]
        if self.xml_root.find('vocabulary') is None:
            self.xml_root.append(self.vocab_list_panel.get_vocabulary_tree())
        else:
            element_to_remove = self.xml_root.find('vocabulary')
            element_to_remove.getparent().remove(element_to_remove)
            self.xml_root.append(self.vocab_list_panel.get_vocabulary_tree())

        voc = self.xml_root.find('vocabulary')
        if voc.find('title_fr') is None:
            cat = ET.Element('title_fr')
            cat.text = self.strvar_title_fr.get()
            voc.append(cat)
        else:
            voc.find('title_fr').text = self.strvar_title_fr.get()

        if voc.find('title_zh') is None:
            cat = ET.Element('title_zh')
            cat.text = self.strvar_title_zh.get()
            voc.append(cat)
        else:
            voc.find('title_zh').text = self.strvar_title_zh.get()
        if voc.find('level') is None:
            cat = ET.Element('level')
            cat.text = str(self.cb_choose_list_level.current())
            voc.append(cat)
        else:
            voc.find('level').text = str(self.cb_choose_list_level.current())

        try:
            self.xml_root.write(self.filename, pretty_print=True)
        except:
            self.xml_root.getroottree().write(self.filename, pretty_print=True)

    def display_file(self):
        if self.xml_root.find('vocabulary') is not None:
            voc = self.xml_root.find('vocabulary')
            thematic = self.xml_root.find('category').text
            if thematic is not None:
                print(thematic)
                for k, value in self.cat_map.items():
                    if value == thematic:
                        print('thematic: ' + thematic + '   value:' + value)
                        self.cb_choose_list_theme.set(k)
            else:
                self.cb_choose_list_theme.current(0)
            self.vocab_list_panel.set(self.xml_root.find('vocabulary'))

            if voc.find('title_fr') is not None:
                self.strvar_title_fr.set(voc.find('title_fr').text)
            else:
                self.strvar_title_fr.set(None)

            if voc.find('title_zh') is not None:
                self.strvar_title_zh.set(voc.find('title_zh').text)
            else:
                self.strvar_title_zh.set(None)

            if voc.find('level') is not None:
                self.cb_choose_list_level.current(int(voc.find('level').text))
            else:
                self.cb_choose_list_level.current(0)
