from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.infrastructure.db.base import get_session
from app.domain.services.shopping_service import ShoppingService
from app.domain.services.family_service import FamilyService
from app.bot.keyboards.main import shopping_list_inline


router = Router(name='shopping')


def _get_family_id_or_hint(message: Message, session) -> int | None:
    parts = message.text.split() if message.text else []
    fam_id = None
    if len(parts) >= 2 and parts[1].isdigit():
        fam_id = int(parts[1])
    else:
        fam_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
    return fam_id


@router.message(Command('buy_add'))
async def buy_add(message: Message) -> None:
    # Формат: /buy_add [family_id] <название>
    parts = message.text.split(maxsplit=2) if message.text else []
    if len(parts) < 2:
        await message.answer('Использование: /buy_add [family_id] <позиция>')
        return
    with get_session() as session:
        family_id = None
        title = ''
        if len(parts) >= 3 and parts[1].isdigit():
            family_id = int(parts[1])
            title = parts[2].strip()
        else:
            family_id = FamilyService(session).get_active_id(user_id=message.from_user.id if message.from_user else 0)
            title = parts[1].strip()
        if not family_id:
            await message.answer('Не задана семья. Укажи family_id или установи активную: /family_set <id>')
            return
        if not title:
            await message.answer('Название позиции не может быть пустым')
            return
        service = ShoppingService(session)
        service.add(family_id=family_id, title=title, created_by=message.from_user.id if message.from_user else None)
        await message.answer(f'Добавлено в покупки: {title}')



@router.message(Command('buy_list'))
async def buy_list(message: Message) -> None:
    # Формат: /buy_list [family_id]
    with get_session() as session:
        family_id = _get_family_id_or_hint(message, session)
        if family_id is None:
            await message.answer('Не задана семья. Укажи family_id или установи активную: /family_set <id>')
            return
        service = ShoppingService(session)
        items = service.list_items(family_id=family_id, include_done=False)
        if not items:
            await message.answer('Список покупок пуст')
            return
        await message.answer('Список покупок:', reply_markup=shopping_list_inline(items, include_clear=True, family_id=family_id))


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


