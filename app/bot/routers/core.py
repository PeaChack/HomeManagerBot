from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main import main_menu_kb

router = Router(name='core')


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
	await message.answer(
		"Привет! Я домашний менеджер. Выберите раздел ниже.",
		reply_markup=main_menu_kb(),
	)


