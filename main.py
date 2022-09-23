from handlers import registration, exit, other
from create_bot import *

async def on_startup(_):
    print("BOT IS STARTING")

registration.register_handlers(dp)
exit.register_handlers(dp)
other.register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
