from keyboards import *
from create_bot import *
import csv

# Состояния для регистрации
class register(StatesGroup):
    FIO = State()                           # Фамилия Имя Отчество                          list[str]
    st = State()                            # st094862                                      str
    real_activation_code = State()          # Сгенерированный код активации                 int
    received_activation_code = State()      # Полученный от пользователя код активации      int

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
        surname, name, lastname = FIO[0], FIO[1], FIO[2]                        # Проверка, что ввели 3 слова
        with open('database/administration.csv', 'rt', encoding="utf8") as file:
            persons = csv.DictReader(file)
            flag = False
            for person in persons:
                if person['name'] == name and person['surname'] == surname:     # Проверка, что есть в списках
                    flag = True
        if flag:
            text="""<b>Второй шаг регистрации:</b> \n<em>Введи st-логин для подтверждения аккаунта по почте\nСкорее всего оно окажется в спаме</em>"""

            await state.update_data(FIO=FIO)
            await message.answer(parse_mode="HTML",text=text)
            await register.st.set()
        else:
            text="""<b>По нашим данным Вы не живёте в АГ</b>
            Если это не так, обратитесь к разработчикам, их telegram-аккаунты вы можете найти в описании бота"""

            await message.answer(parse_mode="HTML",text=text)
            await state.finish()
    except:
        text="""<b>Напишите полное ФИО</b>"""

        await message.answer(parse_mode="HTML",text=text)
        return

# Получили st
async def st(message: types.Message, state=FSMContext):
    ans = str(message.text)  

    new_user = True
    with open('database/users.csv', 'rt', encoding="utf8") as file:
        users = csv.DictReader(file)
        for user in users:
            if user['st'] == ans:
                new_user = False
                break

    if not new_user:
        text = """<b>Ошибка регистрации</b> \nПохоже, что Вы уже зарегестрированы(\nЕсли вы всё равно не можете пользоваться ботом, обратитесь к разработчикам"""
        await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
        await state.finish()

    else:
        real_activation_code = send_mail(ans)
        await state.update_data(st = ans, real_activation_code = real_activation_code)

        text="""<b>Третий шаг регистрации:</b> \n<em>Введи код подтверждения, высланный Вам на почту st</em>"""

        await message.answer(parse_mode="HTML",text=text)
        await register.received_activation_code.set()

# Проверка кода активации
async def check(message: types.Message, state=FSMContext):
    await state.update_data(received_activation_code = int(message.text))
    data = await state.get_data()
    if data['received_activation_code'] == data['real_activation_code']:
        text="""<b>Регистрация прошла успешно.</b> \n<em>Система зафиксировала, что ты являешься учеником АГ!</em>"""
        FIO = data['FIO']
        surname, name, lastname = FIO[0], FIO[1], FIO[2]
        with open('database/administration.csv', 'rt', encoding="utf8") as file:
            persons = csv.DictReader(file)
            for person in persons:
                if name == person['name'] and surname == person['surname']:
                    room = person['room']
                    al_time = person['al_time']
                    break
        with open('database/users.csv', 'a', encoding='utf8') as file:
            file.write(f"{message.from_user.id},{surname},{name},{lastname},{room},{data['st']},{al_time}\n")
        await message.answer(text=text,parse_mode="HTML",reply_markup=kb_in)
        await state.finish()
    else:
        text="""<b>Вы ввели неверный код активации</b>\n Проверьте, правильно ли Вы ввели код, попробуйте снова.\n Если код не пришёл, или Вы уверенны, что вводите правильный код активации, обратитесь к разработчикам, их telegram аккаунты указаны в описании бота"""
        await message.answer(text=text,parse_mode="HTML")
        return

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
        random_number = int(random_number)
        return random_number
    except:
        return


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(add_new_user, text=['REGISTER'])
    dp.register_message_handler(FIO, state=register.FIO)
    dp.register_message_handler(st, state=register.st)
    dp.register_message_handler(check, state=register.received_activation_code)    