from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.infrastructure.db.base import get_session
from app.domain.services.family_service import FamilyService
from app.domain.services.meals_service import MealsService


router = Router(name='meals')


def _active_family(session, message: Message) -> int | None:
	return FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)


@router.message(Command('dish_add'))
async def dish_add(message: Message) -> None:
	parts = message.text.split(maxsplit=1) if message.text else []
	if len(parts) < 2:
		await message.answer('Использование: /dish_add <название>')
		return
	title = parts[1].strip()
	with get_session() as session:
		fam_id = _active_family(session, message)
		if fam_id is None:
			await message.answer('Не задана семья. Установи активную: /family_set <id>')
			return
		service = MealsService(session)
		service.add_dish(family_id=fam_id, title=title, created_by=message.from_user.id if message.from_user else None)
		await message.answer(f'Блюдо создано: {title}')


@router.message(Command('dish_list'))
async def dish_list(message: Message) -> None:
	with get_session() as session:
		fam_id = _active_family(session, message)
		if fam_id is None:
			await message.answer('Не задана семья. Установи активную: /family_set <id>')
			return
		service = MealsService(session)
		dishes = service.list_dishes(family_id=fam_id)
		if not dishes:
			await message.answer('Блюд пока нет')
			return
		lines = [f'{d.id}. {d.title}' for d in dishes]
		await message.answer('\n'.join(lines))


@router.message(Command('ing_add'))
async def ing_add(message: Message) -> None:
	# /ing_add <dish_id> <ингредиент>
	parts = message.text.split(maxsplit=2) if message.text else []
	if len(parts) < 3 or not parts[1].isdigit():
		await message.answer('Использование: /ing_add <dish_id> <ингредиент>')
		return
	dish_id = int(parts[1])
	title = parts[2].strip()
	with get_session() as session:
		service = MealsService(session)
		service.add_ingredient(dish_id=dish_id, title=title)
		await message.answer('Ингредиент добавлен')


@router.message(Command('menu_add'))
async def menu_add(message: Message) -> None:
	# /menu_add <YYYY-MM-DD> <dish_id>
	parts = message.text.split() if message.text else []
	if len(parts) != 3 or not parts[2].isdigit():
		await message.answer('Использование: /menu_add <YYYY-MM-DD> <dish_id>')
		return
	try:
		on_date = date.fromisoformat(parts[1])
	except ValueError:
		await message.answer('Неверная дата. Используй формат YYYY-MM-DD')
		return
	dish_id = int(parts[2])
	with get_session() as session:
		fam_id = _active_family(session, message)
		if fam_id is None:
			await message.answer('Не задана семья. Установи активную: /family_set <id>')
			return
		service = MealsService(session)
		service.plan_meal(family_id=fam_id, on_date=on_date, dish_id=dish_id)
		await message.answer('Блюдо запланировано')


@router.message(Command('menu_list'))
async def menu_list(message: Message) -> None:
	# /menu_list <YYYY-MM-DD>
	parts = message.text.split() if message.text else []
	if len(parts) != 2:
		await message.answer('Использование: /menu_list <YYYY-MM-DD>')
		return
	try:
		on_date = date.fromisoformat(parts[1])
	except ValueError:
		await message.answer('Неверная дата. Используй формат YYYY-MM-DD')
		return
	with get_session() as session:
		fam_id = _active_family(session, message)
		if fam_id is None:
			await message.answer('Не задана семья. Установи активную: /family_set <id>')
			return
		service = MealsService(session)
		meals = service.list_meals(family_id=fam_id, on_date=on_date)
		if not meals:
			await message.answer('На эту дату ничего не запланировано')
			return
		lines = [f'{m.id}. блюдо #{m.dish_id}' for m in meals]
		await message.answer('\n'.join(lines))


