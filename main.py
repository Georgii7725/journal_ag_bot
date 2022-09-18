from turtle import home
from imports import *
    
async def on_startup(_):
    print("BOT IS STARTING")


# START COMMAND
@dp.message_handler(commands=['start'])
async def get_command_start(message: types.Message):
    
    answer_start = f"Приветствую, {message.from_user.full_name}. С вами бот, который поможет тебе временно выйти из АГ! Команда 'HELP' расскажет о функционале"

    await bot.send_message( chat_id=message.from_user.id,
                            text=answer_start,
                            parse_mode="HTML",
                            reply_markup=kb_start)


# HELP COMMAND
@dp.callback_query_handler(text=['HELP'])
async def get_command_help(callback: types.CallbackQuery):

    help_answer = """
    <b>REGISTER</b> - <em>регистрация ученика (при условии проживания в общежитии АГ)</em>\n<b>LOGIN</b> - <em>вход в аккаунт ученика</em>"""

    await bot.answer_callback_query(callback.id)
    
    await bot.send_message( chat_id=callback.from_user.id,
                            text=help_answer,
                            parse_mode="HTML",
                            reply_markup=kb)


# USER INFO COMMAND
@dp.message_handler(text=['PROFILE'])
async def print_user_info(message: types.Message):
    chat_id=str(message.from_user.id)
    flag, index = check_log(chat_id)
    if flag:
        with open('users.csv', 'r') as file:
            user = file.readlines()[index]
            user = user.split(',')
            my_ans = f"""<b>Данные пользователя:</b>
        <em>Фамилия:</em> {user[1]},
        <em>Имя:</em> {user[2]},
        <em>Отчество:</em> {user[3]},
        <em>Комната:</em> {user[4]}
        <em>Твой st:</em> {user[5]}
        <em>Выход разрешён до</em> {user[6]}
        """
    else:
        my_ans = "<b>Вы не вошли в систему или не зарегистрированы в ней</b>.\n <em>Для подробной информации напишите /help</em>"
    await bot.send_message(chat_id, text=my_ans,parse_mode="HTML",)


# REGISTER COMMAND
@dp.callback_query_handler(text=['REGISTER'])
async def add_new_user(callback: types.CallbackQuery):
    text="""<b>Первый шаг регистрации:</b> \n<em>Введи своё ФИО через пробел</em>"""
    
    await bot.answer_callback_query(callback.id)

    await bot.send_message( chat_id=callback.from_user.id,
                            text=text,
                            parse_mode="HTML",
                            reply_markup=ReplyKeyboardRemove())
    await register.FIO.set()

# STATE FIO
@dp.message_handler(state=register.FIO)
async def FIO(message: types.Message, state=FSMContext):
    FIO = message.text
    FIO = FIO.split()
    try:
        surname, name, lastname = FIO[0], FIO[1], FIO[2]
        text="""<b>Второй шаг регистрации:</b> \n<em>Введи номер комнаты в общежитии</em>"""

        await state.update_data(FIO=FIO)
        await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
        await register.num_room.set()
    except:
        text="""<b>Даун пиши ФИО правильно</b>"""

        await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
        return



# STATE ROOMs NUMBER
@dp.message_handler(state=register.num_room)
async def ROOM(message: types.Message, state=FSMContext):
    ans = message.text

    text="""<b>Третий шаг регистрации:</b> \n<em>Введи st-логин для подтверждения аккаунта по почте\nСкорее всего оно окажется в спаме</em>"""

    await state.update_data(num_room=ans)
    await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
    await register.st_reg.set()

# STATE ST - LOGIN IN REGISTER
@dp.message_handler(state=register.st_reg) 
async def st(message: types.Message, state=FSMContext):
    
    ans = message.text  
    global reg_active_code
    reg_active_code = send_mail(ans)

    text="""<b>Четвёртый шаг регистрации:</b> \n<em>Введи код подтверждения</em>"""

    await state.update_data(st_reg=ans)
    await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
    await register.check_code_reg.set()


