from typing import Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session

from app.domain.models import ShoppingItem


class ShoppingRepository:
	def __init__(self, session: Session) -> None:
		self.session = session

	def add_item(self, *, family_id: int, title: str, qty: float | None = None, unit: str | None = None, created_by: int | None = None) -> ShoppingItem:
		item = ShoppingItem(family_id=family_id, title=title, qty=qty, unit=unit, created_by=created_by)
		self.session.add(item)
		return item

	def list_items(self, *, family_id: int, include_done: bool = False) -> Sequence[ShoppingItem]:
		stmt = select(ShoppingItem).where(ShoppingItem.family_id == family_id)
		if not include_done:
			stmt = stmt.where(ShoppingItem.is_done.is_(False))
		stmt = stmt.order_by(ShoppingItem.created_at.asc())
		return list(self.session.execute(stmt).scalars().all())

	def mark_done(self, *, item_id: int) -> int:
		stmt = update(ShoppingItem).where(ShoppingItem.id == item_id).values(is_done=True)
		result = self.session.execute(stmt)
		return result.rowcount or 0

	def clear_done(self, *, family_id: int) -> int:
		stmt = delete(ShoppingItem).where(ShoppingItem.family_id == family_id, ShoppingItem.is_done.is_(True))
		result = self.session.execute(stmt)
		return result.rowcount or 0

	def top_titles_for_user(self, *, user_id: int, family_id: int, limit: int = 10) -> list[str]:
		stmt = (
			select(ShoppingItem.title, func.count(ShoppingItem.id).label('cnt'))
			.where(ShoppingItem.created_by == user_id, ShoppingItem.family_id == family_id)
			.group_by(ShoppingItem.title)
			.order_by(func.count(ShoppingItem.id).desc())
			.limit(limit)
		)
		rows = self.session.execute(stmt).all()
		return [r[0] for r in rows]


