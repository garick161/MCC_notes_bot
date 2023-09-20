import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')

root_dir = os.getcwd()


def bild_exel_file(df):
    df.columns = ['Номер поезда', 'Бортовой номер', 'Машинист', 'Таб. № машиниста', '№ колонны машиниста',
                  'Помощник машиниста', 'Таб. № п/машиниста', '№ колонны п/машиниста', 'Время явки', 'Время сдачи',
                  'Километр', 'Пикет', 'Время замечания', 'Станция/участок', 'Замечание', 'Время записи',
                  'Статус замечания', 'Фамилия ДСП/ДНЦ']
    df.to_excel(os.path.join(root_dir, 'temp_report_files/report.xlsx'))


def all_notes():
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    df = pd.read_sql('SELECT * FROM notes', con=conn, index_col='id')
    bild_exel_file(df)
    conn.close()


def notes_by_month():
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    df = pd.read_sql("""SELECT * FROM notes WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP)""",
                     con=conn, index_col='id')
    bild_exel_file(df)
    conn.close()


def notes_by_month_and_driver(num_driver):
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    df = pd.read_sql(f"""SELECT * 
                        FROM notes 
                        WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP) AND num_driver = {num_driver}""",
                     con=conn, index_col='id')
    bild_exel_file(df)
    conn.close()


def notes_by_month_and_col(num_col):
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    df = pd.read_sql(f"""SELECT * 
                        FROM notes 
                        WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP) AND driver_num_col = {num_col}""",
                     con=conn, index_col='id')
    bild_exel_file(df)
    conn.close()


def all_notes_count():
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT COUNT(*) FROM notes')
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def notes_by_month_count():
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    cur = conn.cursor()
    cur.execute("""SELECT DISTINCT COUNT(*) FROM notes WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP)""")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def notes_by_month_and_driver_count(num_driver):
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    cur = conn.cursor()
    cur.execute(f"""SELECT DISTINCT COUNT(*)
                    FROM notes 
                    WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP) AND num_driver = {num_driver}""")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def notes_by_month_and_col_count(num_col):
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    cur = conn.cursor()
    cur.execute(f"""SELECT DISTINCT COUNT(*)
                    FROM notes 
                    WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP) AND driver_num_col = {num_col}""")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def plot_stat_by_month():
    conn = sqlite3.connect(os.path.join(root_dir, 'volumes/data_bases/notes.sql'))
    df = pd.read_sql("""SELECT *
                        FROM notes WHERE strftime('%m', time_note) = strftime('%m', CURRENT_TIMESTAMP)""",
                     con=conn)
    conn.close()
    df['driver_num_col'] = df['driver_num_col'].astype(int)
    df = df.sort_values('driver_num_col')
    df['driver_num_col'] = df['driver_num_col'].astype('category')
    df = df.rename(columns={'driver_num_col': 'Колонна'})

    fig = plt.figure(figsize=(8, 4))

    sns.histplot(data=df, x='Колонна', hue='Колонна', legend=False)
    plt.title('Статистика по колоннам за месяц')
    plt.ylabel('Количество замечаний')
    plt.savefig(os.path.join(root_dir, 'temp_report_files/stat_by_month.jpg'))
