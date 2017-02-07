import tkinter as tk

from lxml import etree as et

from const_definitions import colors

map_type_colors = {'normal': colors.TYPE_NORMAL,
                   'letter': colors.TYPE_LETTER,
                   'poetry': colors.TYPE_POETRY,
                   'dialog': colors.TYPE_DIALOG}


class ScrolledText(tk.Text):
    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)
        self.vbar = tk.Scrollbar(self.frame)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        kw.update({'yscrollcommand': self.vbar.set})
        tk.Text.__init__(self, self.frame, **kw)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar['command'] = self.yview
        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


class LessonContentFrame(tk.Frame):
    def __init__(self, master, tag):
        tk.Frame.__init__(self, master)
        self.tag = tag
        self.bind("<FocusOut>", self._on_leave_focus)
        self.strvar_title = tk.StringVar(self)
        title = tk.Entry(self, textvariable=self.strvar_title)
        title.grid(row=0, column=0, sticky="nsew")
        self.content = tk.Listbox(self,
                                  selectmode=tk.SINGLE)
        self.content.grid(row=1, column=0, rowspan=6, sticky="nsew")
        self.strvar_current_line = tk.StringVar(self)

        self.index = -1  # Current selected line index
        self.prev_index = -1
        self.current_type = "normal"
        self.current = ScrolledText(self, height=3)
        self.current['state'] = tk.DISABLED
        self.current.insert(tk.END, 'Test :)')
        self.current.grid(row=7, column=0, sticky="nsew")

        #  Binding content Listbox
        self.content.bind('<Button-1>',
                          self._on_click_inside_listbox)

        # Binding current Text
        self.current.bind('<Return>', self._on_update_line)
        self.current.bind("<Alt_L>", self._alt_on)
        self.current.bind('<Up>', self._on_previous_line)
        self.current.bind('<Down>', self._on_next_line)
        self.current.bind('<Control-w>', self._select_all_line)
        self.current.bind('<KeyRelease>', self._on_update_line)

        for i in range(0, 8):
            if i == 0 or i == 7:
                self.rowconfigure(i, weight=1)
            else:
                self.rowconfigure(i, weight=1)

        self.columnconfigure(0, weight=1)
        self.set_type(self.current_type)

    def _on_click_inside_listbox(self, event):
        """
        Triggered when mouse is clicked on the listbox
        :param event: from listbox widget
        :return:
        """
        cur_index = event.widget.curselection()
        next_index = event.widget.nearest(event.y)
        if next_index != self.index and self.index >= 0:
            self.set_color(self.index)
        self.index = next_index
        self.set_current()
        self.prev_index = next_index
        self.current.focus_set()
        return "break"

    def _on_previous_line(self, event):
        """
        Go to the previous sentence in the selected list box( fr content or zh content)
        :param event: triggered when up button is pushed
        :return:
        """
        if self.index > 0:
            self.set_color(self.index)
            cur_index = self.index
            next_index = cur_index - 1
            self.prev_index = next_index
            self.index -= 1
            self.set_current()
            return
            # return 'break'
        return

    def _on_leave_focus(self, event):
        self.set_color(self.index)

    def _on_next_line(self, event):
        """
        Go to the next sentence in the selected list box (  fr content or zh content)
        :param event: triggered when down button is pushed
        :return:
        """
        if -1 < self.index < self.content.size() - 1:
            self.set_color(self.index)
            cur_index = self.index
            next_index = cur_index + 1
            self.prev_index = next_index
            self.index += 1
            self.set_current()
            return
        # return 'break' (break propagation)
        return

    def _alt_on(self, event):
        """
        switch focus between editor panels
        :param event:
        :return: None
        """
        self.master.switch_editor_focus((self.tag + 1) % 2)

    def delete_line(self, index=None):
        """
        Simply delete a line
        :param index:
        :return:
        """
        if self.content.size() <= 0:
            return
        if index is None:
            # Delete the last line
            self.content.delete(self.content.size() - 1)
        else:
            if 0 <= index < self.content.size():
                self.content.delete(index)
        if self.content.size() <= 0:
            self.content['state'] = tk.DISABLED

    def set_current(self):
        """
        Set the current Text to the selected line in Listbox
        :return:
        """

        if self.content.size() <= 0:
            return  # Non item in listbox
        if self.index < 0:
            self.index = 0
        self.content.selection_clear(0, tk.END)
        self.content.selection_set(self.index)
        self.current.delete("1.0", tk.END)
        self.current.insert(tk.END, self.content.get(self.index))
        self.current.focus()

    def add_line(self, content="new_line", index=None):
        """
        Add a line at the given index in the Listbox
        If index is None, insert at the End
        :param index:
        :return:
        """
        self.content['state'] = tk.NORMAL
        self.current['state'] = tk.NORMAL
        insert_index = index
        if insert_index is None:
            insert_index = self.content.size()
        if 0 <= insert_index <= self.content.size():
            self.content.insert(insert_index, content)
            self.content.itemconfig(insert_index,
                                    {"bg": map_type_colors[self.current_type]})

    def process_focus(self):
        self.current.focus_set()

    def load_content(self, content_et):
        if self.content.size() > 0:
            self.content.delete(0, tk.END)
        for line_element in content_et.iter('item'):
            line = line_element.find('content').text
            if line is None:
                line = ''
            self.add_line(line)
            self.content.itemconfig(self.content.size() - 1,
                                    {'bg': map_type_colors[self.current_type]})

    def set_type(self, new_type):
        """
        Set the format for displaying the text
        :param new_type:
        :return:
        """
        for i in range(0, self.content.size()):
            self.content.itemconfig(i,
                                    {"bg": map_type_colors[new_type]})
        pass

    def set_title(self, new_title):
        self.strvar_title.set(new_title)

    def get_title(self):
        return self.strvar_title.get()

    def set_color(self, index):
        if index < 0:
            return
        self.content.itemconfig(index,
                                bg=map_type_colors[self.current_type])

    def _select_all_line(self, event):
        """
        Make the text in the editor entry widget full selected
        :param event:
        :return:
        """
        event.widget.select_range(0, tk.END)
        return "break"

    def get_content_element(self):
        tag_map = ["content_fr", "content_zh"]
        content_el = et.Element(tag_map[self.tag])
        for i in range(0, self.content.size()):
            content_el.append(self.get_line_element(i))
        return content_el

    def get_line_element(self, index):
        if 0 <= index < self.content.size():
            item = et.Element("item")
            item.text = self.content.get(index)
            item.set("index", str(index))
            return item
        return None

    def _on_update_line(self, event):
        """
        Update the content of the current Text in the Listbox
        :param event:
        :return:
        """
        if len(self.content.curselection()) <= 0:
            return
        curindex = self.content.curselection()[0]
        self.content.delete(curindex)
        self.content.insert(curindex,
                            self.current.get("1.0", tk.END + "-1c"))
        self.content.selection_set(curindex)
