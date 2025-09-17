from typing import Sequence

from sqlalchemy.orm import Session

from app.domain.models import Family
from app.infrastructure.db.repositories.family_repo import FamilyRepository


class FamilyService:
	def __init__(self, session: Session) -> None:
		self.repo = FamilyRepository(session)

	def create(self, *, name: str, owner_user_id: int, user_ctx: dict | None = None) -> Family:
		self.repo.ensure_user(
			user_id=owner_user_id,
			first_name=(user_ctx or {}).get('first_name'),
			last_name=(user_ctx or {}).get('last_name'),
			username=(user_ctx or {}).get('username'),
		)
		family = self.repo.create_family(name=name, owner_user_id=owner_user_id)
		self.repo.set_active_family(user_id=owner_user_id, family_id=family.id)
		return family

	def list_for_user(self, *, user_id: int) -> Sequence[Family]:
		return self.repo.list_families_for_user(user_id=user_id)

	def join(self, *, family_id: int, user_id: int, user_ctx: dict | None = None) -> None:
		self.repo.ensure_user(
			user_id=user_id,
			first_name=(user_ctx or {}).get('first_name'),
			last_name=(user_ctx or {}).get('last_name'),
			username=(user_ctx or {}).get('username'),
		)
		self.repo.join_family(family_id=family_id, user_id=user_id)

	def set_active(self, *, user_id: int, family_id: int | None) -> None:
		self.repo.set_active_family(user_id=user_id, family_id=family_id)

	def get_active_id(self, *, user_id: int) -> int | None:
		return self.repo.get_active_family_id(user_id=user_id)


