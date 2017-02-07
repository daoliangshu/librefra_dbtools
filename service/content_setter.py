import tkinter as tk

import lf_tools


def verb_pattern_attributes(frame):
    resource = lf_tools.menu_verb.find('prep_patterns')
    label1 = tk.Label(frame, text=resource.find('head').text,
                      background='black', fg='white')
    label1.grid(row=0, column=0)
    frame.master.check_var = {}
    checkboxes1 = []
    strname = []
    var = frame.master.check_var
    for i in range(0, int(resource.find('size').text)):
        strname.append(resource.find('str' + str(i + 1)).text)
        var[strname[i]] = tk.IntVar(frame)
        checkboxes1.append(
            tk.Checkbutton(frame,
                           text=strname[i],
                           variable=var[strname[i]],
                           name=strname[i],
                           command=frame.master.new_state_checkbox))
        checkboxes1[i].grid(row=i + 1, column=0, sticky=tk.W)


def get_headers(tb_type_int, parent):
    headers_et = lf_tools.menu_global.find('headers')
    if tb_type_int is lf_tools.SUBST:
        head_1 = tk.Label(parent,
                          text=headers_et.find('id').text,
                          height='20', width='100')
        head_2 = tk.Label(parent,
                          text=headers_et.find('word').text,
                          height='20')
        head_3 = tk.Label(parent,
                          text=headers_et.find('category').text,
                          height='20')
        head_4 = tk.Label(parent,
                          text=headers_et.find('trans').text,
                          height='20')
        head_5 = tk.Label(parent,
                          text=headers_et.find('genre').text,
                          height='20')
        return head_1, head_2, head_3, head_4, head_5
    elif tb_type_int is lf_tools.VERB:
        head_1 = tk.Label(parent,
                          text=headers_et.find('id').text,
                          height='20', width='100')
        head_2 = tk.Label(parent,
                          text=headers_et.find('word').text,
                          height='20')
        head_3 = tk.Label(parent,
                          text=headers_et.find('category').text,
                          height='20')
        head_4 = tk.Label(parent,
                          text=headers_et.find('conjug').text,
                          height='20')
        head_5 = tk.Label(parent,
                          text=headers_et.find('trans').text,
                          height='20')
        return head_1, head_2, head_3, head_4, head_5
    elif tb_type_int is lf_tools.OTHER:
        head_1 = tk.Label(parent,
                          text=headers_et.find('id').text,
                          height='20', width='100')
        head_2 = tk.Label(parent,
                          text=headers_et.find('word').text,
                          height='20')
        head_3 = tk.Label(parent,
                          text=headers_et.find('category').text,
                          height='20')
        head_4 = tk.Label(parent,
                          text=headers_et.find('type').text,
                          height='20')
        head_5 = tk.Label(parent,
                          text=headers_et.find('trans').text,
                          height='20')
        return head_1, head_2, head_3, head_4, head_5


def get_place(tb_type_int):
    if tb_type_int == lf_tools.SUBST:
        return [
            [0.0, 0.0, 0.1, 1.0],
            [0.1, 0.0, 0.3, 1.0],
            [0.4, 0.0, 0.1, 1.0],
            [0.5, 0.0, 0.3, 1.0],
            [0.8, 0.0, 0.2, 1.0]
        ]
    elif tb_type_int == lf_tools.VERB:
        return [
            [0.0, 0.0, 0.1, 1.0],
            [0.1, 0.0, 0.2, 1.0],
            [0.3, 0.0, 0.1, 1.0],
            [0.4, 0.0, 0.2, 1.0],
            [0.7, 0.0, 0.28, 1.0]
        ]
    elif tb_type_int == lf_tools.OTHER:
        return [
            [0.0, 0.0, 0.1, 1.0],
            [0.1, 0.0, 0.2, 1.0],
            [0.3, 0.0, 0.1, 1.0],
            [0.4, 0.0, 0.3, 1.0],
            [0.7, 0.0, 0.3, 1.0]
        ]
