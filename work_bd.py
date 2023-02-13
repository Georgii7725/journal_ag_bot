import sqlite3
from sqlite3 import Connection, Error
import traceback


# Создание БД
def create_connection(path) -> Connection:
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def add_user(user: list):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?);"
    try:
        cursor.execute(query, user)
        connection.commit()
    except Error as e:
        print(traceback.format_exc())
    connection.close()

def get_user(tg_id: int) -> list:
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE tg_id = ?"
    try:
        cursor.execute(query, [tg_id])
        user = cursor.fetchone()
        connection.commit()
        connection.close()
        return user
    except Error as e:
        print(traceback.format_exc())
        connection.close
        return [None] * 7

def get_st(tg_id: int) -> str:
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
        print(traceback.format_exc())
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
        print(traceback.format_exc())
    connection.close()

def update_database(st: str):
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "UPDATE database SET flag = True WHERE KEY = ?"
    try:
        cursor.execute(query, [st])
        connection.commit()
    except Error as e:
        print(traceback.format_exc())
    connection.close()

def get_al_time_room_from_adm(surname: str, name: str) -> list:
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
        print(traceback.format_exc())
        connection.close()
        return None

def get_al_time_from_users(tg_id: int) -> str:
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT al_time FROM users WHERE tg_id = ?"
    try:
        cursor.execute(query, [tg_id])
        al_time = cursor.fetchone()
        connection.commit()
        connection.close()
        return al_time[0]
    except Error as e:
        print(traceback.format_exc())
        connection.close()
        return None

def check_exists_tg_id(tg_id: int) -> bool:   
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
        print(traceback.format_exc())
        connection.close()
        return False

def check_is_user_out(st: str) -> bool:
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
        print(traceback.format_exc())
        connection.close()
        return False

def check_exists_FI(surname: str, name: str) -> bool:
    connection = create_connection("journal_ag_bot.sqlite")
    cursor = connection.cursor()
    query = "SELECT EXISTS(SELECT * FROM administration WHERE surname = ? and name = ?)"
    try:
        cursor.execute(query, [surname, name])
        flag = cursor.fetchone()
        connection.commit()
        connection.close()
        return flag[0]
    except Error as e:
        print(traceback.format_exc())
        connection.close()
        return False

def check_exists_st(st: str) -> bool:
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
        print(traceback.format_exc())
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
        print(traceback.format_exc())
