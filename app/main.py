import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.core.settings import get_settings
from app.bot.routers.core import router as core_router


async def main() -> None:
	settings = get_settings()
	logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

	bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
	dp = Dispatcher()

	dp.include_router(core_router)

	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())


