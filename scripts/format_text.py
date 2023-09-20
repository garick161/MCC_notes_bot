import re


def find_picket(string):
    try:
        pick_only = re.search(r'((Пикет.\d{1,2}|\d{1,2}.{1,4}Пикет))', string, re.IGNORECASE).group()
        num_pick = re.search(r'(\d{1})', pick_only).group()
        return num_pick
    except AttributeError:
        return 'Нет информации'


def find_kilometer(string):
    try:
        kilo_only = re.search(r'(\d{1,2}.{1,3}километр|\d{1,2}.{1,3}км)', string, re.IGNORECASE).group()
        num_kilo = re.search(r'(\d{1,2})', kilo_only).group()
        return num_kilo
    except AttributeError:
        return 'Нет информации'


def find_num_bort(string):
    try:
        bort_only = re.search(r'(2Г.{0,}Машинист)', string, re.IGNORECASE).group()[1:]
        bort_num = ''.join(re.findall(r'(\d)', bort_only, re.IGNORECASE))
        return bort_num if len(bort_num) == 3 else '0'+bort_num
    except AttributeError:
        return 'Нет информации'


def find_train_num(string):
    try:
        train_only = re.search(r'(^\d{1}.\d{1,3}|^\d{2}.\d{2})', string, re.IGNORECASE).group()
        train_num = ''.join(re.findall(r'(\d)', train_only, re.IGNORECASE))
        return train_num
    except AttributeError:
        return 'Нет информации'


def find_hour(string):
    try:
        hour_only = re.search(r'(\d{1,2}.час)', string, re.IGNORECASE).group()
        hour_num = ''.join(re.findall(r'(\d)', hour_only, re.IGNORECASE))
        return hour_num if len(hour_num) == 2 else '0'+hour_num
    except AttributeError:
        return 'Нет информации'


def find_minutes(string):
    try:
        minutes_only = re.search(r'(\d{1,2}.минут)', string, re.IGNORECASE).group()
        minutes_num = ''.join(re.findall(r'(\d)', minutes_only, re.IGNORECASE))
        return minutes_num if len(minutes_num) == 2 else '0'+minutes_num
    except AttributeError:
        return 'Нет информации'


def find_train_driver(string):
    try:
        part_string = re.search(r'(Машинист.{0,}километр|Машинист.{0,}км)', string, re.IGNORECASE).group()
        train_driver = part_string.split()[1].rstrip(',').rstrip('.')
        return train_driver
    except AttributeError:
        return 'Нет информации'


def find_note(string):
    try:
        part = re.search(r'((Пикет.\d{1}|Пикет).{1,}Время)', string, re.IGNORECASE).group().split()
        part_new = ' '.join(part[1:-1])
        note = ''.join(re.findall(r'(\D)', part_new)).strip().strip(',')
        return note
    except AttributeError:
        return 'Нет информации'


def get_info_from_text(text, result_dict):
    result_dict['train_num'] = find_train_num(text)
    result_dict['bort_num'] = find_num_bort(text)
    result_dict['train_driver'] = find_train_driver(text)
    result_dict['kilometer'] = find_kilometer(text)
    result_dict['picket'] = find_picket(text)
    result_dict['note'] = find_note(text)
    result_dict['hour_note'] = find_hour(text)
    result_dict['minutes_note'] = find_minutes(text)

    return result_dict
