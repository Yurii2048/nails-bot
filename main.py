import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers.user import user
from app.database.models import async_main
from app.database.requests import clear_rec


async def scheduler():
    while True:
        await asyncio.sleep(3600)
        await clear_rec()


async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(user)
    await asyncio.gather(dp.start_polling(bot), scheduler())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
