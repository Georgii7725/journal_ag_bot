from aiogram import executor, types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = "5749373743:AAG930y7um-KMc0Qm_mFACsQr4e_GAHCGQk"
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())