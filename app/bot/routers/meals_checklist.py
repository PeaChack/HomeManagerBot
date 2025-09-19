from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from app.infrastructure.db.base import get_session
from app.domain.services.family_service import FamilyService
from app.domain.services.meals_service import MealsService
from app.domain.services.shopping_service import ShoppingService


router = Router(name='meals_checklist')


def _kb_for_ingredients(dish_id: int, ings):
	buttons = [[InlineKeyboardButton(text=f'✅ {i.title}', callback_data=f'ing_have:{dish_id}:{i.id}'),
	            InlineKeyboardButton(text=f'🛒', callback_data=f'ing_need:{dish_id}:{i.id}')]
	           for i in ings]
	return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command('dish_check'))
async def dish_check(message: Message) -> None:
	# /dish_check <dish_id>
	parts = message.text.split() if message.text else []
	if len(parts) != 2 or not parts[1].isdigit():
		await message.answer('Использование: /dish_check <dish_id>')
		return
	dish_id = int(parts[1])
	with get_session() as session:
		fam_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
		if fam_id is None:
			await message.answer('Не задана семья. Установи активную: /family_set <id>')
			return
		meals = MealsService(session)
		ings = meals.list_ingredients(dish_id=dish_id)
		if not ings:
			await message.answer('У блюда нет ингредиентов')
			return
		await message.answer('Отметь ингредиенты:', reply_markup=_kb_for_ingredients(dish_id, ings))


@router.callback_query(F.data.startswith('ing_need:'))
async def on_need(cb: CallbackQuery) -> None:
	# Добавляет ингредиент в покупки
	_, dish_id, ing_id = cb.data.split(':', 2)
	with get_session() as session:
		# Получим ингредиент
		meals = MealsService(session)
		ings = meals.list_ingredients(dish_id=int(dish_id))
		ing = next((i for i in ings if i.id == int(ing_id)), None)
		if ing is None:
			await cb.answer('Ингредиент не найден')
			return
		fam_id = FamilyService(session).get_active_id(user_id=cb.from_user.id if cb.from_user else 0)
		if fam_id is None:
			await cb.answer('Нет активной семьи')
			return
		ShoppingService(session).add(family_id=fam_id, title=ing.title, created_by=cb.from_user.id if cb.from_user else None)
	await cb.answer('Добавлено в покупки')


@router.callback_query(F.data.startswith('ing_have:'))
async def on_have(cb: CallbackQuery) -> None:
	await cb.answer('Отмечено как есть')


