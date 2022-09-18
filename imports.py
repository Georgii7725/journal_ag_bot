from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
import time
import csv

TOKEN = "5749373743:AAG930y7um-KMc0Qm_mFACsQr4e_GAHCGQk"
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

global hour_entrance_int
global min_entrance_int
kb_start = InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton('REGISTER', callback_data='REGISTER')).insert(InlineKeyboardButton('LOGIN', callback_data='LOGIN')).add(InlineKeyboardButton('HELP', callback_data='HELP'))
kb = InlineKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('REGISTER', callback_data='REGISTER')).insert(KeyboardButton('LOGIN', callback_data='LOGIN'))
kb_in = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('EXIT')).insert(KeyboardButton('PROFILE')).add(KeyboardButton('LOGOUT')).insert(KeyboardButton('HELP'))
kb_out = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('ENTRANCE')).insert(KeyboardButton('PROFILE')).add(KeyboardButton('LOGOUT')).insert(KeyboardButton('HELP'))

class exit(StatesGroup):
    entrance_time = State()
    reason = State()
    flag = State() # Вышел на улицу - False, вернулся в АГ - True

class register(StatesGroup):
    FIO = State()
    num_room = State()
    st_reg = State()
    check_code_reg = State()

class login(StatesGroup):
    st_log = State()
    check_code_login = State()

users = [ 
    {
        "tg_id": "",
        "name": "Тимофей",
        "surname": "Суеубаев",
        "lastname": "Игоревич",
        "room": "211",
        "st": "st084435",        
        "al_time": "15:00"
    }
]


def check_log(user_id: str):
    with open('users.csv', 'r') as file:
        for index, user in enumerate(file.readlines()):
            user = user.split(',')
            if user_id == user[0]:
                return True, index
        return False, -1

def check_reg(student_st: str):
    with open('users.csv', 'r') as file:
        for index, user in enumerate(file.readlines()):
            user = user.split(',')
            if student_st == user[5]:
                return True, index
        return False, -1

import smtplib, random
def send_mail(student_st):
    smtpObj = smtplib.SMTP('smtp.yandex.ru:587')
    smtpObj.starttls()
    smtpObj.login('ag.spbu@yandex.ru', "Pi31415Pi")
    random_number = str(random.randint(100, 1000))
    student_mail = student_st + "@student.spbu.ru"
    smtpObj.sendmail("ag.spbu@yandex.ru",[student_mail], random_number)
    smtpObj.quit()
    return random_number
    
