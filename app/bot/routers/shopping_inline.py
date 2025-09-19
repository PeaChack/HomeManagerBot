from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from app.infrastructure.db.base import get_session
from app.domain.services.shopping_service import ShoppingService
from app.domain.services.family_service import FamilyService


router = Router(name='shopping_inline')


def _kb_for_items(items):
	buttons = [[InlineKeyboardButton(text=f'✅ {i.title}', callback_data=f'shp_done:{i.id}')]
			for i in items]
	return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command('buy_check'))
async def buy_check(message: Message) -> None:
	# Показывает чек-лист с инлайн-кнопками для текущей/заданной семьи
	with get_session() as session:
		family_id = None
		parts = message.text.split() if message.text else []
		if len(parts) >= 2 and parts[1].isdigit():
			family_id = int(parts[1])
		else:
			family_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
		if family_id is None:
			await message.answer('Не задана семья. Укажи family_id или установи активную: /family_set <id>')
			return
		service = ShoppingService(session)
		items = service.list_items(family_id=family_id, include_done=False)
		if not items:
			await message.answer('Список покупок пуст')
			return
		await message.answer('Отметь купленные позиции:', reply_markup=_kb_for_items(items))


@router.callback_query(F.data.startswith('shp_done:'))
async def on_done(cb: CallbackQuery) -> None:
	item_id = int(cb.data.split(':', 1)[1]) if cb.data else 0
	with get_session() as session:
		service = ShoppingService(session)
		service.done(item_id=item_id)
	await cb.answer('Отмечено')
	if cb.message:
		await cb.message.delete()


@router.callback_query(F.data.startswith('shp_clear:'))
async def on_clear(cb: CallbackQuery) -> None:
	# Очистить купленные позиции в семье
	_, family_id = cb.data.split(':', 1)
	with get_session() as session:
		service = ShoppingService(session)
		service.clear_done(family_id=int(family_id))
	await cb.answer('Очищено')
	if cb.message:
		await cb.message.delete()


