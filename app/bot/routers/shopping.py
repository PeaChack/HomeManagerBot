from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.infrastructure.db.base import get_session
from app.domain.services.shopping_service import ShoppingService


router = Router(name='shopping')


def _parse_family_id(message: Message) -> int | None:
	# MVP: пока берём family_id из числового аргумента команды, позже — активная семья из профиля
	parts = message.text.split() if message.text else []
	if len(parts) >= 2 and parts[1].isdigit():
		return int(parts[1])
	return None


@router.message(Command('buy_add'))
async def buy_add(message: Message) -> None:
	# Формат: /buy_add <family_id> <название>
	parts = message.text.split(maxsplit=2) if message.text else []
	if len(parts) < 3 or not parts[1].isdigit():
		await message.answer('Использование: /buy_add <family_id> <позиция>')
		return
	family_id = int(parts[1])
	title = parts[2].strip()
	if not title:
		await message.answer('Название позиции не может быть пустым')
		return
	with get_session() as session:
		service = ShoppingService(session)
		service.add(family_id=family_id, title=title, created_by=message.from_user.id if message.from_user else None)
		await message.answer(f'Добавлено в покупки: {title}')


@router.message(Command('buy_list'))
async def buy_list(message: Message) -> None:
	# Формат: /buy_list <family_id>
	family_id = _parse_family_id(message)
	if family_id is None:
		await message.answer('Использование: /buy_list <family_id>')
		return
	with get_session() as session:
		service = ShoppingService(session)
		items = service.list(family_id=family_id, include_done=False)
		if not items:
			await message.answer('Список покупок пуст')
			return
		lines = [f'{item.id}. {item.title}' for item in items]
		await message.answer('\n'.join(lines))


@router.message(Command('buy_done'))
async def buy_done(message: Message) -> None:
	# Формат: /buy_done <item_id>
	parts = message.text.split() if message.text else []
	if len(parts) < 2 or not parts[1].isdigit():
		await message.answer('Использование: /buy_done <item_id>')
		return
	item_id = int(parts[1])
	with get_session() as session:
		service = ShoppingService(session)
		updated = service.done(item_id=item_id)
		if updated:
			await message.answer(f'Отмечено как куплено: #{item_id}')
		else:
			await message.answer('Позиция не найдена')


