import db_helper
import dictionary_entries.noun_entry_frame
import dictionary_entries.other_entry_frame
import dictionary_entries.verb_entry_frame
import lf_tools
from state import STATUS


def send_update(event):
    update_bundle = None
    parent = None
    if isinstance(event, dictionary_entries.noun_entry_frame.SubstEntryFrameUnit) or \
            isinstance(event, dictionary_entries.verb_entry_frame.VerbEntryFrameUnit) or \
            isinstance(event, dictionary_entries.other_entry_frame.OtherEntryFrameUnit):
        parent = event
    else:
        parent = event.widget.master
    if STATUS.cur_workingtable == db_helper.VERB:
        update_bundle = (parent.get_id(),
                         parent.get_word(),
                         parent.get_type(),
                         parent.get_tid(0),
                         parent.get_tid(1),
                         parent.get_tid(2),
                         parent.get_categories_int(),
                         parent.get_info())

    elif STATUS.cur_workingtable == db_helper.SUBST:
        update_bundle = (parent.get_id(),
                         parent.get_word(),
                         parent.get_genre(),  # genre is an integer value( 0=masc, 1=fem [see menu_str.xml])
                         parent.get_categories_int(),
                         parent.get_tid(0),
                         parent.get_tid(1),
                         parent.get_tid(2),
                         parent.get_info())
    elif STATUS.cur_workingtable == db_helper.OTHER:
        update_bundle = (parent.get_id(),
                         parent.get_word(),
                         parent.get_categories_int(),
                         parent.get_tid(0),
                         parent.get_tid(1),
                         parent.get_tid(2),
                         parent.get_type(),
                         parent.get_info())
    else:
        return
    previous = STATUS.dbHelper.get_entry_by_id(STATUS.cur_workingtable, parent.get_id())
    if previous is None:
        print('Error')

    STATUS.dbHelper.update_entry(STATUS.cur_workingtable, update_bundle)
    print('UPDATE')
    parent.change_state_frame(parent.nametowidget('_id'), lf_tools.UPDATED)


def update_transword(TB_TYPE, trans_id, sourceid, flag='ADD'):
    '''sourceid is the word_fr in  which the trans_id is newly assigned
        this method is used to update the references in table_zh when a french word has been
         assigned a new word from table_zh as a translation [used for bidirectional search]'''
    previous_match_word_ids = STATUS.dbHelper.get_translation_by_id(trans_id, TB_TYPE)
    if flag == 'ADD':
        if previous_match_word_ids is None:
            print('subst_trans_id is None')
            # directly add the new word_id to the trans entry
            STATUS.dbHelper.update_translation_by_id(TB_TYPE, trans_id, sourceid)
        else:
            tmp = previous_match_word_ids.split(',')
            for i in tmp:
                if i == sourceid:
                    # add ids to the list if not already in
                    print('Warning : translation already has this sourceid : ' + str(sourceid))
                    return
                    previous_match_word_ids += ',' + str(sourceid)
            print('new value of subst_trand_id : ' + subst_trans_id)
            STATUS.dbHelper.update_translation_by_id(TB_TYPE, trans_id, previous_match_word_ids)
            print('sourceid has been inserted')
    if flag == 'DELETE':
        if previous_match_word_ids is None:
            # Nothing to remove
            return
        else:
            tmp = previous_match_word_ids.split(',')
            new_ids = ''
            count = 0
            for i in tmp:
                if i == sourceid:
                    print('Info:Id to remove found: ' + str(sourceid))
                    continue
                if i == '-1':
                    print('Info:Correct null index')
                    continue
                if count != 0:
                    new_ids += ','
                new_ids += i
            STATUS.dbHelper.update_translation_by_id(TB_TYPE, trans_id, new_ids)
