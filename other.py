from email.message import Message
from keyboards import *
from create_bot import *

# START COMMAND
async def get_command_start(message: types.Message):
    
    answer_start = f"Приветствую, {message.from_user.full_name}. Этот бот поможет вам выйти из АГ. Чтобы больше узнать о функционале, воспользуйтесь кнопкой <b>Помощь</b>"""

    await message.answer(text=answer_start,parse_mode="HTML",reply_markup=kb_start)

# HELP COMMAND
async def get_command_help_callback(callback: types.CallbackQuery):

    help_answer = """    <b>Регистрация</b> - <em>Вам необходимо зарегистрироваться, чтобы пользоваться ботом. Для регистрации потребуется ваше ФИО, а также ваша почта st.</em>\n
    <b>Выйти из АГ</b> и <b>Я в АГ</b> - <em>после регистрации у Вас появится доступ к функциям "журнала": чтобы выйти из АГ, нажмите на кнопку 'Выйти из АГ', укажите предполагаемое время возвращения, а также причину, по которой вы покидаете АГ.</em>\n
    <b>Обратная связь</b> - <em>с помощью этой кнопки Вы можете оставить свой отзыв, комментарий или предложение, чтобы наша команда могла улучшить работу бота.</em>"""

    # await callback.answer_callback_query(callback.id)
    await callback.message.answer(text=help_answer,parse_mode="HTML", reply_markup=kb_help)

async def get_command_help_message(message: Message):
    
    help_answer = """    <b>Регистрация</b> - <em>Вам необходимо зарегистрироваться, чтобы пользоваться ботом. Для регистрации потребуется ваше ФИО, а также ваша почта st.</em>\n
    <b>Выйти из АГ</b> и <b>Я в АГ</b> - <em>после регистрации у Вас появится доступ к функциям "журнала": чтобы выйти из АГ, нажмите на кнопку 'Выйти из АГ', укажите предполагаемое время возвращения, а также причину, по которой вы покидаете АГ.</em>\n
    <b>Обратная связь</b> - <em>с помощью этой кнопки Вы можете оставить свой отзыв, комментарий или предложение, чтобы наша команда могла улучшить работу бота.</em>"""

    await message.answer(text=help_answer,parse_mode="HTML")

# USER INFO COMMAND
async def print_user_info(message: types.Message):
    chat_id=str(message.from_user.id)
    flag, index = check_log(chat_id)
    if flag:
        with open('database/users.csv', 'r', encoding='utf8') as file:
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
        my_ans = "<b>Вы не вошли в систему или не зарегистрированы в ней</b>.\n <em>Для подробной информации нажмите на <b>Помощь</b></em>"
    await message.answer(text=my_ans,parse_mode="HTML", reply_markup=kb_in)

# ROUND CONNECT FROM USER
async def round_connect_from_users(message: types.Message):
    text="""<b>Обратная связь</b>\n<em>Если у вас есть пожелания, просьбы для улучшения нашего бота</em>\n<em>или вы нашли ошибку в работе бота, то оставте отзыв в Google Forms.</em>\n<em>Этот комментарий останеться </em><b>АНОНИМНЫМ:</b>\n<a href="https://forms.gle/ovk73RWEPuCqbCd36">Google Forms</a>"""

    await message.answer(text=text, parse_mode="HTML")

# Проверка залогинен пользователь или нет по telegram id
def check_log(user_id: str):
    with open('database/users.csv', 'r') as file:
        for index, user in enumerate(file.readlines()):
            user = user.split(',')
            if user_id == user[0]:
                return True, index
        return False, -1

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(get_command_start, commands=['start'])
    dp.register_callback_query_handler(get_command_help_callback, text=['HELP'])
    dp.register_message_handler(get_command_help_message, text=['Помощь'])
    dp.register_message_handler(print_user_info, text=['Профиль'])
    dp.register_message_handler(round_connect_from_users, text=['Обратная связь'])