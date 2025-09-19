from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message

from app.infrastructure.db.base import get_session
from app.domain.services.family_service import FamilyService
from app.domain.services.shopping_service import ShoppingService
from app.bot.keyboards.main import top_items_kb, main_menu_kb


router = Router(name='shopping_add_fsm')


class AddShoppingStates(StatesGroup):
	choosing = State()
	typing = State()


@router.message(Command('buy_add_ui'))
@router.message(F.text == 'Добавить в покупки')
async def start_add_ui(message: Message, state: FSMContext) -> None:
	with get_session() as session:
		fam_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
		if fam_id is None:
			await message.answer('Не задана семья. Установи активную: /family_set <id>', reply_markup=main_menu_kb())
			return
		top = ShoppingService(session).top_titles_for_user(user_id=message.from_user.id, family_id=fam_id, limit=10)
		if not top:
			await message.answer('Введи название позиции для добавления:', reply_markup=top_items_kb([]))
			await state.set_state(AddShoppingStates.typing)
		else:
			await message.answer('Выбери из популярных или введи вручную:', reply_markup=top_items_kb(top))
			await state.set_state(AddShoppingStates.choosing)


@router.message(AddShoppingStates.choosing)
async def choose_or_manual(message: Message, state: FSMContext) -> None:
	text = (message.text or '').strip()
	if text == '✍️ Ввести вручную':
		await message.answer('Введи название позиции:')
		await state.set_state(AddShoppingStates.typing)
		return
	if text == '⬅️ Назад':
		await state.clear()
		await message.answer('Отменено', reply_markup=main_menu_kb())
		return
	# иначе считаем это названием из популярных
	with get_session() as session:
		fam_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
		if fam_id is None:
			await message.answer('Не задана семья. /family_set <id>', reply_markup=main_menu_kb())
			await state.clear()
			return
		ShoppingService(session).add(family_id=fam_id, title=text, created_by=message.from_user.id if message.from_user else None)
	await message.answer(f'Добавлено: {text}', reply_markup=main_menu_kb())
	await state.clear()


@router.message(AddShoppingStates.typing)
async def type_title(message: Message, state: FSMContext) -> None:
	title = (message.text or '').strip()
	if not title:
		await message.answer('Введи корректное название позиции:')
		return
	if title == '⬅️ Назад':
		await state.clear()
		await message.answer('Главное меню', reply_markup=main_menu_kb())
		return
	with get_session() as session:
		fam_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
		if fam_id is None:
			await message.answer('Не задана семья. /family_set <id>', reply_markup=main_menu_kb())
			await state.clear()
			return
		ShoppingService(session).add(family_id=fam_id, title=title, created_by=message.from_user.id if message.from_user else None)
	await message.answer(f'Добавлено: {title}', reply_markup=main_menu_kb())
	await state.clear()


