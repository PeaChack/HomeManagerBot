from aiogram.types import (
	ReplyKeyboardMarkup,
	KeyboardButton,
	InlineKeyboardMarkup,
	InlineKeyboardButton,
)


def main_menu_kb() -> ReplyKeyboardMarkup:
	return ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Покупки'), KeyboardButton(text='Блюда')],
			[KeyboardButton(text='Меню'), KeyboardButton(text='Семья')],
		],
		resize_keyboard=True,
		one_time_keyboard=False,
		input_field_placeholder='Выберите раздел',
	)


def shopping_list_inline(items, include_clear: bool = True, family_id: int | None = None) -> InlineKeyboardMarkup:
	rows = [[InlineKeyboardButton(text=f'✔️ {i.title}', callback_data=f'shp_done:{i.id}')]
			for i in items]
	if include_clear and family_id:
		rows.append([InlineKeyboardButton(text='🧹 Очистить купленные', callback_data=f'shp_clear:{family_id}')])
	return InlineKeyboardMarkup(inline_keyboard=rows)


def top_items_kb(titles: list[str]) -> ReplyKeyboardMarkup:
	rows = []
	row: list[KeyboardButton] = []
	for idx, t in enumerate(titles):
		row.append(KeyboardButton(text=t))
		if (idx + 1) % 2 == 0:
			rows.append(row)
			row = []
	if row:
		rows.append(row)
	rows.append([KeyboardButton(text='✍️ Ввести вручную'), KeyboardButton(text='⬅️ Назад')])
	return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)


def shopping_actions_kb() -> ReplyKeyboardMarkup:
	return ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Добавить в покупки')],
			[KeyboardButton(text='⬅️ Назад')],
		],
		resize_keyboard=True,
		one_time_keyboard=False,
	)


