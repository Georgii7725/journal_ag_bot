from keyboards import *
from create_bot import *
from aiogram_calendar import dialog_cal_callback, DialogCalendar
import time
from work_bd import *

class exit_(StatesGroup):
    cal_date = State()          # Дата возвращения
    entrance_time = State()     # Время возвращения
    reason = State()            # Причина возвращения

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
        now=time.localtime()
        sel = date.timetuple()
        if now.tm_year <= sel.tm_year and now.tm_mon <= sel.tm_mon and now.tm_mday <= sel.tm_mday:
            await bot.answer_callback_query(callback_query.id)
            await exit_.cal_date.set()
            await state.update_data(cal_date=date.strftime("%d.%m.%Y"))
            await callback_query.message.answer(f"""<b>Ты выбрал: {date.strftime("%d.%m.%Y")}</b>""", parse_mode="HTML")
        
            await add_new_user(callback_query.message)
        else:
            await bot.answer_callback_query(callback_query.id)
            await state.finish()
            await callback_query.message.answer(f'<b>Дата прихода меньше текущей</b>', parse_mode="HTML")
            await exit_calendar(callback_query.message)

# STATE cal_date
async def add_new_user(message: types.Message):
    text="""<b>Укажите время возвращения</b> \n<em>Формат: ЧЧ:ММ</em>"""

    await message.answer(text=text,parse_mode="HTML",reply_markup=ReplyKeyboardRemove())
    await exit_.entrance_time.set()

# STATE get_entrance_time
async def state1(message: types.Message, state=FSMContext):
    try:
        ans = message.text

        hour_entrance = ans[0]+ans[1]
        min_entrance = ans[3]+ans[4]
        hour_entrance_int = int(hour_entrance)
        min_entrance_int = int(min_entrance)
        al_time = get_al_time_from_users(message.from_user.id)
        al_time = al_time.split("/")
        
        if(ans[2] == ":"):
            hour_al_start = al_time[0][0] + al_time[0][1]
            min_al_start = al_time[0][3] + al_time[0][4]
            hour_al_end = al_time[1][0] + al_time[1][1]
            min_al_end = al_time[1][3] + al_time[1][4]
            if (hour_al_start < hour_entrance or (hour_al_start == hour_entrance and min_entrance <= min_al_start)) and (hour_entrance < hour_al_end or (hour_entrance == hour_al_end and min_entrance <= min_al_end)):
                text="""<b>Укажите причину выхода</b>"""
                await state.update_data(entrance_time = f'{hour_entrance}:{min_entrance}')
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
    st = get_st(str(message.from_user.id))
    
    params = [st, f'{day_exit}.{month_exit}.{year_exit}', f'{hour_exit}:{min_exit}', data['cal_date'], data['entrance_time'], data['reason']]
    add_exit(params)
    
    await message.answer(parse_mode="HTML",text=text,reply_markup=kb_out)
    await state.finish()

# STATE flag
async def entrance(message: types.Message):
    text="<b>С возвращением!</b>"
    st = get_st(str(message.from_user.id))
    update_database(st)
    
    await message.answer(text=text,parse_mode="HTML",reply_markup=kb_in)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(exit_calendar, text='Выйти из АГ')
    dp.register_callback_query_handler(process_dialog_calendar, dialog_cal_callback.filter())
    dp.register_message_handler(add_new_user, state=exit_.cal_date)
    dp.register_message_handler(state1, state=exit_.entrance_time)
    dp.register_message_handler(state3, state=exit_.reason)
    dp.register_message_handler(entrance, text='Я в АГ')