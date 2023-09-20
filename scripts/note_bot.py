import telebot
from telebot import types
from collections import defaultdict
from datetime import datetime
from loguru import logger
from shutil import copy
import os

# импорт собственных файлов
from transformers_whisper import get_transcription_whisper, whisper_model, whisper_processor
from format_text import get_info_from_text
from db_connection import add_to_db_func, add_to_history_db_func
import data_validation
import reports


# Определим необходимые глобальные переменные
root_dir = os.getcwd()
station_name = ''
recognition_text = ''
note_dict = defaultdict(str)
log_file_name = ''
# словарь для определения местоположения станции по километру и пикету
stations_dict = {'andronovka': (20.7, 24.2), 'lefortovo': (17.9, 20.6), 'cherkizovo': (13.9, 16.4),
                 'belokamen': (9.2, 12.4), 'rostokino': (5.1, 9.1), 'vladikino': (2.2, 5.0), 'likhobory': (49.0, 54.9),
                 'likhobory ': (1.0, 2.1), 'serbor': (45.1, 48.9), 'presnya': (38.2, 45.0),
                 'kanatchikovo': (32.5, 36.1),
                 'kozuhovo': (28.2, 30.5), 'ygresh': (24.7, 28.1),
                 'dnc1': [(30.6, 32.4), (36.2, 38.1)], 'dnc2': [(12.5, 13.8), (16.5, 17.8), (24.3, 24.6)]}
stations_dict_rus_name = {'andronovka': 'Андроновка', 'lefortovo': 'Лефортово', 'cherkizovo': 'Черкизово',
                          'belokamen': 'Белокаменная', 'rostokino': 'Ростокино', 'vladikino': 'Владыкино',
                          'likhobory': 'Лихоборы', 'serbor': 'Сер. Бор', 'presnya': 'Пресня',
                          'kanatchikovo': 'Канатчиково',
                          'kozuhovo': 'Кожухово', 'ygresh': 'Угрешская', 'dnc1': 'ДНЦ-1', 'dnc2': 'ДНЦ-2'}

bot = telebot.TeleBot(os.environ.get('MCC_TOKEN'))


@logger.catch
@bot.message_handler(content_types=['text'])
def start(message):
    text = message.text.lower()
    if text == 'передать замечание' or text == '/send_note':
        # Создание файла для логирования истории по каждой коммуникации с пользователем
        # Новая коммуникация - новый файл
        global log_file_name
        log_file_name = datetime.now().strftime('%H-%M_%d-%m-%Y')
        path_to_log_file = os.path.join(root_dir, f'volumes/history_logs/{log_file_name}.log')
        logger.remove()  # Чтобы не выводилось в консоль, а писалось только в файл
        logger.add(path_to_log_file, format='{time:HH:mm:ss} {message}')
        logger.info(f'передать замечание/send_note')

        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Андроновка', callback_data='andronovka')
        btn2 = types.InlineKeyboardButton('Лефортово', callback_data='lefortovo')
        btn3 = types.InlineKeyboardButton('Черкизово', callback_data='cherkizovo')
        btn4 = types.InlineKeyboardButton('Белокаменная', callback_data='belokamen')
        btn5 = types.InlineKeyboardButton('Ростокино', callback_data='rostokino')
        btn6 = types.InlineKeyboardButton('Владыкино', callback_data='vladikino')
        btn7 = types.InlineKeyboardButton('Лихоборы', callback_data='likhobory')
        btn8 = types.InlineKeyboardButton('Сер. Бор', callback_data='serbor')
        btn9 = types.InlineKeyboardButton('Пресня', callback_data='presnya')
        btn10 = types.InlineKeyboardButton('Канатчиково', callback_data='kanatchikovo')
        btn11 = types.InlineKeyboardButton('Кожухово', callback_data='kozuhovo')
        btn12 = types.InlineKeyboardButton('Угрешская', callback_data='ygresh')
        btn13 = types.InlineKeyboardButton('ДНЦ-1', callback_data='dnc1')
        btn14 = types.InlineKeyboardButton('ДНЦ-2', callback_data='dnc2')
        btn15 = types.InlineKeyboardButton('Автоматически определить станцию', callback_data='find_station')
        btn16 = types.InlineKeyboardButton('Прислать схему МЦК', callback_data='send_schema')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12)
        markup.row(btn13, btn14)
        markup.row(btn15)
        markup.row(btn16)

        bot.reply_to(message, 'На какую станцию?', reply_markup=markup)

    elif text == '/info':
        with open(os.path.join(root_dir, 'addition_files/description.txt'), "r", encoding='utf-8') as f:
            info = f.read()
            bot.send_message(message.chat.id, info, parse_mode='html')

    elif text == '/start':
        with open(os.path.join(root_dir, 'addition_files/hello_message.txt'), "r", encoding='utf-8') as f:
            info = f.read()
            bot.send_message(message.chat.id, info, parse_mode='html')

    elif text == '/commands':
        commands = """/info - Получение информации о боте и как это работает\n/reports - Получение отчетов и статистик\n\nДля <b>передачи замечания</b> просто напишите "<b>Передать замечание</b>" без кавычек, регистр не имеет значения или команду /send_note"""
        bot.send_message(message.chat.id, commands, parse_mode='html')

    elif text == '/reports':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Получить все замечания', callback_data='all_notes')
        btn2 = types.InlineKeyboardButton('Все замечания за месяц', callback_data='notes_by_month')
        btn3 = types.InlineKeyboardButton('За месяц по машинисту', callback_data='notes_by_month_and_driver')
        btn4 = types.InlineKeyboardButton('За месяц по колонне', callback_data='notes_by_month_and_col')
        btn5 = types.InlineKeyboardButton('Количество всех замечаний', callback_data='all_notes_count')
        btn6 = types.InlineKeyboardButton('Количество за месяц', callback_data='notes_by_month_count')
        btn7 = types.InlineKeyboardButton('Количество по машинисту за месяц',
                                          callback_data='notes_by_month_and_driver_count')
        btn8 = types.InlineKeyboardButton('Количество по колонне за месяц',
                                          callback_data='notes_by_month_and_col_count')
        btn9 = types.InlineKeyboardButton('Статистка по колоннам за месяц', callback_data='plot_stat_by_month')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
        bot.reply_to(message, 'Какой отчет вы хотите?', reply_markup=markup)


