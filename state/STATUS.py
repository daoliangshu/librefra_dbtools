import lf_tools

'''Here are stored the variables used to manage the current state'''

cur_workingtable = ''

dbHelper = None
previousSelectedFrame = {lf_tools.SUBST: None,
                         lf_tools.VERB: None,
                         lf_tools.OTHER: None}
currentSelectedFrame = {lf_tools.SUBST: None,
                        lf_tools.VERB: None,
                        lf_tools.OTHER: None}

list_entry_canvas = None

TAG_FR = 0
TAG_ZH = 1
''' Translation frame status variables
    -1 : Non editable
    0 to 2 : Indexes corresponding to the transid,
    that is 0 if setting the first id to correspond, etc'''
cur_state = -1

'''instance : TranslationFrame'''
translationFrame = None
