# модуль для работы с базой данных
import sqlite3 as sl
import telebot
# модуль работы со временем
from datetime import datetime, timezone, timedelta

# подключаемся к файлу с базой данных
con = sl.connect('repostbot.db')

# открываем файл
with con:
    # получаем количество таблиц с нужным нам именем
    data = con.execute("select count(*) from sqlite_master where type='table' and name='users'")
    for row in data:
        # если таких таблиц нет
        if row[0] == 0:
            # создаём таблицу для отчётов
            with con:
                con.execute("""
                    CREATE TABLE users (
                        datetime VARCHAR(40) PRIMARY KEY,
                        date VARCHAR(20),
                        id VARCHAR(200),
                        name VARCHAR(200),
                        text VARCHAR(500)
                    );
                """)


# bot = telebot.TeleBot("token")

def add_to_db():
    # подключаемся к базе
    con = sl.connect('repostbot.db')
    # подготавливаем запрос
    sql = 'INSERT INTO users (datetime, date, id, name, text) values(?, ?, ?, ?, ?)'
    # получаем дату и время
    now = datetime.now(timezone.utc)
    # и просто дату
    date = now.date()
    # формируем данные для запроса
    data = [
        (str(now), str(date), str('1'), str('dwdawda'), str('adwwdwa wdad ad a'))
    ]
    # добавляем с помощью запроса данные
    with con:
        con.executemany(sql, data)


if __name__ == '__main__':
    add_to_db()
