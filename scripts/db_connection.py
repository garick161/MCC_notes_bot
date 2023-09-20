from datetime import datetime
import sqlite3
from shutil import copy
import os

root_dir = os.getcwd()


def add_to_db_func(note_dict):
    time_of_note = str(datetime.now().date()) + ' ' + note_dict['hour_note'] + ':' + note_dict['minutes_note']
    time_now = str(datetime.now().date())
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS notes 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                train_num varchar(4), 
                bort_num varchar(12), 
                driver varchar(15), 
                num_driver varchar(5), 
                driver_num_col varchar(2), 
                assist varchar(15), 
                num_assist varchar(5), 
                assist_num_col varchar(2), 
                start_work datetime, 
                end_work datetime, 
                km varchar(2), 
                picket varchar(2), 
                time_note datetime, 
                station varchar(15), 
                notition varchar(150), 
                reg_time datetime, 
                status_note varchar(15), 
                name_dsp varchar(10))
                """)
    cur = conn.execute("""insert into notes (train_num, bort_num, driver, num_driver, driver_num_col, assist, 
                       num_assist, assist_num_col, start_work, end_work, km, picket, time_note, station, 
                       notition, reg_time, status_note, name_dsp) 
                       values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 
                       '%s', '%s', '%s', '%s', '%s')""" % (note_dict['train_num'], note_dict['bort_num'],
                                                           note_dict['train_driver'], note_dict['num_driver'],
                                                           note_dict['driver_num_col'], note_dict['assist'],
                                                           note_dict['num_assist'], note_dict['assist_num_col'],
                                                           note_dict['start_work'], note_dict['end_work'],
                                                           note_dict['kilometer'], note_dict['picket'],
                                                           time_of_note, note_dict['station'],
                                                           note_dict['note'], time_now, 'На рассмотрении',
                                                           ''))
    conn.commit()
    cur.close()
    conn.close()


def add_to_history_db_func(note_dict, text):
    time_of_note = str(datetime.now().date()) + ' ' + note_dict['hour_note'] + ':' + note_dict['minutes_note']
    time_now = str(datetime.now().date())
    path_to_dir_voice = 'volumes/voices'

    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/history_db.sql'))
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS history 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                voice varchar(20),
                recognition_text varchar(100),
                train_num varchar(4), 
                bort_num varchar(12), 
                driver varchar(15), 
                km varchar(2), 
                picket varchar(2), 
                time_note datetime, 
                station varchar(15), 
                notition varchar(150), 
                reg_time datetime)
                """)
    cur = conn.execute("""insert into history (voice, recognition_text, train_num, bort_num, driver, km, picket, 
                        time_note, station, notition, reg_time) 
                       values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"""
                       % (path_to_dir_voice, text, note_dict['train_num'], note_dict['bort_num'], note_dict['train_driver'],
                          note_dict['kilometer'], note_dict['picket'], time_of_note, note_dict['station'],
                          note_dict['note'], time_now))
    conn.commit()

    cur.execute('SELECT MAX(id) FROM history')
    last_entry_num = cur.fetchone()[0]

    cur.close()
    conn.close()

    path_voice = os.path.join(root_dir, f'volumes/voices/{last_entry_num}.ogg')
    copy('new_note.ogg', os.path.join(root_dir, path_voice))
