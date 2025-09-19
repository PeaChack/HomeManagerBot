import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.core.settings import get_settings
from app.bot.routers.core import router as core_router
from app.bot.routers.shopping import router as shopping_router
from app.bot.routers.shopping_inline import router as shopping_inline_router
from app.bot.routers.family import router as family_router
from app.bot.routers.meals import router as meals_router
from app.infrastructure.db.init_db import create_all


async def main() -> None:
	settings = get_settings()
	logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

	bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()

	dp.include_router(core_router)
	dp.include_router(shopping_router)
	dp.include_router(shopping_inline_router)
	dp.include_router(family_router)
	dp.include_router(meals_router)

	create_all()  # ensure tables exist for MVP
	await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())


