from keyboards import *
from create_bot import *
from work_bd import *
from .other import get_command_start

# Состояния для регистрации
class register(StatesGroup):
    FIO = State()                           # Фамилия Имя Отчество                          list[str]
    st = State()                            # st094862                                      str
    real_activation_code = State()          # Сгенерированный код активации                 int
    received_activation_code = State()      # Полученный от пользователя код активации      int

# Отмена handlera st для повторной регистрации
async def cancel_st(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback.id)
    await add_new_user(callback, state)

# Начали регистрацию
async def add_new_user(callback: types.CallbackQuery, state:FSMContext):
    if check_exists_tg_id(callback.from_user.id):
        text="""<b>Вы уже зарегистрированы</b>"""
        st = get_st(callback.from_user.id)
        flag = check_is_user_out(st)
        if flag:    kb = kb_in 
        else:       kb = kb_out  
        await callback.message.answer(text=text,parse_mode="HTML",reply_markup=kb)
        return
    text="""<b>Первый шаг регистрации:</b> \n<em>Введи своё ФИО через пробел</em>"""

    await bot.answer_callback_query(callback.id)

    await callback.message.answer(text=text,parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    await register.FIO.set()

# Получили ФИО  
async def FIO(message: types.Message, state=FSMContext):
    FIO = message.text
    FIO = FIO.split()
    try:
        surname, name, lastname = FIO[0], FIO[1], FIO[2]                                # Проверка, что ввели 3 слова
        flag = check_exists_FI(surname, name)
        if flag:
            text="""<b>Второй шаг регистрации:</b> \n<em>Введи st-логин для подтверждения аккаунта по почте\nСкорее всего оно окажется в спаме</em>"""

            await state.update_data(FIO=FIO)
            await message.answer(parse_mode="HTML",text=text)
            await register.st.set()
        else:
            text="""<b>По нашим данным Вы не живёте в АГ</b>
            Если это не так, обратитесь к разработчикам, их telegram-аккаунты вы можете найти в описании бота"""

            await message.answer(parse_mode="HTML",text=text)
            await get_command_start(message)

            await state.finish()
    except Exception as e:
        print(traceback.format_exc())
        text="""<b>Напишите полное ФИО</b>"""

        await message.answer(parse_mode="HTML",text=text, reply_markup=ReplyKeyboardRemove())
        return

# Получили st
async def st(message: types.Message, state=FSMContext):
    ans = message.text  
    new_user = check_exists_st(ans)

    if new_user:
        text = """<b>Ошибка регистрации</b> \nПохоже, что Вы уже зарегестрированы\nЕсли вы всё равно не можете пользоваться ботом, обратитесь к разработчикам"""
        await message.answer(parse_mode="HTML",text=text,reply_markup=kb_in)
        await state.finish()
    else:
        try:
            real_activation_code = send_mail(ans)
            await state.update_data(st = ans, real_activation_code = real_activation_code)

            text="""<b>Третий шаг регистрации:</b> \n<em>Введи код подтверждения, высланный Вам на почту st\nЕсли вы ввели неправильный st-логин или вам не пришёл код, нажмите кнопку отмена и начните регистрацию заново</em>"""
        except Exception as e:
            print(e, "\n", traceback.format_exc())
            text=f"Произошла внутреняя ошибка бота. <b>{e}</b>. Перешлите это сообщение разработчикам их tg аккаунты указаны в описании бота" 
        await message.answer(parse_mode="HTML",text=text,reply_markup=cancel_st_kb)
        await register.received_activation_code.set()

# Проверка кода активации
async def check(message: types.Message, state=FSMContext):
    await state.update_data(received_activation_code = int(message.text))
    data = await state.get_data()
    if data['received_activation_code'] == data['real_activation_code']:
        text="""<b>Регистрация прошла успешно.</b> \n<em>Система зафиксировала, что ты являешься учеником АГ!</em>"""
        FIO = data['FIO']
        surname, name, lastname = FIO[0], FIO[1], FIO[2]
        al_time, room = get_al_time_room_from_adm(surname, name)
        user = [message.from_user.id, surname, name, lastname, room, data['st'], al_time]
        add_user(user)

        await message.answer(text=text,parse_mode="HTML",reply_markup=kb_in)
        await state.finish()
    else:
        text="""<b>Вы ввели неверный код активации</b>\n Проверьте, правильно ли Вы ввели код, попробуйте снова.\n Если код не пришёл, или Вы уверенны, что вводите правильный код активации, обратитесь к разработчикам, их telegram аккаунты указаны в описании бота"""
        await message.answer(text=text,parse_mode="HTML")
        return

# Отправка кода активации
import smtplib, random
def send_mail(student_st):
    smtpObj = smtplib.SMTP('smtp.yandex.ru:587')
    smtpObj.starttls()
    smtpObj.login('ag.spbu@yandex.ru', "journal.ag.spbu@yandex.ru")
    random_number = str(random.randint(100, 1000))
    student_mail = student_st + "@student.spbu.ru"
    smtpObj.sendmail("ag.spbu@yandex.ru",[student_mail], random_number)
    smtpObj.quit()
    random_number = int(random_number)
    return random_number


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_st, text='cancel_st', state=register.received_activation_code)
    dp.register_callback_query_handler(add_new_user, text=['REGISTER'])
    dp.register_message_handler(FIO, state=register.FIO)
    dp.register_message_handler(st, state=register.st)
    dp.register_message_handler(check, state=register.received_activation_code)    