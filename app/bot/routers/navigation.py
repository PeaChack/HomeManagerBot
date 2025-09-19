from aiogram import Router, F
from aiogram.types import Message

from app.infrastructure.db.base import get_session
from app.domain.services.family_service import FamilyService
from app.domain.services.shopping_service import ShoppingService
from app.bot.keyboards.main import main_menu_kb, shopping_list_inline, shopping_actions_kb


router = Router(name='navigation')


@router.message(F.text == 'Покупки')
async def nav_shopping(message: Message) -> None:
	with get_session() as session:
		fam_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
		if fam_id is None:
			await message.answer('Не задана семья. Сначала создайте/выберите семью в разделе «Семья».', reply_markup=main_menu_kb())
			return
		items = ShoppingService(session).list_items(family_id=fam_id)
		if not items:
			await message.answer('Список покупок пуст', reply_markup=shopping_actions_kb())
			return
		await message.answer('Список покупок:', reply_markup=shopping_list_inline(items, include_clear=True, family_id=fam_id))
		await message.answer('Действия:', reply_markup=shopping_actions_kb())


@router.message(F.text == 'Семья')
async def nav_family(message: Message) -> None:
	await message.answer('Управление семьями: /family_create, /family_list, /family_set, /family_join', reply_markup=main_menu_kb())


@router.message(F.text == 'Блюда')
async def nav_dishes(message: Message) -> None:
	await message.answer('Работа с блюдами: /dish_add, /dish_list, /ing_add, /dish_check', reply_markup=main_menu_kb())


@router.message(F.text == 'Меню')
async def nav_menu(message: Message) -> None:
	await message.answer('Планирование меню: /menu_add, /menu_list', reply_markup=main_menu_kb())


@router.message(F.text == '⬅️ Назад')
async def nav_back(message: Message) -> None:
	await message.answer('Главное меню', reply_markup=main_menu_kb())


