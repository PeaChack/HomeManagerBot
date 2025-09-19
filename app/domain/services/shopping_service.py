from typing import Sequence

from sqlalchemy.orm import Session

from app.domain.models import ShoppingItem
from app.infrastructure.db.repositories.shopping_repo import ShoppingRepository


class ShoppingService:
	def __init__(self, session: Session) -> None:
		self.repo = ShoppingRepository(session)

	def add(self, *, family_id: int, title: str, created_by: int | None = None) -> ShoppingItem:
		return self.repo.add_item(family_id=family_id, title=title, created_by=created_by)

	def list_items(self, *, family_id: int, include_done: bool = False) -> Sequence[ShoppingItem]:
		return self.repo.list_items(family_id=family_id, include_done=include_done)

	def done(self, *, item_id: int) -> int:
		return self.repo.mark_done(item_id=item_id)

	def clear_done(self, *, family_id: int) -> int:
		return self.repo.clear_done(family_id=family_id)

	def top_titles_for_user(self, *, user_id: int, family_id: int, limit: int = 10) -> list[str]:
		return self.repo.top_titles_for_user(user_id=user_id, family_id=family_id, limit=limit)


