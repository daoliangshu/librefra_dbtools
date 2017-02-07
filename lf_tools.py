import os.path
from xml.etree import cElementTree as ET

UPDATED = 11
NON_UPDATED = 12

SUBST = 101
VERB = 102
OTHER = 105

TYPE_ORDER = 'order'
TYPE_MULTCHOICES = 'multiplechoices'

VERB_IRR = 103
TRANS_ZH = 104

map_phonetic = {
    '§': 'ɔ̃',
    '@': 'ɑ̃',
    'N': 'ɲ',
    'S': 'ʃ',
    'R': 'ʁ',
    'Z': 'ʒ',
    'E': 'ɛ',
    '°': 'ø',
    '5': 'ɛ̃',
    '2': 'œ',
    '1': 'œ̃',
    'O': 'ɔ',
    '8': 'ɥ',
    'G': 'ŋ'
}


def resource_path(relative):
    path = os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )
    if "lesson/" in path:
        path = path.replace("lesson/", "")
    return path


''' XML string retrieving convenient references'''
menu_res = ET.parse(resource_path('res/_inner/menu_str.xml'))

menu_verb = menu_res.find('menu_verb')
menu_subst = menu_res.find('menu_subst')
menu_lesson = menu_res.find('lesson')
# contains **lesson editor** menu language reources
menu_global = menu_res.find('global')
conjug_res = ET.parse(resource_path('res/_inner/irregular_conjugate.xml'))


def set_word(word):
    if word is None:
        return ''
    else:
        return word


def get_hex(word):
    if word is None:
        return ''
    else:
        try:
            return hex(word)
        except TypeError:
            return '-1'


def hex_to_int(word):
    try:
        return int(word, 16)
    except TypeError:
        print('Exception hex_to_int:TypeError')
        return 0
    except ValueError:
        print('Exception hex_to_int:ValueError')
        return 0


