import re
from datetime import datetime as dt


def check_train_num(num):
    try:
        int(num)
    except ValueError:
        return 'Номер поезда должен быть числом'

    if len(num) != 4:
        return 'Номер поезда должен состоять из 4-х чисел'
    if num[0] not in ['6', '7']:
        return 'Номер поезда должен начинаться с 6 или 7'


def check_bort_num(num):
    if len(num) != 3:
        return 'Бортовой номер должен состоять из 3-х чисел'
    try:
        num = int(num)
    except ValueError:
        return 'Бортовой номер должен быть числом'
    if num < 45:
        return 'Маловероятно, что вы эксплуатируете Ласточку с номером раньше 45'


def check_name(name):
    if len(re.findall('[а-яА-Я]+', name)) > 1 and len(re.findall('[а-яА-Я]+', name)) == len(name):
        return 'Фамилия должна быть написана только кириллицей, без цифр, пробелов внутри и спец символов'
    if len(name) < 2:
        return 'Фамилия должна состоять хотя бы из 2-х букв'


def check_km(km):
    if len(km) > 2:
        return 'Слишком большое значение для МЦК'
    try:
        km = int(km)
    except ValueError:
        return 'Номер километра должен быть числом'
    if km < 1 or km > 54:
        return 'Некорректное значение км для МЦК'


def check_picket(picket):
    try:
        picket = int(picket)
    except ValueError:
        return 'Номер пикета должен быть числом'
    if picket < 1 or picket > 10:
        return 'Номер пикета должен быть от 1 до 10'


def check_hour_note(hour):
    try:
        hour = int(hour)
    except ValueError:
        return 'Час замечания должен быть числом'
    if hour < 0 or hour > 24:
        return 'Чаc должен быть от 0 до 24'


def check_minutes_note(minutes):
    try:
        minutes = int(minutes)
    except ValueError:
        return 'Минуты замечания должны быть числом'
    if minutes < 0 or minutes > 60:
        return 'Минуты должны быть от 0 до 60'


def check_name_station(name):
    if len(re.findall('[а-яА-Я]+', name)) > 1:
        return 'Название станции должно быть написано только кириллицей, без цифр, пробелов внутри и спец символов'
    if len(name) < 3:
        return 'Название станции должно быть минимум из 3-х букв'


def check_tab_num(num):
    if len(num) != 5 or num[0] == '0':
        return 'Табельный номер должен быть пятизначным числом'
    try:
        int(num)
    except ValueError:
        return 'Табельный номер должен быть числом'


def check_col_num(col):
    try:
        col = int(col)
    except ValueError:
        return 'Номер колонны должен быть числом'
    if col < 6 or col > 14:
        return 'Некорректное значение колонны для МЦК'


def check_time(time):
    from dateutil import parser
    try:
        time = parser.parse(time)
        return time
    except ValueError:
        return 'Формат даты и времени некорректен'


def check_time_logic(start_time, end_time, hour_note, minutes_note):
    from dateutil import parser
    from datetime import timedelta
    start_time = parser.parse(start_time)
    end_time = parser.parse(end_time)
    time_note = parser.parse(hour_note + ':' + minutes_note + ' ' + str(dt.now().date()))
    if time_note <= start_time or time_note >= end_time:
        return 'Время замечания не может быть вне диапазона времени смены'
    if end_time - start_time > timedelta(hours=12):
        return 'Рабочее время смены не может быть больше 12 часов'
