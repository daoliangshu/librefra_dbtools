""" Each vocabulary could be sorted in 4 different static categories
    The categories are written in db on a 32int ( 4 * 8bits) :
    At most 64-1 categories ( 2^8 -1) are referenced here"""
cat_mask = int('FF', 16)

categories = {}
categories['NO'] = int('00', 16)
categories['PERSON'] = int('01', 16)
categories['FOOD'] = int('02', 16)
categories['NATURE'] = int('03', 16)
categories['PLANT'] = int('04', 16)
categories['ACTIVITY'] = int('05', 16)
categories['FAMILY'] = int('06', 16)
categories['ANIMALS'] = int('07', 16)
categories['TIME'] = int('08', 16)
categories['ECONOMY'] = int('09', 16)
categories['WEATHER'] = int('10', 16)
categories['ART'] = int('11', 16)
categories['ART'] = int('12', 16)
categories['BODY_PART'] = int('13', 16)
categories['CONCEPT'] = int('14', 16)
categories['ACTION'] = int('15', 16)
categories['FEELING'] = int('16', 16)
categories['BAD'] = int('17', 16)
categories['GOOD'] = int('18', 16)


def get_category_name(valueint):
    for k, v in categories.items():
        if v == valueint:
            return k
    return None


"""
NOT_DEFINED = int('00', 16)
PERSON = int('01', 16)
FOOD = int('02', 16)
NATURE = int('03', 16)
PLANT = int('04', 16)
ACTIVITY = int('05', 16)
FAMILY = int('06', 16)
ANIMAL = int('07', 16)
TIME = int('08', 16)
WEATHER = int('09', 16)
AGE = int('0A', 16)
SPORT = int('0B', 16)
MONEY = int('0C', 16)
JOB = int('0D', 16)
COMMUNICATION = int('0E', 16)
DIRECTION = int('0F', 16)
FEELING = int('10', 16)
CHILD = int('11', 16)
MAN = int('12', 16)
WOMAN = int('13', 16)
HIGHTECH = int('14', 16)
POLITIC = int('15', 16)
ECONOMY = int('16', 16)
FINANCE = int('17', 16)
GOOD = int('18', 16)
BAD = int('19', 16)
TOURISM = int('1A', 16)
CULTURE = int('1B', 16)
MATERIAL = int('1C', 16)
ABSTRACT = int('1D', 16)
TOOL = int('1E', 16)
BUILDING = int('1F', 16)
"""