# STATE CHECK E-MAIL CODE IN REGISTER
@dp.message_handler(state=register.check_code_reg)
async def check(message: types.Message, state=FSMContext):
    await state.update_data(check_code_reg = message.text)
    data = await state.get_data()
    if data['check_code_reg'] == reg_active_code:
        text="""<b>Регистрация прошла успешно.</b> \n<em>Система зафиксировала, что ты являешься учеником АГ!</em>"""
        FIO = data['FIO']
        surname, name, lastname = FIO[0], FIO[1], FIO[2]
        with open('users.csv', 'a') as file:
            file.write(f"{message.from_user.id},{surname},{name},{lastname},{data['num_room']},{data['st_reg']},22:00\n")        

        await bot.send_message( chat_id=message.from_user.id,
                                text=text,
                                parse_mode="HTML",
                                reply_markup=kb_in)
    else:
        text="""Регистрация не удалась.\nВозможно вы ввели некорректный код активации"""
        await bot.send_message( chat_id=message.from_user.id,
                                text=text,
                                parse_mode="HTML",
                                reply_markup=kb_start)


    await state.finish()


# LOGIN COMMAND
@dp.callback_query_handler(text='LOGIN')
async def get_command_login(callback: types.CallbackQuery):

    text="""<em>Введи st-логин для подтверждения по почте</em>"""

    await bot.answer_callback_query(callback.id)

    await bot.send_message( chat_id=callback.from_user.id,
                            text=text,
                            parse_mode="HTML",
                            reply_markup=ReplyKeyboardRemove())
    await login.st_log.set()


# STATE ST - LOGIN IN LOGIN
@dp.message_handler(state=login.st_log)
async def state_log(message: types.Message, state=FSMContext):
    ans = message.text
    global index #Нужен global, чтобы в следующем handler обратиться
    flag, index = check_reg(ans)
    if flag:
        global log_active_code
        log_active_code = send_mail(ans)
        await state.update_data(st_log=ans)
        text="""<em>Введи код подтверждения по st-почте</em>"""
        await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
    else:
        text="""<em>Пользователь с таким st не зарегистрирован в нашей системе</em>"""
        await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text)
        await get_command_start(message)

    await login.check_code_login.set()


# STATE CHECK E-MAIL CODE IN LOGIN
@dp.message_handler(state=login.check_code_login)
async def check_code_login_def(message: types.Message, state=FSMContext):
    ans = message.text
    if log_active_code == ans:
        data = await state.get_data()
        fl, index = check_reg(data['st_log'])
        with open('users.csv', 'r') as fileREAD:
            data = fileREAD.readlines()
            user = data[index].split(',')
            user[0] = str(message.from_user.id)
            update_user = ""
            for charact in user:
                update_user += charact + ","
            update_user = update_user[:-1]
            data[index] = update_user
            users = ""
            for user in data:
                users += user
        with open('users.csv', 'w') as fileWRITE:
            fileWRITE.write(users)

        text="""<b>Авторизация прошла успешно.</b> \n<b>Добро пожаловать!</b>"""
    else:
        text="""<b>Вы не смогли войти в аккаунт.</b> \n<b>Скорее всего вы указали неправильный код активации</b>"""

    await bot.send_message( chat_id=message.from_user.id,
                                text=text,
                                parse_mode="HTML",
                                reply_markup=kb_in)

    await state.finish()


# LOGOUT COMMAND
@dp.message_handler(text='LOGOUT')
async def get_command_login(message: types.Message):

    flag, index = check_log(str(message.from_user.id))
    if flag:
        with open('users.csv', 'r') as fileREAD:
            data = fileREAD.readlines()
            update_user = data[index].replace(str(message.from_user.id), '-1')
            data[index] = update_user
            update_data = ""
            for user in data:
                update_data += user
        with  open('users.csv', 'w') as fileWRITE:
            fileWRITE.write(update_data)

        text="<b>Вы успешно вышли из аккаунта!</b>"
    else:
        text="<b>Вы не в системе!</b>"

    await bot.send_message( chat_id=message.from_user.id,
                            text=text,
                            parse_mode="HTML",
                            reply_markup=kb_start)

