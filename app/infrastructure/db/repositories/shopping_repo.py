from typing import Sequence

from sqlalchemy import select, update, delete
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


