import tkinter as tk

from lxml import etree as et

import lf_tools
from const_definitions import colors


class ExplanationPanel(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # (1) Control buttons:
        control_frame = tk.Frame(self)
        self.btn_add_explanation = tk.Button(control_frame,
                                             text=lf_tools.menu_global.find('buttons').
                                             find('add').text,
                                             command=self._on_add)
        self.btn_delete_explanation = tk.Button(control_frame,
                                                text=lf_tools.menu_global.find('buttons').
                                                find('delete').text,
                                                command=self._on_delete)

        # (2) Listbox displaying explanations
        self.strvar_curexplanation = tk.StringVar(self)
        self.listbox_explanation = tk.Listbox(self, selectmode=tk.BROWSE)
        self.bind("<<ListBoxSelect>>", self._on_new_selection)
        self.listbox_explanation.config(highlightcolor='#FFFFFF',
                                        highlightbackground='#000000')
        self.listbox_explanation.bind("<Alt_L>", self._alt_on)
        # (3) Entry to edit current selected explanation
        self.strvar_typed_text = tk.StringVar(self)
        self.entry_typed_text = tk.Entry(self)
        self.entry_typed_text.bind("<KeyRelease>", self._on_edit)
        self.entry_typed_text.bind("<Alt_L>", self._alt_on)

        # (4) Placing:
        self.btn_add_explanation.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.btn_delete_explanation.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.listbox_explanation.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.entry_typed_text.pack(side=tk.TOP, fill=tk.X, expand=True)

    def _on_add(self):
        """
        Add an explanation to the listbox
        :param event: event.widget is normally the add button
        :return: None
        """
        current_index = self.listbox_explanation.curselection()
        if len(current_index) > 1:
            current_index = 0
        sentence_default_content = \
            "%2s : [default value]" % str(self.listbox_explanation.size())
        self.listbox_explanation.insert(tk.END, sentence_default_content)
        self.listbox_explanation.itemconfig(self.listbox_explanation.size() - 1,
                                            bg=colors.TYPE_POETRY,
                                            )
        self.listbox_explanation.select_set(self.listbox_explanation.size() - 1)
        self.listbox_explanation.activate(self.listbox_explanation.size() - 1)
        self.strvar_typed_text.set(current_index)

    def _on_delete(self):

        """
        Delete the last explanation in listbox ( Not yet implemented)
        :param self:
        :return:
        """
        self.listbox_explanation.delete(self.listbox_explanation.size() - 1)

    def _on_edit(self, event):
        if len(self.listbox_explanation.curselection()) <= 0:
            return
        selected_index = self.listbox_explanation.curselection()[0]
        self.listbox_explanation.delete(selected_index)
        self.listbox_explanation.insert(selected_index, event.widget.get())
        self.listbox_explanation.select_set(selected_index)
        self.listbox_explanation.itemconfig(selected_index, bg=colors.TYPE_POETRY)

    def _on_new_selection(self, event=None):
        self.strvar_typed_text.set(self.listbox_explanation.get())

    def _alt_on(self, event):
        if isinstance(event.widget, tk.Entry):
            self.listbox_explanation.focus()
            self.entry_typed_text.delete(0, tk.END)
            self.entry_typed_text.insert(tk.END, '')
        else:
            self.entry_typed_text.focus()
            self.entry_typed_text.delete(0, tk.END)
            self.entry_typed_text.insert(tk.END,
                                         self.listbox_explanation.get(self.listbox_explanation.curselection()))

    def get_explanation_tree(self):
        explanation_element = et.Element("explanation")
        for i in range(0, self.listbox_explanation.size()):
            explanation_unit = et.Element("item")
            temp_str = self.listbox_explanation.get(i).split(':', 1)
            if len(temp_str) != 2:
                continue
            index = temp_str[0].strip()
            if index.isdigit() is False:
                continue
            explanation_unit.set('index', index)
            explanation_unit.text = temp_str[1]
            explanation_element.append(explanation_unit)
        return explanation_element
