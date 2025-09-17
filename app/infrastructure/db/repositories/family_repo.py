from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import Family, FamilyMember, User, UserPreference


class FamilyRepository:
	def __init__(self, session: Session) -> None:
		self.session = session

	def create_family(self, *, name: str, owner_user_id: int) -> Family:
		family = Family(name=name)
		self.session.add(family)
		self.session.flush()
		member = FamilyMember(family_id=family.id, user_id=owner_user_id, role='owner')
		self.session.add(member)
		return family

	def list_families_for_user(self, *, user_id: int) -> Sequence[Family]:
		stmt = (
			select(Family)
			.join(FamilyMember, FamilyMember.family_id == Family.id)
			.where(FamilyMember.user_id == user_id)
			.order_by(Family.created_at.asc())
		)
		return list(self.session.execute(stmt).scalars().all())

	def ensure_user(self, *, user_id: int, first_name: str | None, last_name: str | None, username: str | None) -> User:
		user = self.session.get(User, user_id)
		if user is None:
			user = User(id=user_id, first_name=first_name, last_name=last_name, username=username)
			self.session.add(user)
		else:
			user.first_name = first_name
			user.last_name = last_name
			user.username = username
		return user

	def join_family(self, *, family_id: int, user_id: int) -> None:
		link = self.session.get(FamilyMember, {'family_id': family_id, 'user_id': user_id})
		if link is None:
			self.session.add(FamilyMember(family_id=family_id, user_id=user_id, role='member'))

	def set_active_family(self, *, user_id: int, family_id: int | None) -> None:
		pref = self.session.get(UserPreference, user_id)
		if pref is None:
			pref = UserPreference(user_id=user_id, active_family_id=family_id)
			self.session.add(pref)
		else:
			pref.active_family_id = family_id

	def get_active_family_id(self, *, user_id: int) -> int | None:
		pref = self.session.get(UserPreference, user_id)
		return pref.active_family_id if pref else None


