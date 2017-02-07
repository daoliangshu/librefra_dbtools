import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename

from lxml import etree as et

import lf_tools
from components import explanation_panel
from lesson import activity_panel
from lesson import lesson_content_frame as lc
from lesson import lesson_information_panel as les_info
from lesson import vocab_panel

TAG_SRC = 1
TAG_DST = 0
TAG_FR = 0
TAG_ZH = 1


class LessonControlPanel(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        button_add = tk.Button(self,
                               text=lf_tools.menu_lesson.
                               find('buttons').find('add').text)
        button_add.config(command=master.on_add_line)
        button_add.pack(side=tk.LEFT)
        button_delete = tk.Button(self,
                                  text=lf_tools.menu_lesson.
                                  find('buttons').find('delete').
                                  text)
        button_delete.config(command=master.on_delete_line)
        button_delete.pack(side=tk.LEFT)


class LessonFrame(tk.Frame):
    def __init__(self, master, root):
        tk.Frame.__init__(self, master)
        # tk.Pack.config(self)
        self.root = root
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master = master

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)

        self['bg'] = '#555555'
        # State Variables
        self.filename = None

        # Control Panel : Add/Delete btn
        self.control_panel = LessonControlPanel(self)

        # Frame containing informations about the lesson
        self.info_panel = les_info.LessonInformationPanel(self)
        self.info_panel.grid(in_=frame_left)
        self.control_panel.grid(in_=frame_left)

        # Container for lesson text editors
        self.lesson_content = [
            lc.LessonContentFrame(self, tag=TAG_FR),
            lc.LessonContentFrame(self, tag=TAG_ZH)
        ]

        self.lesson_content[0].grid(in_=frame_left, sticky=tk.NSEW)
        self.lesson_content[1].grid(in_=frame_left, sticky=tk.NSEW)
        unit = self.create_new_file()
        frame_left.grid(row=0, column=0, rowspan=3, sticky=tk.NSEW)

        # Vocabulary Panel
        self.vocab_list_panel = vocab_panel.VocabularyPanel(self)
        self.vocab_list_panel.grid(in_=frame_right, row=0)
        # Activity Panel
        self.activity_list_panel = activity_panel.ActivityPanel(self,
                                                                unit.find('activity_list'))

        self.activity_list_panel.grid(in_=frame_right, row=2)

        # Explanation Display Panel
        self.explanation_panel = explanation_panel.ExplanationPanel(self)
        self.explanation_panel.grid(in_=frame_right, row=1)
        frame_right.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW)

        for i in range(0, 3):
            self.rowconfigure(i, weight=1)
            frame_right.rowconfigure(i, weight=1)
        # TEST : Display a letter format
        """self.top_letter_frame = []
        self.strvar_top_date_and_location = []
        self.e_letter_top_date_and_location = []
        self.strvar_top_politeness = []
        self.e_letter_top_start_politeness = []

        self.bottom_letter_frame = []
        self.strvar_end_signature = []
        self.e_letter_bottom_signature = []
        self.strvar_end_politeness = []
        self.e_letter_bottom_end_politeness = []"""

        for i in range(0, 2):
            if i == 1:
                parent = self.lesson_content[0]
            else:
                parent = self.lesson_content[1]

                # Initialize Letter format [ TOP FRAME ]
                # self.top_letter_frame.append(tk.Frame(parent))
                # self.strvar_top_date_and_location.append(tk.StringVar(parent))
                # self.strvar_top_date_and_location[i].set('A Paris, le 21 Octobre 2018,')
                # self.e_letter_top_date_and_location.append(tk.Entry(self.top_letter_frame[i],
                #                                           textvariable=self.strvar_top_date_and_location[i]))
                # self.e_letter_top_date_and_location[i].pack(side=tk.TOP, anchor=tk.E)
                # self.strvar_top_politeness.append(tk.StringVar(self.top_letter_frame[i]))
                # self.strvar_top_politeness[i].set("Ma chère fille,")
                # self.e_letter_top_start_politeness.append(tk.Entry(self.top_letter_frame[i],
                #                                                   textvariable=self.strvar_top_politeness[i]))
                # self.e_letter_top_start_politeness[i].pack(side=tk.TOP,
                #                                           anchor=tk.W,
                #                                           padx=10)

                # Initialize Letter format [BOTTOM FRAME]
                # self.bottom_letter_frame.append(tk.Frame(parent))
                # self.strvar_end_signature.append(tk.StringVar(self.bottom_letter_frame[i]))
                # self.strvar_end_signature[i].set("Ta maman qui t'aime")
                # self.e_letter_bottom_signature.append(tk.Entry(self.bottom_letter_frame[i],
                #                                               textvariable=self.strvar_end_signature[i]))
                # self.e_letter_bottom_signature[i].pack(side=tk.BOTTOM, anchor=tk.E)
                # self.strvar_end_politeness.append(tk.StringVar(self.bottom_letter_frame[i]))
                # self.strvar_end_politeness[i].\
                #   set("Je t'embrasse, en te souhaitant un bon séjour,")
                # self.e_letter_bottom_end_politeness.append(tk.Entry(self.bottom_letter_frame[i],
                #                                           textvariable=self.strvar_end_politeness[i]))
                # self.e_letter_bottom_end_politeness[i].pack(side=tk.BOTTOM, anchor=tk.W)
                # self.top_letter_frame[i].pack(side=tk.TOP, fill=tk.X)
                # self.bottom_letter_frame[i].pack(side=tk.TOP, fill=tk.X)
        self._init_toplevel_menu()
        self.load_file(unit)
        self.pack(expand=True, fill=tk.BOTH)

    def on_closing(self):
        try:
            # When lesson frame is attached to the complete prog.
            self.root.callback_reset_lesson()
        except:
            pass
        self.destroy()
        self.master.destroy()

    def switch_editor_focus(self, index_to_focus=0):
        self.lesson_content[index_to_focus].process_focus()

    def set_type(self, selected_type):
        """
        Change the type of the lesson content
        :param event:
        :return:
        """

        for i in range(0, 2):
            self.lesson_content[i].set_type(selected_type)
            """parent = self.zh_editor_frame
            if i != 1:
                parent = self.fr_editor_frame
            for child in parent.winfo_children():
                child.pack_forget()
            if selected_type == 'letter':
                self.top_letter_frame[i].pack(side=tk.TOP, fill=tk.X)
                self.main_content_frame[i].pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                self.bottom_letter_frame[i].pack(side=tk.TOP, fill=tk.X)
            elif selected_type == 'normal':
                self.main_content_frame[i].pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            elif selected_type == 'poetry':
                self.main_content_frame[i].pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.CENTER)
            elif selected_type == 'dialog':
                self.main_content_frame[i].pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.CENTER)
            for j in range(0, self.listbox[i].size()):
                self.listbox[i].itemconfig(j, )"""

    def _init_toplevel_menu(self):
        """
        Initialization of the menu
        :return:
        """
        menu_strings = lf_tools.menu_lesson.find('menu').find('file')
        print(menu_strings.find('open').text)
        # create a toplevel menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar)
        print(self.master)
        filemenu.add_command(label=menu_strings.find('new').text,
                             command=self._on_new_file)
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
        """
        Choose a file with extension lec to open
        :return:
        """
        self.filename = askopenfilename(initialdir="./res/")
        self.file_tree = et.parse(self.filename)
        unit = self.file_tree.find('unit')
        self.load_file(unit)

    def load_file(self, unit_el):
        """
        Load the lesson content and display it
        :return: None
        """
        if unit_el is None:
            return
        content = [unit_el.find('content_fr'),
                   unit_el.find('content_zh')]
        if unit_el.get('level') is not None:
            self.info_panel.set_level(int(unit_el.get('level')))
        if unit_el.get('type') is not None:
            self.info_panel.set_type(unit_el.get('type'))
        else:
            self.info_panel.set_type('normal')
        if unit_el.get('theme') is not None:
            self.info_panel.set_theme(unit_el.get('theme'))

        for i in range(0, 2):
            self.lesson_content[i]. \
                load_content(content[i])
            sufix = ''
            if i == 1:
                sufix = '_zh'
            self.lesson_content[i]. \
                set_title(unit_el.find('title' + sufix).text)

        self.activity_list_panel.set(unit_el.find('activity_list'))
        if unit_el.find('vocabulary') is not None:
            self.vocab_list_panel.set(unit_el.find('vocabulary'))

    def _load_letter(self):
        """
        Is called when the file opened is of type 'letter'
        Assign the letter specific headers
        :return:
        """
        # Initialize Letter format [ TOP FRAME ]
        for tag_index in range(0, 2):
            tag_suffix = '_fr'
            if tag_index == 1:
                tag_suffix = '_zh'
            self.strvar_top_date_and_location[tag_index].set(self.unit.find('letter_header1' + tag_suffix).text)
            self.strvar_top_politeness[tag_index].set(self.unit.find('letter_header2' + tag_suffix).text)
            self.strvar_end_politeness[tag_index].set(self.unit.find('letter_tail1' + tag_suffix).text)
            self.strvar_end_signature[tag_index].set(self.unit.find('letter_tail2' + tag_suffix).text)

    def on_add_line(self):
        """
        Add a new sentence a the end of the current lesson content
        :return: None
        """
        for i in range(0, 2):
            self.lesson_content[i].add_line()

    def on_delete_line(self):
        """
        Remove last sentence from the lesson content
        :param event:
        :return:
        """
        for i in range(0, 2):
            self.lesson_content[i].delete_line()

    def create_new_file(self):
        """
         Prepare the basic tree structure for a new xml file
        :return: None
        """
        file_tree = et.Element('lessons')  # root of a xml file
        lesson_title = et.Element('title')
        lesson_title.text = \
            lf_tools.menu_global.find('text').find('new_lesson').text
        lesson_title_zh = \
            et.Element('title_zh')
        lesson_title_zh.text = \
            lf_tools.menu_global.find('text').find('new_lesson_zh').text

        unit = et.Element('unit')
        unit.append(lesson_title)
        unit.append(lesson_title_zh)
        unit.append(et.Element('content_fr'))
        unit.find('content_fr').text = ''
        unit.append(et.Element('content_zh'))
        unit.find('content_zh').text = ''
        unit.append(et.Element('activity_list'))
        unit.find('activity_list').text = ''
        unit.append(et.Element('vocabulary'))
        file_tree.append(unit)
        return unit

    def get_voc_list_element(self):
        vocab_tree = self.vocab_list_panel.get_vocabulary_tree()
        vocab_tree.set("level",
                       str(self.info_panel.get_level()))

        voc_title = et.Element('title_fr')
        voc_title.text = self.lesson_content[0].get_title()
        voc_title_zh = et.Element('title_zh')
        voc_title_zh.text = self.lesson_content[1].get_title()

        # Append titles of lesson to vocabulary list
        vocab_tree.append(voc_title)
        vocab_tree.append(voc_title_zh)

        return vocab_tree

    def on_save(self):

        if self.filename is None:
            print('Not file selected for saving')
            return

        file_to_save = et.Element("lessons")
        unit = et.Element("unit")
        unit.set("type", str(self.info_panel.get_type()))
        unit.set("theme", str(self.info_panel.get_theme()))
        unit.set("level", str(self.info_panel.get_level()))

        title_fr = et.Element("title_fr")
        title_fr.text = self.lesson_content[0].get_title()
        unit.append(title_fr)

        title_zh = et.Element("title_zh")
        title_zh.text = self.lesson_content[1].get_title()
        unit.append(title_zh)

        # Append lesson content
        for i in range(0, 2):
            unit.append(self.lesson_content[1].
                        get_content_element())

        unit.append(self.activity_list_panel.
                    get_activity_list())

        unit.append(self.get_voc_list_element())
        unit.append(self.explanation_panel.get_explanation_tree())

        file_to_save.append(unit)
        try:
            with open(self.filename, 'wb') as saved_file:
                saved_file.write(et.tostring(file_to_save, pretty_print=True))
        except AttributeError:
            file_to_save.getroottree().write(self.filename, pretty_print=True)

    def on_save_as(self):
        """
        Save the lesson in the user defined file
        :return:
        """
        filename = asksaveasfilename(initialdir="./res/")
        if filename is not None:
            self.filename = filename
            self.on_save()

    def prepare_formatted_content(self):
        """
        Construct xml content according to the type of the lesson content
        :return:
        """
        selected_type = self.info_panel.get_type()
        unit_to_process = self.unit
        letter_tags = ['letter_header1',
                       'letter_header2',
                       'letter_tail1',
                       'letter_tail2']
        letter_textes = None
        if selected_type == 'letter':
            letter_textes = []
            for comp_index in range(0, 2):
                letter_textes.append([self.strvar_top_date_and_location[comp_index].get(),
                                      self.strvar_top_politeness[comp_index].get(),
                                      self.strvar_end_politeness[comp_index].get(),
                                      self.strvar_end_signature[comp_index].get()])
        tag_language_suffix = ['_fr', '_zh']
        for i in range(0, 2):
            for j in range(0, len(letter_tags)):
                if unit_to_process.find(letter_tags[j] + tag_language_suffix[i]) is not None:
                    if selected_type != 'letter':
                        unit_to_process.remove(letter_tags[j] + tag_language_suffix[i])
                    else:
                        unit_to_process.find(letter_tags[j] + tag_language_suffix[i]).text = \
                            letter_textes[i][j]
                else:
                    if selected_type == 'letter':
                        element = et.Element(letter_tags[j] + tag_language_suffix[i])
                        element.text = letter_textes[i][j]
                        unit_to_process.append(element)

    def _on_new_file(self):
        self.load_file(self.create_new_file())


if __name__ == "__main__":
    root = tk.Tk()
    test = LessonFrame(root, 't')
    root.title('Text test')
    test.mainloop()