class V:
    """Class V for Verb contains class variables for processing flags extracted
     from verb entries in the sqlite db
     PREP : Each verb has a prep_flag which indicates which patterns
     can be used with the verb
    """

    def conjug_first_group(verb, tense):
        if verb.endswith('er') is False or verb == 'aller':
            return None
        res = None
        term = menu_verb.find('term').find(tense).find('term1').text.split(',')
        radical = verb[0:-2]
        res = []
        mobile = ''
        if term[0][0] == 'r' and V.requires_mobile_vowel(radical[-1]) is True:
            mobile = 'e'
        for i in range(0, 6):
            if radical[-1] == 'g' and (term[i][0] == 'a' or term[i][0] == 'o'):
                mobile = 'e'
            res.append(radical + mobile + term[i])
        return res

    def conjug_second_group(verb, tense):
        if verb.endswith('ir') is False:
            return None
        res = []
        term = menu_verb.find('term').find(tense).find('term2').text.split(',')
        radical = verb[0:-2]
        for i in range(0, 6):
            res.append(radical + term[i])
        return res

    def requires_mobile_vowel(last):
        if last == 'm' or last == 'n' or last == 'l' or last == 't' or last == 'b' \
                or last == 'g' or last == 'd' or last == 'h':
            return True
        return False

    '''
        Return None if not found
        Return ( model, index_pointing_at_prefix_end)
    '''

    def get_irreg_model(verb_str):
        irreg_list = conjug_res.find('list').text.split(',')
        idx = -1
        v = None
        for irreg in irreg_list:
            idx = len(verb_str) - len(irreg)
            if idx < 0:
                continue
            v = verb_str[idx: None]
            if v == irreg:
                return (v, idx)
        return (None, None)

    @staticmethod
    def check_ir_is_third_group(verb_str):
        res = conjug_res.find('list_ir').text.split(',')
        for v in res:
            if len(verb_str) >= len(v):
                offset = len(verb_str) - len(v)
                if verb_str[offset:None] == v:
                    return True
        return False

    @staticmethod
    def get_verb_irreg(verb_str, tense):
        (model, idx) = V.get_irreg_model(verb_str)
        if model is not None and idx is not None:
            prefix = verb_str[0:idx]
            print('ok1')
            term_model = conjug_res.find('term').find(model)
            radicals = None
            try:
                radicals = term_model.find('rad').text.split(',')
            except:
                print('no_radicals')
            radical_code_list = None
            tense_term_group = 1
            try:
                radical_code_list = term_model.find(tense).find('code').text
            except:
                pass
            try:
                tense_term_group = term_model.find(tense).find('t').text
            except:
                pass

            rad_sorted = ['', '', '', '', '', '']
            reg_rad = None
            if radical_code_list is None:
                rad_sorted = None
                reg_rad = V.get_regular_radical(verb_str)
            else:
                for i in range(0, 6):
                    rad_sorted[i] = prefix + radicals[int(radical_code_list[i])]
            term = menu_verb.find('term').find(tense).find('term' + str(tense_term_group)). \
                text.split(',')
            '''Merge'''
            res = ['', '', '', '', '', '']
            final_rad = reg_rad
            for i in range(0, 6):
                if rad_sorted is not None:
                    final_rad = rad_sorted[i]
                res[i] = final_rad + term[i]
            return res
        return None

    @staticmethod
    def get_regular_radical(verb):
        index = -1
        print(verb)
        for i in range(len(verb) - 1, 1, -1):
            if verb[i] is 'r':
                index = i
                break
        if index == -1:
            return None
        return verb[0: index - 1]

    def conjugate(verb, tense):
        res = None
        r = verb[-1:None]
        if verb[-2:None] == 'er':
            res = V.conjug_first_group(verb, tense)
        elif verb[-2:None] == 'ir' and V.check_ir_is_third_group(verb) is False:
            res = V.conjug_second_group(verb, tense)
        else:
            res = V.get_verb_irreg(verb, tense)  # None --> is regular
        print(res)
        return res

    def conjugate_present(verb_str, verb_group_int=None):
        tense = 'present'
        return V.conjugate(verb_str, tense)

    def conjugate_simple_past(verb_str, verb_group_int=None):
        tense = 'simple_past'
        return V.conjugate(verb_str, tense)

    def conjugate_imparfait(verb_str):
        tense = 'imparfait'
        return V.conjugate(verb_str, tense)

    def conjugate_futur(verb_str, verb_group_int=None):
        tense = 'futur'
        return V.conjugate(verb_str, tense)

    MASK_GROUP = int('00000000000000000000000000000011', 2)
    MASK_PRESENT_TM = int('00000000000000000000000000001100', 2)
    MASK_PAST_SIMPLE_TM = int('00000000000000000000000011000000', 2)
    MASK_TRANS = int('00000000000000000000001100000000', 2)
    MASK_PREPO = int('00000000000000000000110000000000', 2)
    MASK_IMPERS_NORM = int('00000000000000000011000000000000', 2)
    MASK_IMPERS_PASS = int('00000000000000000100000000000000', 2)

    SHIFT_GROUP = 0
    SHIFT_PRESENT_TM = 2
    SHIFT_PAST_SIMPLE_TM = 6
    SHIFT_TRANS = 8
    SHIFT_IMPERS_PASS = 14
    SHIFT_IMPERS_NORM = 12
    SHIFT_PREPO = 10

    MASK = {'transitivity': MASK_TRANS,
            'prepositional': MASK_PREPO,
            'present_term': MASK_PRESENT_TM,
            'impersonal_passif': MASK_IMPERS_PASS,
            'impersonal_norm': MASK_IMPERS_NORM,
            'pastsimple_term': MASK_PAST_SIMPLE_TM}

    SHIFT = {'transitivity': SHIFT_TRANS,
             'prepositional': SHIFT_PREPO,
             'present_term': SHIFT_PRESENT_TM,
             'impersonal_passif': SHIFT_IMPERS_PASS,
             'impersonal_norm': SHIFT_IMPERS_NORM,
             'pastsimple_term': SHIFT_PAST_SIMPLE_TM}

    class PREP:
        r = menu_verb.find('prep_patterns')
        BASE_SHIFT = 24  # PREP bits are stored from in [32:24]
        V_INF = 0
        V_PREP_INF = 1
        V_CODpo_COIp = 2
        V_COIp_DE_INF = 3
        V_CODp_A_INF = 4
        V_CODp_DE_INF = 5
        V_CODp_DE_NOUN = 6
        SHIFT = {r.find('str1').text, V_INF + BASE_SHIFT,
                 r.find('str2').text, V_PREP_INF + BASE_SHIFT,
                 r.find('str3').text, V_CODpo_COIp + BASE_SHIFT,
                 r.find('str4').text, V_COIp_DE_INF + BASE_SHIFT,
                 r.find('str5').text, V_CODp_A_INF + BASE_SHIFT,
                 r.find('str6').text, V_CODp_DE_INF + BASE_SHIFT,
                 r.find('str7').text, V_CODp_DE_NOUN + BASE_SHIFT,
                 r.find('str8').text, 7 + BASE_SHIFT}

        @staticmethod
        def get_flag_mask(flag_strname):
            return 1 << V.PREP.SHIFT['flag_strname']

        @staticmethod
        def check_flag(flag_int, str_flagname):
            return (flag_int >> V.PREP.SHIFT['flag_strname']) & 1

    @staticmethod
    def get_flag_str(flag_int, str_flagname):
        tmp_res = flag_int >> V.SHIFT[str_flagname]
        size = int(menu_verb.find(str_flagname).find('size').text)
        for i in range(0, size):
            if (tmp_res & (size - 1)):
                return menu_verb.find(str_flagname). \
                    find('str' + str(i + 1)).text

    @staticmethod
    def get_flag_int(str_content, str_flagname, mode='shift'):
        shift = V.SHIFT[str_flagname]
        size = int(menu_verb.find(str_flagname).find('size').text)
        if mode == 'index':
            shift = 0
        for i in range(0, size):
            if str_content == menu_verb.find(str_flagname). \
                    find('str' + str(i + 1)).text:
                return i << shift


class N:
    MASK_GENRE = int('0000000000000111', 2)
    MASK_TYPE = int('1111000000000000', 2)

    MASC = 0
    FEM = 1
    MASC_FEM = 2
    PLUR = 3

    GENRE = {MASC: 'masc',
             FEM: 'fem',
             MASC_FEM: 'masc+fem',
             PLUR: 'plurial'}

    @staticmethod
    def genre_to_int(genre_str):
        for k, v in N.GENRE.items():
            if v == genre_str:
                return k
        return None

    @staticmethod
    def extract_cat(self, index, flagcontent):
        if index >= 4:
            return None
        return (flagcontent >> index * 4) & int(1111, 2)
