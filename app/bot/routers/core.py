from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router(name='core')


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
	await message.answer(
		"Привет! Я домашний менеджер. Выбери семью или создай новую в ближайших обновлениях."
	)


