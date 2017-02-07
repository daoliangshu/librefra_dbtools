import sqlite3

import lf_tools

SUBST = 101
VERB = 102
OTHER = 105

VERB_IRR = 103
TRANS_ZH = 104

map_table = {
    SUBST: "subst_fr",
    VERB: "verb_fr",
    OTHER: "adj_extended_fr"
}


class LF_SQLiteHelper:
    map_offset = 8
    dbHelper = None

    def __init__(self,
                 filename=lf_tools.resource_path("res/_inner")):

        self.map_zh_column = {
            lf_tools.SUBST: 'subst_trans_id',
            lf_tools.VERB: 'verb_trans_id',
            lf_tools.OTHER: 'other_trans_id'
        }

        self.filename = filename
        self.conn = sqlite3.connect(filename)
        LF_SQLiteHelper.dbHelper = self

    def remove_sentences_without_translations(self):
        sentence_fn = "/home/daoliangshu/Pycharm_WorkSpace/librefra_dbtools/res/sentences.db"
        conn_sentences = sqlite3.connect(sentence_fn)
        c = conn_sentences.cursor()
        q = "DELETE FROM intermediate_cor WHERE Field2 is NULL"
        c.execute(q)
        c.close()
        conn_sentences.commit()
        conn_sentences.close()

    def repair_sentences(self):
        return
        c = self.conn.cursor()
        q = "SELECT sentence_fr FROM sentences_fr_zh;"
        sentences_to_repair = {}
        for row in c.execute(q).fetchall():
            point_index = row[0].find(' nap ')
            if point_index >= 0:
                new_sentence = row[0][0:point_index] + " n'as " + row[0][point_index + 5:]
                sentences_to_repair[row[0]] = new_sentence
                # if len(row[0]) > point_index + 5:
                #   sub = row[0][point_index+1:].strip()
                #   if sub[1].isdigit():
                #       sentences_to_repair[row[0]] = row[0][0:point_index+1]
        c.close()
        c2 = self.conn.cursor()
        q2 = "UPDATE sentences_fr_zh SET sentence_fr=? WHERE sentence_fr=?;"
        for key, value in sentences_to_repair.items():
            c2.execute(q2, (value, key))
        c2.close()
        self.conn.commit()

    def import_sentences(self):
        pass  # Do not use
        sentence_fn = "/home/daoliangshu/Pycharm_WorkSpace/librefra_dbtools/res/sentences.db"
        conn_sentences = sqlite3.connect(sentence_fn)

        c = conn_sentences.cursor()
        q = "SELECT Field1, Field2 FROM intermediate_cor"
        print(q)
        corresp_id = {}
        c.execute(q)
        for row in c.fetchall():
            if row[1] in corresp_id or row[0] == row[1]:
                continue
            corresp_id[row[0]] = row[1]
        c.close()
        q1 = "SELECT field1, field2, field3 FROM phrase_examples_ext WHERE field1=?;"
        phrases_to_insert = []
        c1 = conn_sentences.cursor()
        for key, value in corresp_id.items():
            entry1 = c1.execute(q1, (key,)).fetchone()
            entry2 = c1.execute(q1, (value,)).fetchone()
            if entry1[1] == entry2[1]:
                continue
            if entry1[1] == 'cmn':
                phrases_to_insert.append([entry2[2], entry1[2]])
            else:
                phrases_to_insert.append([entry1[2], entry2[2]])
        c1.close()
        c2 = self.conn.cursor()
        q2 = "INSERT INTO sentences_fr_zh (sentence_fr, sentence_zh) VALUES (?, ?);"
        for my_sentence in phrases_to_insert:
            c2.execute(q2, (my_sentence[0], my_sentence[1]))
        c2.close()

    def clean_sentences_db(self):
        pass  # Do not use
        sentence_fn = "/home/daoliangshu/Pycharm_WorkSpace/librefra_dbtools/res/sentences.db"
        conn_sentences = sqlite3.connect(sentence_fn)
        c = conn_sentences.cursor()
        q = "SELECT field1, field2 FROM example_coresp"
        print(q)

        c6 = conn_sentences.cursor()
        # qqq = c6.execute("DELETE FROM phrase_examples_ext WHERE field2!=? AND field2!=?",('fra','cmn',))
        # c6.execute("SELECT field1 FROM phrase_examples_ext")
        c6.execute(q)
        sub_cursor = conn_sentences.cursor()
        # query_sub = "INSERT INTO intermediate_cor(field1) SELECT ?" +\
        #                       "WHERE NOT EXISTS (SELECT 1 FROM intermediate_cor WHERE field1 = ?)"
        # print(query_sub)
        query_2 = "UPDATE intermediate_cor SET field2 = ? " + \
                  "WHERE field1 = ? AND EXISTS (SELECT 1 FROM intermediate_cor WHERE field1 = ?)" + \
                  " AND EXISTS (SELECT 1 FROM intermediate_cor WHERE field1 = ?)"
        print(query_2)
        for row in c6.fetchall():
            print(row[0], row[1])
            params = [row[1], row[0], row[0], row[1]]
            sub_cursor.execute(query_2,
                               params)
        sub_cursor.close()
        c6.close()
        conn_sentences.commit()

    def get_subst_entries(self, str_to_search=None):
        res = []
        c = self.conn.cursor()

        q = "SELECT " + LF_SQLiteHelper._query_fr_common_cols() + ", genre FROM subst_fr"
        print(q)
        if str_to_search is not None:
            c.execute(q + " WHERE" + LF_SQLiteHelper._like_or_clause('word', str_to_search))
        else:
            c.execute(q)
        for row in c.fetchall():
            row_map = {}
            LF_SQLiteHelper._map_fr_common_cols(row_map, row)
            row_map['genre'] = row[LF_SQLiteHelper.map_offset]
            res.append(row_map)
        return res

    @staticmethod
    def _query_fr_common_cols():
        q = "_id, word, " \
            "categories_flag, " \
            "trans_id1, " \
            "trans_id2, " \
            "trans_id3, " \
            "phonetic, " \
            "info"
        return q

    @staticmethod
    def _map_fr_common_cols(row_map, row):
        '''
            Convenient method to retrieve common columns for each type of french word
            Note:Should be used along with __query_common_columns and placed before
            other columns
        '''
        row_map['_id'] = row[0]
        row_map['word'] = row[1]
        row_map['categories_flag'] = row[2]
        row_map['trans_id1'] = row[3]
        row_map['trans_id2'] = row[4]
        row_map['trans_id3'] = row[5]
        row_map['phonetic'] = row[6]
        row_map['info'] = row[7]

    def get_other_entries(self, str_to_search=None):
        res = []
        c = self.conn.cursor()
        query = "SELECT " + LF_SQLiteHelper._query_fr_common_cols() + \
                ", type" + \
                " FROM adj_extended_fr"
        if str_to_search is None:
            c.execute(query)
        else:
            c.execute(query + " WHERE word LIKE ?", (str_to_search + '%',))
        for row in c.fetchall():
            row_map = {}
            LF_SQLiteHelper._map_fr_common_cols(row_map, row)
            row_map['type'] = row[LF_SQLiteHelper.map_offset]
            res.append(row_map)
        return res

    def get_verb_entries(self, str_to_search=None):
        '''
        RETRIEVES VERBS in a DICT
        :param str_to_search:
        :return:
        '''
        res = []
        c = self.conn.cursor()
        query = "SELECT " + LF_SQLiteHelper._query_fr_common_cols() + \
                ", type FROM verb_fr"
        if str_to_search is None:
            c.execute(query)
        else:
            like_clause = LF_SQLiteHelper._like_or_clause('word', str_to_search)
            c.execute(query + " WHERE" + like_clause)
        for row in c.fetchall():
            row_map = {}
            LF_SQLiteHelper._map_fr_common_cols(row_map, row)
            row_map['type'] = row[LF_SQLiteHelper.map_offset]
            res.append(row_map)
        return res

    def commit(self):
        self.conn.commit()

    def get_zh_entries(self, str_to_search=None):
        c = self.conn.cursor()
        res_list = []
        if str_to_search is None:
            res = c.execute("SELECT " + LF_SQLiteHelper._query_trans_cols() + " FROM table_zh")
        else:
            like_or_clause = LF_SQLiteHelper._like_or_clause('word', str_to_search)
            res = c.execute("SELECT " + LF_SQLiteHelper._query_trans_cols() +
                            " FROM table_zh " +
                            "WHERE" + like_or_clause)
        for row in res.fetchall():
            row_mapped = {
                '_id': row[0],
                'word': row[1],
                'subst_trans_id': row[2],
                'verb_trans_id': row[3],
                'other_trans_id': row[4]}
            res_list.append(row_mapped)
        return res_list

    def get_trans_id(self, translation):
        c = self.conn.cursor()
        res = c.execute("SELECT _id FROM table_zh WHERE word=? ;", [translation, ])
        res = res.fetchone()
        if res is None:
            return -1
        else:
            return res[0]

    def get_entry_id(self, word_fr, tb_type):
        table = 'subst_fr'
        if tb_type == SUBST:
            table = "subst_fr"
        elif tb_type == VERB:
            table = "verb_fr"
        elif tb_type == OTHER:
            table = "adj_extended_fr"
        else:
            return
        c = self.conn.cursor()
        res = c.execute("SELECT _id FROM " + table + " WHERE word=? ;", [word_fr, ])
        res = res.fetchone()
        if res is None:
            c.close()
            return -1
        else:
            c.close()
            return res[0]

    @staticmethod
    def _query_trans_cols():
        return "_id, word, subst_trans_id, verb_trans_id, other_trans_id"

    @staticmethod
    def _like_or_clause(column_name, str_column_values):
        values = str_column_values.split(',')
        res = ''
        for i in range(0, len(values)):
            if i != 0:
                res += " OR"
            res += " " + column_name + " LIKE \"" + values[i] + "%\""
        return res

    def get_entries_it(self, type, str_to_search=None):
        if type == SUBST:
            return self.get_subst_entries(str_to_search)
        elif type == VERB:
            return self.get_verb_entries(str_to_search)
        elif type == OTHER:
            return self.get_other_entries(str_to_search)
        elif type == TRANS_ZH:
            return self.get_zh_entries(str_to_search)
        return None

    def get_translation_by_id(self, id_value, flag='ONLY_WORD'):
        cursor = self.conn.cursor()
        column_name = None
        if flag is 'ONLY_WORD':
            cursor.execute("SELECT word FROM table_zh WHERE _id = ?",
                           (id_value,))
            data = cursor.fetchone()
            if data is None:
                return None
            return data[0]

        elif flag == 'SUBST_ID' or flag == lf_tools.SUBST:
            column_name = "subst_trans_id"
        elif flag == lf_tools.VERB:
            column_name = "verb_trans_id"
        elif flag == lf_tools.OTHER:
            column_name = "other_trans_id"
        else:
            return None
        cursor.execute("SELECT " + column_name + " FROM table_zh WHERE _id = ?",
                       (id_value,))
        data = cursor.fetchone()
        if data is None:
            return None
        return data[0]

    '''Update the table_zh with a new value corresponding to a list of french word id
        for which this translation is assigned [for bidirectional search]'''

    def update_translation_by_id(self, db_table_code, trans_id, wids):
        """
        :param db_table_code:
        :param trans_id: Id of the translation to update
        :param wids: word ids to update for the translation
        :return:
        """
        c = self.conn.cursor()
        column_name = self.map_zh_column[db_table_code]
        query = "UPDATE table_zh SET " + column_name + "=? " + \
                "WHERE _id=?"
        print(query)
        c.execute(query, (wids, int(trans_id),))
        self.conn.commit()
        c.close()

    def check_exist(self, TB_TYPE, column_name, column_value):
        """
        Check is the given value exist for the given column in the given table
        :param TB_TYPE: integer code representing table name, defined in db_helper ( SUBST, VERB, ..)
        :param column_name: in which column to search the value
        :param column_value: value to check for existence
        :return:
        """
        table_name = None
        if TB_TYPE == TRANS_ZH:
            table_name = 'table_zh'
        elif TB_TYPE == SUBST:
            table_name = 'subst_fr'
        elif TB_TYPE == VERB:
            table_name = 'verb_fr'
        elif TB_TYPE == OTHER:
            table_name = 'adj_extended_fr'
        else:
            return True
        c = self.conn.cursor()
        c.execute("SELECT _id FROM " + table_name +
                  " WHERE " + column_name + " = ?", (column_value,))
        data = c.fetchone()
        c.close()
        if data is None:
            print('There is no component named %s' % column_value)
            return False
        else:
            print("Exist")
            return True

    def insert_translation(self, translation):
        """
        Insert a translation with default settings.
        If the translation already exist, does nothing
        :param translation:
        :return:
        """
        if self.check_exist(TRANS_ZH, 'word', translation) is True:
            return
        self.insert_entry(TRANS_ZH, [translation])
        print(translation + ' has been inserted.')

    def insert_word(self, word_fr,
                    tb_type_int,
                    trans_id_list1,
                    trans_id_list2,
                    trans_id_list3,
                    insert_bundle):
        '''
        Nothing is inserted if the word already exist
        :param word_fr: word to insert in db
        :param tb_type_int:
        :param trans_id_list1: ids to assign to corresponding bucket
        :param trans_id_list2:
        :param trans_id_list3:
        :param insert_bundle: SUBST=0->genre, OTHER=0->type
        :return: None
        '''
        if word_fr is None or str(word_fr).strip() == '':
            print('invalid word to insert')
            return
        stripped_word_fr = word_fr.strip()
        if self.check_exist(tb_type_int, 'word', stripped_word_fr):
            print(stripped_word_fr + ' exist !')
            return

        # Insert the new word_fr in db
        if tb_type_int == OTHER:
            self.insert_other(stripped_word_fr, insert_bundle[0])
        elif tb_type_int == SUBST:
            self.insert_entry(tb_type_int, insert_bundle)
        else:
            self.insert_entry(tb_type_int, [stripped_word_fr])

        word_id = self.get_entry_id(stripped_word_fr,
                                    tb_type_int)
        if word_id is None:
            return

        order = 1
        for trans_list in [trans_id_list1,
                           trans_id_list2,
                           trans_id_list3]:

            for my_trans_id in trans_list:
                self.update_translation_by_id(tb_type_int,
                                              str(my_trans_id),
                                              word_id)
                self.add_tid_to_entry(word_id,
                                      my_trans_id,
                                      order,
                                      tb_type_int)
            order += 1

    def insert_other(self, word, type_code):
        c = self.conn.cursor()
        c.execute("INSERT INTO adj_extended_fr ('word', 'type') VALUES (?, ?) ;",
                  (word, type_code,))

    def insert_entry(self, TB_TYPE, insert_bundle):
        c = self.conn.cursor()
        if TB_TYPE == TRANS_ZH:
            table_name = 'table_zh'
            vals = [str(insert_bundle[0])]
            c.execute('INSERT INTO ' + table_name +
                      ' ("word") VALUES (?)',
                      (vals[0],))
            self.conn.commit()

        elif TB_TYPE == SUBST:
            table_name = 'subst_fr'
            vals = [str(insert_bundle[0]), int(insert_bundle[1]), 0]
            c.execute('INSERT INTO ' + table_name +
                      ' ( "word", "genre", "categories_flag" ) VALUES (?, ?, ?)',
                      (str(vals[0]), vals[1], vals[2],))
            self.conn.commit()

        elif TB_TYPE == VERB:
            table_name = 'verb_fr'
            vals = [str(insert_bundle[0]), 1, 0]
            c.execute('INSERT INTO ' + table_name +
                      ' ( "word",  "type" ) VALUES (?,  ?)',
                      (str(vals[0]), vals[2],))
            self.conn.commit()

        elif TB_TYPE == OTHER:
            table_name = 'adj_extended_fr'
            vals = [str(insert_bundle[0]), 1, 0]
            c.execute('INSERT INTO ' + table_name +
                      ' ( "word" ) VALUES (?)',
                      (vals[0],))
            self.conn.commit()

    '''Return the values corresponding to the id as a dictionnary'''

    def get_entry_by_id(self, TB_TYPE, id_to_retrieve):
        print(id_to_retrieve)
        if id_to_retrieve is None or id_to_retrieve == 'None':
            return None
        c = self.conn.cursor()
        query_pre = "SELECT " + LF_SQLiteHelper._query_fr_common_cols()
        print(query_pre)
        if TB_TYPE == SUBST:
            res = c.execute(query_pre + ", genre" +
                            " FROM subst_fr where _id = " + str(id_to_retrieve))
            if res is None:
                return None
            else:
                row = res.fetchone()
                res_dic = {}
                LF_SQLiteHelper._map_fr_common_cols(res_dic, row)
                res_dic['genre'] = row[LF_SQLiteHelper.map_offset]
                return res_dic
        elif TB_TYPE == VERB:
            res = c.execute(query_pre +
                            ", type" +
                            " FROM verb_fr WHERE _id = " + str(id_to_retrieve))
            if res is None:
                return None
            else:
                row = res.fetchone()
                res_dic = {}
                LF_SQLiteHelper._map_fr_common_cols(res_dic, row)
                res_dic['type'] = row[LF_SQLiteHelper.map_offset]
                return res_dic
        elif TB_TYPE == OTHER:
            res = c.execute(query_pre +
                            " FROM adj_extended_fr WHERE _id = " + str(id_to_retrieve))
            if res is None:
                return None
            else:
                row = res.fetchone()
                res_dic = {}
                LF_SQLiteHelper._map_fr_common_cols(res_dic, row)
                return res_dic
        else:
            return None

    @staticmethod
    def _query_commons_update():
        return "word=?, categories_flag=?, trans_id1=?, trans_id2=?, trans_id3=?, info=?"

    def add_tid_to_entry(self, wid, tid_to_add, order, tb_type):
        print('tid to add : ' + str(tid_to_add))
        print('order = ' + str(order))
        table_name = map_table[tb_type]
        if table_name == '' or table_name is None:
            print('table_problem while "add_tid_to_entry"')
            return
        new_trans_id = None
        c = self.conn.cursor()
        res = c.execute("SELECT trans_id1, trans_id2, trans_id3 FROM " + table_name + " WHERE _id=? ;",
                        [int(wid), ])
        res = res.fetchone()
        c.close()
        if res is None:
            print('word not found')
            return
        if res[int(order) - 1] is not None:
            print('order : ' + str(order) + '   res[rder-1] = ' + str(res[int(order) - 1]))
        if res[int(order) - 1] is not None and (str(res[int(order) - 1])).strip() != '':
            vals = []
            if ',' in str(res[int(order) - 1]):
                vals = str(res[int(order) - 1]).split(',')
                if str(tid_to_add) in vals:
                    return
                else:
                    new_trans_id = res[int(order) - 1] + ',' + str(tid_to_add)
            else:
                vals = [res[int(order) - 1]]
                if str(tid_to_add) in vals:
                    print('tid already set in word')
                    return  # tid is already set
                else:
                    new_trans_id = str(res[int(order) - 1]) + ',' + str(tid_to_add)
        else:
            new_trans_id = str(tid_to_add)

        c2 = self.conn.cursor()
        ord = int(order)
        trans_col = "trans_id" + str(ord)
        print('now updating ' + table_name + ' ' + trans_col + ' with ' + new_trans_id + 'for wid : ' + str(wid))
        c2.execute("UPDATE " + table_name + " SET " + trans_col + "=? WHERE _id=? ;",
                   (new_trans_id, int(wid),))

    def update_entry(self, TB_TYPE, update_bundle, flags=0):
        c = self.conn.cursor()
        if TB_TYPE == VERB:
            (entry_id, word, type_hex, tid1, tid2, tid3, cat, info) = update_bundle
            print(update_bundle)
            # type_hex = lf_tools.hex_to_int(type_hex)
            type_hex = type_hex
            print(update_bundle)
            res = c.execute("UPDATE verb_fr SET " +
                            LF_SQLiteHelper._query_commons_update() +
                            ", type=?" +
                            " WHERE _id=?",
                            (word, cat, tid1, tid2, tid3, info, type_hex, entry_id,))
            self.conn.commit()
        elif TB_TYPE == SUBST:
            (entry_id, word, genre, cat, tid, tid2, tid3, info) = update_bundle
            print(update_bundle)
            query = "UPDATE subst_fr SET " + \
                    LF_SQLiteHelper._query_commons_update() + \
                    ", genre=?" + \
                    " WHERE _id=?"
            print(query)
            res = c.execute(query, (word, cat, tid, tid2, tid3, info, genre, entry_id,))
            self.conn.commit()
        elif TB_TYPE == OTHER:
            (entry_id, word, cat, tid, tid2, tid3, w_t, info) = update_bundle
            print(update_bundle)
            res = c.execute("UPDATE adj_extended_fr SET " +
                            LF_SQLiteHelper._query_commons_update() + ", type=?" +
                            " WHERE _id=?", (word, cat, tid, tid2, tid3, info, w_t, entry_id,))
            self.conn.commit()

        else:
            pass
        c.close()

    def _clean_table_zh(self):
        c = self.conn.cursor()
        for tb, col in self.map_zh_column.items():
            query = 'SELECT _id, ' + col + ' FROM table_zh;'
            c.execute(query)
            for row in c.fetchall():
                if row[1] is None:
                    continue
                if len(row[1]) == 0:
                    self.update_translation_by_id(tb, row[0], None)
                elif row[1][0] is ',':
                    new_value = None
                    if len(row[1]) > 1:
                        new_value = row[1][1:None]
                    self.update_translation_by_id(tb, row[0], new_value)

    def display_phonetic(self):
        c = self.conn.cursor()
        query = "SELECT `phonetic` FROM subst_fr"
        c.execute(query)
        for row in c.fetchall():
            phon = row[0]
            if phon is None:
                continue
            res = "["
            for i in range(0, len(phon)):
                charr = lf_tools.map_phonetic.get(phon[i], None)
                if charr is not None:
                    res += charr
                else:
                    res += phon[i]
            res += ']'
            print(res)

    def import_phonetic(self):
        """
        Import phonetic from lexique3 db
        :return:
        """
        for row in self.get_entries_it(SUBST):
            if row['phonetic'] is not None and row['phonetic'] != '':
                continue
            tokens = row['word'].lower().split(' ')
            phonetic_full = ''
            for symbol in tokens:
                res = self.get_word_phonetic(symbol)
                if res is None:
                    continue
                phonetic_full += res
            self._update_phonetic(row['_id'], phonetic_full, SUBST)

    def get_word_phonetic(self, word):
        c = self.conn.cursor()
        query = "SELECT `1_ortho`, `2_phon` FROM lexique WHERE `1_ortho`=?;"
        c.execute(query, (word,))
        if c is None:
            return None
        res = c.fetchone()
        c.close()
        if res is False or res is None:
            return None
        return res[1]

    def _update_phonetic(self, _id, new_phon, DB_TABLE):
        c = self.conn.cursor()
        query = "UPDATE " + map_table[DB_TABLE] + "  SET phonetic=?" + \
                " WHERE _id=?"
        c.execute(query, (new_phon, _id,))
        c.close()
        self.conn.commit()

    def _update_info(self):
        c = self.conn.cursor()
        query = "SELECT _id, word, subst_trans_id, verb_trans_id, other_trans_id FROM table_zh"
        c.execute(query)
        res_list = []
        for r in c.fetchall():
            if '[' in r[1]:
                res_list.append(r)
        c.close()
        for row in res_list:
            trans_id = row[0]
            new_trans_str = None
            ''' extract infos'''
            info = extract_info_from_word(row[1])
            updated_word = remove_info_from_word(row[1])
            table = [SUBST, VERB, OTHER]
            trans = [row[2], row[3], row[4]]
            for idx in range(0, len(trans)):
                if trans[idx] is not None and trans[idx] != 'None':
                    for wid in trans[idx].split(','):
                        self.sub_update_info(trans[idx], info, table[idx], trans_id)
            self._update_trans_word_by_id(updated_word, trans_id)

    def _update_trans_word_by_id(self, new_word, _id):
        c = self.conn.cursor()
        query = "UPDATE table_zh SET word=? WHERE _id=?"
        args = [new_word, int(_id)]
        c.execute(query, args)
        c.close()

    def sub_update_info(self, word_id, info_str, DB_TABLE, trans_id):
        if word_id is not None:
            for wid in word_id.split(','):
                map_row = {}
                map_row = self.get_entry_by_id(DB_TABLE, wid)
                info = [None, None, None]
                need_update = False
                if map_row['info'] is not None:
                    info = map_row['info'].split(';')
                for i in range(1, 4):
                    if check_col_contain_id(map_row['trans_id' + str(i)], str(trans_id)):
                        need_update = True
                        if info[i - 1] is None or info[i - 1] == '':
                            info[i - 1] = info_str
                        else:
                            info[i - 1] += ',' + str(info_str)
                if need_update:
                    new_info_str = ''
                    for i in range(0, 3):
                        if i > 0:
                            new_info_str += ';'
                        if info[i] is None:
                            new_info_str += ''
                        else:
                            new_info_str += info[i]
                    self._update_info_by_id(new_info_str, DB_TABLE, wid)

    def _update_info_by_id(self, new_info_str, DB_TABLE, _id):
        c4 = self.conn.cursor()
        self.conn.commit()
        query = "UPDATE " + map_table[DB_TABLE] + " SET info=? WHERE _id=?;"
        args = [str(new_info_str), int(_id)]
        c4.execute(query, args)
        c4.close()

    def close(self):
        self.conn.close()


def check_col_contain_id(buck_str, trans_id):
    if buck_str is not None:
        for tid in buck_str.split(','):
            if tid == trans_id:
                return True
    return False


def extract_info_from_word(word):
    print('test')
    res = ''
    for i in range(word.find('[') + 1, word.find(']')):
        res += word[i]
    return res


def remove_info_from_word(word):
    res = ''
    start = word.find('[')
    end = word.find(']')
    for i in range(0, len(word)):
        if i < start or i > end:
            res += word[i]
    return res
