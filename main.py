from imports import *
    
async def on_startup(_):
    print("BOT IS STARTING")


# START COMMAND
@dp.message_handler(commands=['start'])
async def get_command_start(message: types.Message):
    
    answer_start = f"Приветствую, {message.from_user.full_name}. С вами бот, который поможет тебе временно выйти из АГ! Команда 'HELP' расскажет о функционале"

    await message.answer(text=answer_start,parse_mode="HTML",reply_markup=kb_start)


# HELP COMMAND
@dp.callback_query_handler(text=['HELP'])
async def get_command_help(callback: types.CallbackQuery):

    help_answer = """
    <b>REGISTER</b> - <em>регистрация ученика (при условии проживания в общежитии АГ)</em>"""

    await callback.answer_callback_query(callback.id)
    
    await callback.message.answer(text=help_answer,parse_mode="HTML",reply_markup=kb)

@dp.message_handler(text=['HELP'])
async def get_command_help(message: types.Message):

    help_answer = """
    <b>REGISTER</b> - <em>регистрация ученика (при условии проживания в общежитии АГ)</em>\n<b>LOGIN</b> - <em>вход в аккаунт ученика</em>"""
    
    await message.answer(text=help_answer,parse_mode="HTML",reply_markup=kb)

# USER INFO COMMAND
@dp.message_handler(text=['PROFILE'])
async def print_user_info(message: types.Message):
    chat_id=str(message.from_user.id)
    flag, index = check_log(chat_id)
    if flag:
        with open('users.csv', 'r', encoding='utf8') as file:
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
    await message.answer(text=my_ans,parse_mode="HTML",)


# REGISTER COMMAND
@dp.callback_query_handler(text=['REGISTER'])
async def add_new_user(callback: types.CallbackQuery):
    text="""<b>Первый шаг регистрации:</b> \n<em>Введи своё ФИО через пробел</em>"""
    
    await bot.answer_callback_query(callback.id)

    await callback.message.answer(text=text,parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
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
        await message.answer(parse_mode="HTML",text=text)
        await register.num_room.set()
    except:
        text="""<b>Напишите полное ФИО</b>"""

        await message.answer(parse_mode="HTML",text=text)
        return



# STATE ROOMs NUMBER
@dp.message_handler(state=register.num_room)
async def ROOM(message: types.Message, state=FSMContext):
    ans = message.text

    text="""<b>Третий шаг регистрации:</b> \n<em>Введи st-логин для подтверждения аккаунта по почте\nСкорее всего оно окажется в спаме</em>"""

    await state.update_data(num_room=ans)
    await message.answer(parse_mode="HTML",text=text)
    await register.st_reg.set()

# STATE ST - LOGIN IN REGISTER
@dp.message_handler(state=register.st_reg) 
async def st(message: types.Message, state=FSMContext):
    
    ans = message.text  

    new_user = 0
    with open('users.csv', 'rt', encoding="utf8") as file:
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


# STATE CHECK E-MAIL CODE IN REGISTER
@dp.message_handler(state=register.check_code_reg)
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
            with open('users.csv', 'a', encoding='utf8') as file:
                file.write(f"{message.from_user.id},{surname},{name},{lastname},{data['num_room']},{list(data['st_reg'])[count]},22:00\n")
            break        
        else:
            count += 1
            kb = kb_start
            text="""Регистрация не удалась.\nВозможно вы ввели некорректный код активации"""
    await message.answer(text=text,parse_mode="HTML",reply_markup=kb)
    await state.finish()

# EXIT COMMAND
@dp.message_handler(text='EXIT')
async def exit_calendar(message: types.Message):
    await message.answer(text="""<b>Выберите дату прихода в АГ</b>""",
                         parse_mode="HTML",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer(text="""<em>Если вы вернетесь этим же днём, \nвыберите сегодняшнюю дату:</em>""",
                         parse_mode="HTML",
                         reply_markup=await DialogCalendar().start_calendar())

# CALENDAR
@dp.callback_query_handler(dialog_cal_callback.filter())
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await bot.answer_callback_query(callback_query.id)
        await exit.cal_date.set()
        await state.update_data(cal_date=date.strftime("%d.%m.%Y"))
        await callback_query.message.answer(f"""<b>Ты выбрал: {date.strftime("%d.%m.%Y")}</b>""", parse_mode="HTML")
        
        await add_new_user(callback_query.message)

# STATE cal_date
@dp.message_handler(state=exit.cal_date)
async def add_new_user(message: types.Message):
    text="""<b>Укажите время возвращения</b> \n<em>Формат: ЧЧ:ММ</em>"""

    await message.answer(text=text,parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    await exit.entrance_time.set()

# STATE get_entrance_time
@dp.message_handler(state=exit.entrance_time)
async def state1(message: types.Message, state=FSMContext):
    try:
        ans = message.text
        reader = csv.DictReader(open('users.csv', 'rt', encoding='utf8'))
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
                await message.answer(parse_mode="HTML",text=text)
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

    hour_exit = f'0{time.localtime().tm_hour}' if time.localtime().tm_hour < 10 else f'{time.localtime().tm_hour}'
    min_exit = f'0{time.localtime().tm_min}' if time.localtime().tm_min < 10 else f'{time.localtime().tm_min}'
    day_exit = f'0{time.localtime().tm_mday}' if time.localtime().tm_mday < 10 else f'{time.localtime().tm_mday}'
    month_exit = f'0{time.localtime().tm_mon}' if time.localtime().tm_mon < 10 else f'{time.localtime().tm_mon}'
    year_exit = f'{time.localtime().tm_year}'

    users_st = 0
    with open('users.csv', 'rt', encoding="utf8") as file:
        reader = csv.reader(file)
        for i in reader:
            if f'{i[0]}' == f'{message.from_user.id}':
                users_st = i[5]
                break


    with open('database.csv', 'a', encoding='utf') as file: 
        file.write(f"{f'{users_st}'},{f'{day_exit}.{month_exit}.{year_exit}'},{f'{hour_exit}:{min_exit}'},{data['cal_date']},{data['entrance_time']},{data['reason']},False\n")

    await message.answer(parse_mode="HTML",text=text,reply_markup=kb_out)
    await exit.flag.set()

# STATE flag
@dp.message_handler(state=exit.flag)
async def state4(message: types.Message, state=FSMContext):
    text="<b>С возвращением!</b>"
    fl, index = check_log(message.from_user.id)
    with open('database.csv', 'r', encoding='utf8') as fileREAD:
        data = fileREAD.readlines()
        update_user = data[index].replace("False", "True")
        data[index] = update_user
        update_data = ""
        for user in data:
            update_data += user
    with  open('database.csv', 'w', encoding='utf8') as fileWRITE:
        fileWRITE.write(update_data)

    await message.answer(text=text,parse_mode="HTML",reply_markup=kb_in)

    await state.finish()

# ROUND CONNECT FROM USER
@dp.message_handler(text='COMMENT')
async def round_connect_from_users(message: types.Message):
    text="""<b>Обратная связь</b>\n<em>Если у вас есть пожелания, просьбы для улучшения нашего бота</em>\n<em>или вы нашли ошибку в работе бота, то оставте отзыв в Google Forms.</em>\n<em>Этот комментарий останеться </em><b>АНОНИМНЫМ:</b>\n<a href="https://forms.gle/ovk73RWEPuCqbCd36">Google Forms</a>"""

    await message.answer(text=text,
                         parse_mode="HTML")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