# EXIT COMMAND
@dp.message_handler(text=['EXIT'])
async def add_new_user(message: types.Message):
    text="""<b>Укажите время возвращения</b> \n<em>Формат: ЧЧ:ММ</em>"""

    await bot.send_message( chat_id=message.from_user.id,
                            text=text,
                            parse_mode="HTML",
                            reply_markup=ReplyKeyboardRemove())
    await exit.entrance_time.set()


# STATE get_entrance_time
@dp.message_handler(state=exit.entrance_time)
async def state1(message: types.Message, state=FSMContext):
    try:
        ans = message.text
        reader = csv.DictReader(open('users.csv', 'rt'))
        database = {}
        for row in reader:
            for column, value in row.items():
                database.setdefault(column, []).append(value)
        hour_entrance = ans[0]+ans[1]
        min_entrance = ans[3]+ans[4]
        hour_entrance_int = int(hour_entrance)
        min_entrance_int = int(min_entrance)
        if(ans[2] == ":"):
            hour_al = database["al_time"][0][0] + database["al_time"][0][1]
            min_al = database["al_time"][0][3] + database["al_time"][0][4]
            if hour_entrance < hour_al or (hour_entrance == hour_al and min_entrance <= min_al):
                text="""<b>Укажите причину выхода</b>"""
                await state.update_data(entrance_time = f'{hour_entrance}:{min_entrance}')
                #await state.update_data(exit_time=f'{hour_exit}:{min_exit}')
                await bot.send_message( chat_id=message.from_user.id,
                                parse_mode="HTML",
                                text=text)
                await exit.reason.set()
            else:
                await message.answer("Вам не разрешено приходить в это время", reply_markup=kb_in)
                await state.finish()
        else:
            await message.answer("Введите время в формате 'ЧЧ:ММ'")
            return
    except Exception as e:
        print(e)
        await message.answer("Введите время в формате 'ЧЧ:ММ'")
        return

# STATE reason
@dp.message_handler(state=exit.reason) 
async def state3(message: types.Message, state=FSMContext):
    await state.update_data(reason=message.text)
    text="""<b>Вы можете идти</b> \n<em>Когда будете подходить к АГ, нажмите кнопку ENTRANCE</em>"""
    data = await state.get_data()
    hour_exit = ""
    min_exit = ""
    if(time.localtime().tm_min < 10):
        min_exit = f'0{time.localtime().tm_min}'
    else:
        min_exit = time.localtime().tm_min
    if(time.localtime().tm_hour < 10):
        hour_exit = f'0{time.localtime().tm_hour}'
    else:
        hour_exit = time.localtime().tm_hour
    
    with open('database.csv', 'a') as file: 
        file.write(f"{message.from_user.id},{f'{hour_exit}:{min_exit}'},{data['entrance_time']},{data['reason']},False\n")

    await bot.send_message( chat_id=message.from_user.id,
                            parse_mode="HTML",
                            text=text,
                            reply_markup=kb_out
                            )
    await exit.flag.set()

# STATE flag
@dp.message_handler(state=exit.flag)
async def state4(message: types.Message, state=FSMContext):
    text="<b>С возвращением!</b>"
    fl, index = check_log(message.from_user.id)
    with open('database.csv', 'r') as fileREAD:
        data = fileREAD.readlines()
        update_user = data[index].replace("False", "True")
        data[index] = update_user
        update_data = ""
        for user in data:
            update_data += user
    with  open('database.csv', 'w') as fileWRITE:
        fileWRITE.write(update_data)


    await bot.send_message( chat_id=message.from_user.id,
                            text=text,
                            parse_mode="HTML",
                            reply_markup=kb_in)

    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)