from keyboards import *
from create_bot import *
from handlers.other import get_command_start
import csv

# Состояния для регистрации
class register(StatesGroup):
    FIO = State()               # Фамилия Имя Отчество
    num_room = State()          # Номер комнаты
    st_reg = State()            # st094862
    check_code_reg = State()    # Код активации

# Начали регистрацию
async def add_new_user(callback: types.CallbackQuery):
    text="""<b>Первый шаг регистрации:</b> \n<em>Введи своё ФИО через пробел</em>"""

    await bot.answer_callback_query(callback.id)

    await callback.message.answer(text=text,parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    await register.FIO.set()

# Получили ФИО
async def FIO(message: types.Message, state=FSMContext):
    FIO = message.text
    FIO = FIO.split()
    try:
        # Проверка, что ввели 3 слова
        surname, name, lastname = FIO[0], FIO[1], FIO[2]

        # Проверка на существование такой ФИО
        # if FIO == database_of_administration["FIO"]:
        #     await state.update_data(FIO=FIO)
        #     await message.answer(parse_mode="HTML",text=text)
        #     await register.num_room.set()    
        # else: 
        #     text="""<b>Напишите полное ФИО</b>"""

        #     await message.answer(parse_mode="HTML",text=text)
        #     return
        text="""<b>Второй шаг регистрации:</b> \n<em>Введите номер комнаты в общежитии</em>"""

        await state.update_data(FIO=FIO)
        await message.answer(parse_mode="HTML",text=text)
        await register.num_room.set()
    except:
        text="""<b>Напишите полное ФИО</b>"""

        await message.answer(parse_mode="HTML",text=text)
        return

# Получили номер комнаты
async def room(message: types.Message, state=FSMContext):
    ans = message.text
    try:
        ans = int(ans)
        if ans >= 200 and ans < 399:
            text="""<b>Третий шаг регистрации:</b> \n<em>Введи st-логин для подтверждения аккаунта по почте\nСкорее всего оно окажется в спаме</em>"""

            await state.update_data(num_room=ans)
            await message.answer(parse_mode="HTML",text=text)
            await register.st_reg.set()
        else:
            text="""</b>Введите номер комнаты в общежитии</b>
            <em>По данным учебного отдела номера комнат в общежитии начинаются с 200 и заканчиваются 399</em>"""

            await message.answer(parse_mode="HTML", text=text)
            return    
    except:
        text="""</b>Введите номер своей комнаты в числовом формате</b>"""

        await message.answer(parse_mode="HTML", text=text)
        return

# Получили st
async def st(message: types.Message, state=FSMContext):
    
    ans = message.text  

    new_user = 0
    with open('database/users.csv', 'rt', encoding="utf8") as file:
        reader = csv.reader(file)
        for i in reader:
            if i[5] == ans:
                new_user = 1
                break

    if new_user:
        text = """<b>Ошибка авторизации</b> \n<em>Похоже, что данный пользователь уже зарегестрирован(</em>"""
        await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
        await get_command_start(message)
        
    else:
        reg_active_code = send_mail(ans)

        text="""<b>Четвёртый шаг регистрации:</b> \n<em>Введи код подтверждения</em>"""

        await state.update_data(st_reg={ans,reg_active_code})
        await message.answer(parse_mode="HTML",text=text)
        await register.check_code_reg.set()

# Проверка кода активации
async def check(message: types.Message, state=FSMContext):
    await state.update_data(check_code_reg = message.text)
    data = await state.get_data()
    kb = InlineKeyboardMarkup()
    count = 0
    for item in list(data['st_reg']):
        if data['check_code_reg'] == item:
            kb = kb_in 
            text="""<b>Регистрация прошла успешно.</b> \n<em>Система зафиксировала, что ты являешься учеником АГ!</em>"""
            FIO = data['FIO']
            surname, name, lastname = FIO[0], FIO[1], FIO[2]
            count = not count
            with open('database/users.csv', 'a', encoding='utf8') as file:
                file.write(f"{message.from_user.id},{surname},{name},{lastname},{data['num_room']},{list(data['st_reg'])[count]},22:00\n")
            break        
        else:
            count += 1
            kb = kb_start
            text="""Регистрация не удалась.\nВозможно вы ввели некорректный код активации"""
    await message.answer(text=text,parse_mode="HTML",reply_markup=kb)
    await state.finish()

# Отправка кода активации
import smtplib, random
def send_mail(student_st):
    try:
        smtpObj = smtplib.SMTP('smtp.yandex.ru:587')
        smtpObj.starttls()
        smtpObj.login('ag.spbu@yandex.ru', "Pi31415Pi")
        random_number = str(random.randint(100, 1000))
        student_mail = student_st + "@student.spbu.ru"
        smtpObj.sendmail("ag.spbu@yandex.ru",[student_mail], random_number)
        smtpObj.quit()
        return random_number
    except:
        return


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(add_new_user, text=['REGISTER'])
    dp.register_message_handler(FIO, state=register.FIO)
    dp.register_message_handler(room, state=register.num_room)
    dp.register_message_handler(st, state=register.st_reg)
    dp.register_message_handler(check, state=register.check_code_reg)    