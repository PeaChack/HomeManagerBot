from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.infrastructure.db.base import get_session
from app.domain.services.family_service import FamilyService


router = Router(name='family')


@router.message(Command('family_create'))
async def family_create(message: Message) -> None:
	# /family_create <название>
	parts = message.text.split(maxsplit=1) if message.text else []
	if len(parts) < 2 or not parts[1].strip():
		await message.answer('Использование: /family_create <название>')
		return
	with get_session() as session:
		service = FamilyService(session)
		user = message.from_user
		family = service.create(
			name=parts[1].strip(),
			owner_user_id=user.id if user else 0,
			user_ctx=dict(first_name=user.first_name if user else None, last_name=user.last_name if user else None, username=user.username if user else None),
		)
		await message.answer(f'Семья создана: {family.name} (id={family.id}). Активная семья обновлена.')


@router.message(Command('family_list'))
async def family_list(message: Message) -> None:
	with get_session() as session:
		service = FamilyService(session)
		user_id = message.from_user.id if message.from_user else 0
		families = service.list_for_user(user_id=user_id)
		if not families:
			await message.answer('У тебя пока нет семей. Создай: /family_create <название>')
			return
		lines = [f'{f.id}. {f.name}' for f in families]
		await message.answer('\n'.join(lines))


@router.message(Command('family_set'))
async def family_set(message: Message) -> None:
	# /family_set <family_id|null>
	parts = message.text.split() if message.text else []
	if len(parts) != 2:
		await message.answer('Использование: /family_set <family_id|null>')
		return
	arg = parts[1].lower()
	family_id = None if arg == 'null' else (int(arg) if arg.isdigit() else None)
	if arg != 'null' and family_id is None:
		await message.answer('Укажи числовой id или null')
		return
	with get_session() as session:
		service = FamilyService(session)
		user_id = message.from_user.id if message.from_user else 0
		service.set_active(user_id=user_id, family_id=family_id)
		await message.answer('Активная семья обновлена' if family_id else 'Активная семья сброшена')


@router.message(Command('family_join'))
async def family_join(message: Message) -> None:
	# /family_join <family_id>
	parts = message.text.split() if message.text else []
	if len(parts) != 2 or not parts[1].isdigit():
		await message.answer('Использование: /family_join <family_id>')
		return
	family_id = int(parts[1])
	with get_session() as session:
		service = FamilyService(session)
		user = message.from_user
		service.join(
			family_id=family_id,
			user_id=user.id if user else 0,
			user_ctx=dict(first_name=user.first_name if user else None, last_name=user.last_name if user else None, username=user.username if user else None),
		)
		await message.answer(f'Присоединился к семье #{family_id}')