@logger.catch
@bot.callback_query_handler(func=lambda call: True)
def get_note(call):
    # Памятка перед записью замечания
    def before_voice_func():
        global station_name
        station_name = ''
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Прислать образец аудио записи', callback_data='send_example')
        template = 'Отправте аудиосообщение по образцу:\n6421-й(64-21) ЭС2Г-075 Машинист Щербаков 45-й километр 1-й пикет(пикет один)\nОтсутствует секция заграждения\nВремя замечания 10 часов 15 минут'
        markup.row(btn)
        bot.send_message(call.message.chat.id, template, reply_markup=markup)

    # Кнопки для редактирования данных
    def edit_menu_func():
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Номер поезда', callback_data='train_num')
        btn2 = types.InlineKeyboardButton('Бортовой номер', callback_data='bort_num')
        btn3 = types.InlineKeyboardButton('Машинист', callback_data='train_driver')
        btn4 = types.InlineKeyboardButton('Километр', callback_data='km')
        btn5 = types.InlineKeyboardButton('Пикет', callback_data='picket')
        btn6 = types.InlineKeyboardButton('Час замечания', callback_data='hour_note')
        btn7 = types.InlineKeyboardButton('Минуты замечания', callback_data='minutes_note')
        btn8 = types.InlineKeyboardButton('Текст замечания', callback_data='text_note')
        btn9 = types.InlineKeyboardButton('Станция', callback_data='station')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
        bot.send_message(call.message.chat.id, "Какое из полей вы хотите исправить?", reply_markup=markup)

    # Функция для формирования промежуточного кочета для проверки зафиксированных данных машинистом
    # Флаг all_data=False - неполный отчет, без данных о поездке и помощнике машиниста
    # Флаг all_data=True - полный отчет, с данными о поездке и помощнике машиниста
    def report_func(all_data=False):
        if all_data:
            info_for_check = f"Номер поезда: {note_dict['train_num']}\nЭлектропоезд ЭС2Г - {note_dict['bort_num']}\nМашинист: {note_dict['train_driver']}\nТаб. номер машиниста: {note_dict['num_driver']}\nКолонна машиниста: {note_dict['driver_num_col']}\nПомощник машиниста: {note_dict['assist']}\nТаб. номер п/м: {note_dict['num_assist']}\nКолонна п/м: {note_dict['assist_num_col']}\nВремя явки: {note_dict['start_work']}\nВремя сдачи: {note_dict['end_work']}\nМесто замечания: {note_dict['kilometer']} километр {note_dict['picket']} пикет\nСтанция: {note_dict['station']}\nЗамечание: {note_dict['note']}\nВремя замечания: {note_dict['hour_note']}:{note_dict['minutes_note']}"
            bot.send_message(call.message.chat.id, "Данные для книги замечаний")
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Данные заполнены верно👍', callback_data='save_to_db')
            btn2 = types.InlineKeyboardButton('Нет, хочу заново передать замечание🤦‍♂️', callback_data='repeat_note')
            markup.add(btn1, btn2)
            bot.send_message(call.message.chat.id, info_for_check, reply_markup=markup)
        else:
            logger.info(f'note_dict_after_ARM_info\n{note_dict}')
            info_for_check = f"Номер поезда: {note_dict['train_num']}\nЭлектропоезд ЭС2Г - {note_dict['bort_num']}\nМашинист: {note_dict['train_driver']}\nМесто замечания: {note_dict['kilometer']} километр {note_dict['picket']} пикет\nСтанция: {note_dict['station']}\nЗамечание: {note_dict['note']}\nВремя замечания: {note_dict['hour_note']}:{note_dict['minutes_note']}"
            bot.send_message(call.message.chat.id, info_for_check)
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Да, все верно!', callback_data='add_to_db')
            btn2 = types.InlineKeyboardButton('Нет, хочу исправить', callback_data='edit_note')
            btn3 = types.InlineKeyboardButton('Хочу продиктовать замечание заново', callback_data='repeat_note')
            markup.add(btn1, btn2, btn3)
            bot.send_message(call.message.chat.id, "Данные верно зафиксированы?", reply_markup=markup)

    # Блок функций редактирования переданных данных
    def edit_train_num(message):
        num = message.text
        check_result = data_validation.check_train_num(num)
        logger.info(f'edit_train_num, value:{num}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'train_num'
            get_note(call)
        else:
            note_dict['train_num'] = num
            report_func()

    def edit_bort_num(message):
        num = message.text
        check_result = data_validation.check_bort_num(num)
        logger.info(f'edit_bort_num, value:{num}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'bort_num'
            get_note(call)
        else:
            note_dict['bort_num'] = num
            report_func()

    def edit_train_driver(message):
        name = message.text
        check_result = data_validation.check_name(name)
        logger.info(f'edit_train_driver, value:{name}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'train_driver'
            get_note(call)
        else:
            note_dict['train_driver'] = name
            report_func()

    def edit_km(message):
        km = message.text
        check_result = data_validation.check_km(km)
        logger.info(f'edit_km, value:{km}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'kilometer'
            get_note(call)
        else:
            note_dict['kilometer'] = km
            report_func()

    def edit_picket(message):
        picket = message.text
        check_result = data_validation.check_picket(picket)
        logger.info(f'edit_picket, value:{picket}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'picket'
            get_note(call)
        else:
            note_dict['picket'] = picket
            report_func()

    def edit_hour_note(message):
        hour = message.text
        check_result = data_validation.check_hour_note(hour)
        logger.info(f'edit_hour_note, value:{hour}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'hour_note'
            get_note(call)
        else:
            note_dict['hour_note'] = hour
            report_func()

    def edit_minutes_note(message):
        minutes = message.text
        check_result = data_validation.check_minutes_note(minutes)
        logger.info(f'edit_minutes_note, value:{minutes}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'minutes_note'
            get_note(call)
        else:
            note_dict['minutes_note'] = minutes
            report_func()

    def edit_text_note(message):
        logger.info(f'edit_text_note, value:{message.text}')
        note_dict['note'] = message.text
        report_func()

    def edit_station(message):
        name = message.text
        check_result = data_validation.check_name_station(name)
        logger.info(f'edit_station, value:{name}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            call.data = 'station'
            get_note(call)
        else:
            note_dict['station'] = name
            report_func()

    # Блок заполнения доп данных без связи с АРМ
    def fill_driver_num(message):
        num = message.text
        check_result = data_validation.check_tab_num(num)
        logger.info(f'fill_driver_num, value:{num}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            bot.register_next_step_handler(call.message, fill_driver_num)
        else:
            note_dict['num_driver'] = num
            bot.send_message(call.message.chat.id, 'Введите номер колонны машиниста')
            bot.register_next_step_handler(call.message, fill_col_num)

    def fill_col_num(message):
        num = message.text
        check_result = data_validation.check_col_num(num)
        logger.info(f'fill_col_num, value:{num}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            bot.register_next_step_handler(call.message, fill_col_num)
        else:
            note_dict['driver_num_col'] = num
            bot.send_message(call.message.chat.id, 'Введите фамилию помощника машиниста')
            bot.register_next_step_handler(call.message, fill_assist_name)

    def fill_assist_name(message):
        name = message.text
        check_result = data_validation.check_name(name)
        logger.info(f'fill_assist_name, value:{name}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            bot.register_next_step_handler(call.message, fill_assist_name)
        else:
            note_dict['assist'] = name
            bot.send_message(call.message.chat.id, 'Введите табельный номер помощника машиниста')
            bot.register_next_step_handler(call.message, fill_assist_num)

    def fill_assist_num(message):
        num = message.text
        check_result = data_validation.check_tab_num(num)
        logger.info(f'fill_assist_num, value:{num}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            bot.register_next_step_handler(call.message, fill_assist_num)
        else:
            note_dict['num_assist'] = num
            bot.send_message(call.message.chat.id, 'Введите номер колонны помощника машиниста')
            bot.register_next_step_handler(call.message, fill_assist_col)

    def fill_assist_col(message):
        num = message.text
        check_result = data_validation.check_col_num(num)
        logger.info(f'fill_assist_col, value:{num}, {check_result}')
        if check_result:
            bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
            bot.register_next_step_handler(call.message, fill_assist_col)
        else:
            note_dict['assist_num_col'] = num
            bot.send_message(call.message.chat.id,
                             'Введите время и дату явки через пробел\nНапример:"12:45 25.09.2023"')
            bot.register_next_step_handler(call.message, fill_start_time)

    def fill_start_time(message):
        time = data_validation.check_time(message.text)
        logger.info(f'fill_start_time, value:{message.text}, {time}')
        if isinstance(time, str):
            bot.send_message(call.message.chat.id, time)
            bot.register_next_step_handler(call.message, fill_start_time)
        else:
            note_dict['start_work'] = str(time)
            bot.send_message(call.message.chat.id, 'Введите время дату сдачи через пробел\nНапример:"18:45 25.09.2023"')
            bot.register_next_step_handler(call.message, fill_end_time)

    def fill_end_time(message):
        time = data_validation.check_time(message.text)
        logger.info(f'fill_end_time, value:{message.text}, {time}')
        if isinstance(time, str):
            bot.send_message(call.message.chat.id, time)
            bot.register_next_step_handler(call.message, fill_end_time)
        else:
            note_dict['end_work'] = str(time)
            check_result = data_validation.check_time_logic(note_dict['start_work'], note_dict['end_work'],
                                                            note_dict['hour_note'], note_dict['minutes_note'])
            logger.info(f'check_logit_time - {check_result}')
            if check_result:
                bot.send_message(call.message.chat.id, '🙅‍♂️ ' + check_result)
                bot.send_message(call.message.chat.id, 'Введите время и дату явки')
                bot.register_next_step_handler(call.message, fill_start_time)
            else:
                report_func(all_data=True)

    # Функции для получения отчетов
    def report_by_month_and_driver(message):
        reports.notes_by_month_and_driver(message.text.strip())
        with open(os.path.join(root_dir, 'temp_report_files/report.xlsx'), "rb") as f:
            bot.send_document(call.message.chat.id, f)

    def report_by_month_and_col(message):
        reports.notes_by_month_and_col(message.text.strip())
        with open(os.path.join(root_dir, 'temp_report_files/report.xlsx'), "rb") as f:
            bot.send_document(call.message.chat.id, f)

    def report_by_month_and_driver_count(message):
        bot.send_message(call.message.chat.id, reports.notes_by_month_and_driver_count(message.text.strip()))

    def report_by_month_and_col_count(message):
        bot.send_message(call.message.chat.id, reports.notes_by_month_and_col_count(message.text.strip()))

    #######################################################################################
    # Блок обработки callback сообщений
    if call.data in ['andronovka', 'lefortovo', 'cherkizovo', 'belokamen', 'rostokino', 'vladikino', 'likhobory',
                     'serbor', 'presnya', 'kanatchikovo', 'kozuhovo', 'ygresh', 'dnc1', 'dnc2']:
        global station_name
        station_name = stations_dict_rus_name[call.data]
        logger.info(f'Выбранная станция: {station_name}')
        before_voice_func()

    elif call.data == 'send_example':
        with open(os.path.join(root_dir, 'addition_files/example_voice.ogg'), "rb") as voice:
            bot.send_voice(call.message.chat.id, voice)

    elif call.data == 'send_schema':
        with open(os.path.join(root_dir, 'addition_files/schema_mcc.pdf'), "rb") as schema:
            bot.send_document(call.message.chat.id, schema)

    elif call.data == 'find_station':
        logger.info(f'Выбранная станция: Автоматическое определение')
        before_voice_func()

    elif call.data == 'add_to_db':
        logger.info('all_right - ready add_to_db')
        if 'Нет информации' in note_dict.values():
            bot.send_message(call.message.chat.id, '❗️❗️❗️\nПожалуйста, проверьте еще раз заполнение данных!')
            report_func()
        else:
            bot.send_message(call.message.chat.id,
                             'Отлично!\nВременно отсутствует доступ к АРМ💩\nПожалуйста введите дополнительные данные:\n\nТабельный номер машиниста')
            bot.register_next_step_handler(call.message, fill_driver_num)

    elif call.data == 'save_to_db':
        logger.info('final step - add to volumes: notes.sql, history.sql, voices')
        add_to_db_func(note_dict=note_dict)
        add_to_history_db_func(note_dict=note_dict, text=recognition_text)
        bot.send_message(call.message.chat.id,
                         'Информация успешно добавлена в книгу замечаний👍\n\nВы всегда можете сделать запрос и посмотеть статус, замечания за месяц или узнать количество переданных замечаний на текущий момент.\nДля получения спавки о доступных функциях и командах введите /info или нажмите на это слово')

    elif call.data == 'edit_note':
        logger.info('not all right - edit_note menu')
        edit_menu_func()

    elif call.data == 'repeat_note':
        logger.info('not all right - try repeat note')
        before_voice_func()

    elif call.data == 'train_num':
        bot.send_message(call.message.chat.id, 'Введите номер поезда')
        bot.register_next_step_handler(call.message, edit_train_num)

    elif call.data == 'bort_num':
        bot.send_message(call.message.chat.id, 'Введите номер борта трехзначное число\nНапример: 113 или 045')
        bot.register_next_step_handler(call.message, edit_bort_num)

    elif call.data == 'train_driver':
        bot.send_message(call.message.chat.id, 'Введите фамилию машиниста')
        bot.register_next_step_handler(call.message, edit_train_driver)

    elif call.data == 'km':
        bot.send_message(call.message.chat.id, 'Введите километр')
        bot.register_next_step_handler(call.message, edit_km)

    elif call.data == 'picket':
        bot.send_message(call.message.chat.id, 'Введите пикет')
        bot.register_next_step_handler(call.message, edit_picket)

    elif call.data == 'hour_note':
        bot.send_message(call.message.chat.id, 'Введите час замечания')
        bot.register_next_step_handler(call.message, edit_hour_note)

    elif call.data == 'minutes_note':
        bot.send_message(call.message.chat.id, 'Введите минуты замечания')
        bot.register_next_step_handler(call.message, edit_minutes_note)

    elif call.data == 'text_note':
        bot.send_message(call.message.chat.id, 'Введите текст замечания')
        bot.register_next_step_handler(call.message, edit_text_note)

    elif call.data == 'station':
        bot.send_message(call.message.chat.id, 'Введите станцию или участок ДНЦ(ДНЦ-1 или ДНЦ-2)')
        bot.register_next_step_handler(call.message, edit_station)

    # Блок получения отчетов и статистик
    elif call.data == 'all_notes':
        reports.all_notes()
        with open(os.path.join(root_dir, 'temp_report_files/report.xlsx'), "rb") as f:
            bot.send_document(call.message.chat.id, f)

    elif call.data == 'notes_by_month':
        reports.notes_by_month()
        with open(os.path.join(root_dir, 'temp_report_files/report.xlsx'), "rb") as f:
            bot.send_document(call.message.chat.id, f)

    elif call.data == 'notes_by_month_and_driver':
        bot.send_message(call.message.chat.id, 'Введите табельный номер машиниста')
        bot.register_next_step_handler(call.message, report_by_month_and_driver)

    elif call.data == 'notes_by_month_and_col':
        bot.send_message(call.message.chat.id, 'Введите номер колонны машиниста')
        bot.register_next_step_handler(call.message, report_by_month_and_col)

    elif call.data == 'all_notes_count':
        bot.send_message(call.message.chat.id, reports.all_notes_count())

    elif call.data == 'notes_by_month_count':
        bot.send_message(call.message.chat.id, reports.notes_by_month_count())

    elif call.data == 'notes_by_month_and_driver_count':
        bot.send_message(call.message.chat.id, 'Введите табельный номер машиниста')
        bot.register_next_step_handler(call.message, report_by_month_and_driver_count)

    elif call.data == 'notes_by_month_and_col_count':
        bot.send_message(call.message.chat.id, 'Введите номер колонны машиниста')
        bot.register_next_step_handler(call.message, report_by_month_and_col_count)

    elif call.data == 'plot_stat_by_month':
        reports.plot_stat_by_month()
        with open(os.path.join(root_dir, 'temp_report_files/stat_by_month.jpg'), "rb") as f:
            bot.send_document(call.message.chat.id, f)


# Блок распознавания голосового сообщения замечания
@logger.catch
@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    # Короткий отчет для проверки корректности распознанных данных
    def report_func():
        info_for_check = f"Номер поезда: {note_dict['train_num']}\nЭлектропоезд ЭС2Г - {note_dict['bort_num']}\nМашинист: {note_dict['train_driver']}\nМесто замечания: {note_dict['kilometer']} километр {note_dict['picket']} пикет\nСтанция: {note_dict['station']}\nЗамечание: {note_dict['note']}\nВремя замечания: {note_dict['hour_note']}:{note_dict['minutes_note']}"
        bot.send_message(message.chat.id, info_for_check)
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Да, все верно!', callback_data='add_to_db')
        btn2 = types.InlineKeyboardButton('Нет, хочу исправить', callback_data='edit_note')
        btn3 = types.InlineKeyboardButton('Хочу продиктовать замечание заново', callback_data='repeat_note')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Данные верно зафиксированы?", reply_markup=markup)

    logger.info('record voice message')
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('new_note.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    # Сохранение временного голосового для логирования
    temp_voice = os.path.join(root_dir, f'volumes/history_log_voices/{log_file_name}.ogg')
    copy('new_note.ogg', os.path.join(root_dir, temp_voice))

    # Распознавание текста с помощью трансформеров
    global recognition_text
    recognition_text = get_transcription_whisper("new_note.ogg",
                                                 whisper_model,
                                                 whisper_processor,
                                                 language="russian",
                                                 skip_special_tokens=True).strip()

    logger.info(f'recognition_text\n{recognition_text}')
    global note_dict
    # Вытягивание нужной информации из текста в основном с помощью регулярных выражений, файл format_text.py
    note_dict = get_info_from_text(recognition_text, result_dict=note_dict)
    global station_name
    if station_name == '':
        try:
            # Переведем км и пикет в вещественное число для удобства
            # Небольшая хитрость с поправкой на -1 пикет. Диапазон значения пикетов от 1 до 10, а нам нужно от 0 до 9
            km = int(note_dict['kilometer']) * 10
            picket = int(note_dict['picket']) - 1
            point = (km + picket) / 10
            # Определяем принадлежность места замечания к станции
            for key, value in stations_dict.items():
                if key == 'dnc1' or key == 'dnc2':
                    for dist in value:
                        if dist[0] <= point <= dist[1]:
                            station_name = stations_dict_rus_name[key]
                            break
                else:
                    if value[0] <= point <= value[1]:
                        station_name = stations_dict_rus_name[key.rstrip()]
                        break
        except ValueError:
            pass
    note_dict['station'] = station_name
    logger.info(f'note_dict after text postprocessing:\n{note_dict}')
    report_func()


if __name__ == "__main__":
    bot.polling(non_stop=True)
