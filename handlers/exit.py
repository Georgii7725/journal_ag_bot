from keyboards import *
from create_bot import *
from handlers.other import check_log
from aiogram_calendar import dialog_cal_callback, DialogCalendar
import time, csv

class exit_(StatesGroup):
    cal_date = State()          # Дата возвращения
    entrance_time = State()     # Время возвращения
    reason = State()            # Причина возвращения
    flag = State()              # Вышел на улицу - False, вернулся в АГ - True

# EXIT COMMAND
async def exit_calendar(message: types.Message):
    await message.answer(text="""<b>Выберите дату возвращения в АГ</b>""",
                         parse_mode="HTML",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer(text="""<em>Если вы вернетесь этим же днём, \nвыберите сегодняшнюю дату:</em>""",
                         parse_mode="HTML",
                         reply_markup=await DialogCalendar().start_calendar())

# CALENDAR
async def process_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        await bot.answer_callback_query(callback_query.id)
        await exit_.cal_date.set()
        await state.update_data(cal_date=date.strftime("%d.%m.%Y"))
        await callback_query.message.answer(f"""<b>Ты выбрал: {date.strftime("%d.%m.%Y")}</b>""", parse_mode="HTML")
        
        await add_new_user(callback_query.message)

# STATE cal_date
async def add_new_user(message: types.Message):
    text="""<b>Укажите время возвращения</b> \n<em>Формат: ЧЧ:ММ</em>"""

    await message.answer(text=text,parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    await exit_.entrance_time.set()

# STATE get_entrance_time
async def state1(message: types.Message, state=FSMContext):
    try:
        ans = message.text
        reader = csv.DictReader(open('database/users.csv', 'rt', encoding='utf8'))
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
                await exit_.reason.set()
            else:
                await message.answer("Вы собираетесь придти после разрешённого Вам времени\nИзмените время возвращения", reply_markup=kb_in) #FIXME
                await state.finish()
        else:
            await message.answer("Введите время в формате 'ЧЧ:ММ'")
            return
    except Exception as e:
        print(e)
        await message.answer("Введите время в формате 'ЧЧ:ММ'")
        return

# STATE reason
async def state3(message: types.Message, state=FSMContext):
    await state.update_data(reason=message.text)
    text="""<b>Вы можете идти</b> \n<em>Когда вернетесь в АГ, нажмите кнопку "Я в АГ"</em>"""
    data = await state.get_data()

    hour_exit = f'0{time.localtime().tm_hour}' if time.localtime().tm_hour < 10 else f'{time.localtime().tm_hour}'
    min_exit = f'0{time.localtime().tm_min}' if time.localtime().tm_min < 10 else f'{time.localtime().tm_min}'
    day_exit = f'0{time.localtime().tm_mday}' if time.localtime().tm_mday < 10 else f'{time.localtime().tm_mday}'
    month_exit = f'0{time.localtime().tm_mon}' if time.localtime().tm_mon < 10 else f'{time.localtime().tm_mon}'
    year_exit = f'{time.localtime().tm_year}'

    users_st = 0
    with open('database/users.csv', 'rt', encoding="utf8") as file:
        reader = csv.reader(file)
        for i in reader:
            if f'{i[0]}' == f'{message.from_user.id}':
                users_st = i[5]
                break


    with open('database/database.csv', 'a', encoding='utf') as file: 
        file.write(f"{f'{users_st}'},{f'{day_exit}.{month_exit}.{year_exit}'},{f'{hour_exit}:{min_exit}'},{data['cal_date']},{data['entrance_time']},{data['reason']},False\n")

    await message.answer(parse_mode="HTML",text=text,reply_markup=kb_out)
    await exit_.flag.set()

# STATE flag
async def state4(message: types.Message, state=FSMContext):
    text="<b>С возвращением!</b>"
    fl, index = check_log(message.from_user.id)
    with open('database/database.csv', 'r', encoding='utf8') as fileREAD:
        data = fileREAD.readlines()
        update_user = data[index].replace("False", "True")
        data[index] = update_user
        update_data = ""
        for user in data:
            update_data += user
    with  open('database/database.csv', 'w', encoding='utf8') as fileWRITE:
        fileWRITE.write(update_data)

    await message.answer(text=text,parse_mode="HTML",reply_markup=kb_in)

    await state.finish()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(exit_calendar, text='Выйти из АГ')
    dp.register_callback_query_handler(process_dialog_calendar, dialog_cal_callback.filter())
    dp.register_message_handler(add_new_user, state=exit_.cal_date)
    dp.register_message_handler(state1, state=exit_.entrance_time)
    dp.register_message_handler(state3, state=exit_.reason)
    dp.register_message_handler(state4, state=exit_.flag)