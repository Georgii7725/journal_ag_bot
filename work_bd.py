import sqlite3
from sqlite3 import Error
import traceback


# Создание БД
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection



# DML команды
def add_user(user: list):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?);"
    try:
        cursor.execute(query, user)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
    connection.close()

def get_user(tg_id):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = f"SELECT * FROM users WHERE tg_id = {tg_id}"
    try:
        cursor.execute("SELECT * FROM users WHERE tg_id = ?", [tg_id])
        user = cursor.fetchone()
        connection.commit()
        connection.close()
        return user
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close
        return None


def get_st(tg_id):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT st FROM users WHERE tg_id = ?"
    try:
        cursor.execute(query, [tg_id])
        st = cursor.fetchone()
        connection.commit()
        connection.close()
        return st[0]
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close()
        return None


def add_exit(params: list):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "INSERT INTO database (KEY, exit_date, exit_time, entrance_date, entrance_time, reason, flag) VALUES (?, ?, ?, ?, ?, ?, 0);"

    try:
        cursor.execute(query, params)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
    connection.close()

def update_database(st):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "UPDATE database SET flag = True WHERE KEY = ?"
    try:
        cursor.execute(query, [st])
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
    connection.close()

def get_al_time_room_from_adm(surname, name):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT al_time, room FROM administration WHERE surname = ? AND name = ?"
    try:
        print
        cursor.execute(query, [surname, name])
        al_time, room = cursor.fetchone()
        connection.commit()
        connection.close()
        return al_time, room
    except Error as e:
        print(f"The error '{e}' occurred.\n{traceback.format_exc()}")
        connection.close()
        return None

def get_al_time_from_users(tg_id):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT al_time FROM users WHERE tg_id = ?"
    try:
        cursor.execute(query, [tg_id])
        al_time = cursor.fetchone()
        connection.commit()
        connection.close()
        return al_time
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close()
        return None


def check_exists_tg_id(tg_id):    # ["surname", "name"]
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT EXISTS(SELECT * FROM users WHERE tg_id = ?)"
    try:
        cursor.execute(query, [tg_id])
        flag = cursor.fetchone()
        connection.commit()
        connection.close()
        return flag[0]
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close()
        return False


def check_is_user_out(st):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT flag FROM database WHERE KEY = ?"
    try:
        cursor.execute(query, [st])
        flag = cursor.fetchall()
        connection.commit()
        connection.close()
        return flag[-1][0]
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close()
        return False


def check_exists_FI(surname, name):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT EXISTS(SELECT * FROM administration WHERE surname = ? and name = ?)"
    try:
        flag = cursor.execute(query, [surname, name])
        flag = flag.fetchone() # ты возвращал объект cursor. if в регистрациии нихуя не понимал что имел ввиду под cursor
        connection.commit()
        connection.close()
        return bool(flag[0])# инедкс 0, тк это кортеж tuple и когда ты просто писал flag там был вывод (0,) а bool просто мне нравится bool
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close()
        return False #Гош да ты гений я тут блять сижду переделываю последний хендлер чтобы выдавало что такого имени и фамилии нет а тыт тут true возвращал

def check_exists_st(st: str):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT EXISTS(SELECT * FROM users WHERE st = ?)"
    try:
        cursor.execute(query, [st])
        flag = cursor.fetchone()
        connection.commit()
        connection.close()
        return flag[0]
    except Error as e:
        print(f"The error '{e}' occurred.\n{query}\n{traceback.format_exc()}")
        connection.close()
        return False

def print_table(table: str) -> list:
    connection = create_connection("journal_ag_bot.sqlite")
    query = f"SELECT * from {table}"
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result
    except Error as e:
        connection.close()
        print(f"The error '{e}' occurred")

