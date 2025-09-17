from datetime import datetime

from sqlalchemy import Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class Family(Base):
	__tablename__ = 'family'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(100), nullable=False)
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

	members: Mapped[list['FamilyMember']] = relationship(back_populates='family', cascade='all, delete-orphan')
	shopping_items: Mapped[list['ShoppingItem']] = relationship(back_populates='family', cascade='all, delete-orphan')


class User(Base):
	__tablename__ = 'user'

	id: Mapped[int] = mapped_column(Integer, primary_key=True)  # Telegram user_id
	first_name: Mapped[str | None] = mapped_column(String(100))
	last_name: Mapped[str | None] = mapped_column(String(100))
	username: Mapped[str | None] = mapped_column(String(100))

	memberships: Mapped[list['FamilyMember']] = relationship(back_populates='user', cascade='all, delete-orphan')


class FamilyMember(Base):
	__tablename__ = 'family_member'

	family_id: Mapped[int] = mapped_column(ForeignKey('family.id'), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
	role: Mapped[str] = mapped_column(String(20), default='member', nullable=False)

	family: Mapped[Family] = relationship(back_populates='members')
	user: Mapped[User] = relationship(back_populates='memberships')


class ShoppingItem(Base):
	__tablename__ = 'shopping_item'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	family_id: Mapped[int] = mapped_column(ForeignKey('family.id'), nullable=False, index=True)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	qty: Mapped[float | None] = mapped_column()
	unit: Mapped[str | None] = mapped_column(String(20))
	is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	created_by: Mapped[int | None] = mapped_column(ForeignKey('user.id'))
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

	family: Mapped[Family] = relationship(back_populates='shopping_items')


class UserPreference(Base):
	__tablename__ = 'user_preference'

	user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
	active_family_id: Mapped[int | None] = mapped_column(ForeignKey('family.id'))


class Dish(Base):
	__tablename__ = 'dish'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	family_id: Mapped[int] = mapped_column(ForeignKey('family.id'), index=True)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	instructions: Mapped[str | None] = mapped_column(String)
	created_by: Mapped[int | None] = mapped_column(ForeignKey('user.id'))

	ingredients: Mapped[list['DishIngredient']] = relationship(back_populates='dish', cascade='all, delete-orphan')


class DishIngredient(Base):
	__tablename__ = 'dish_ingredient'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	dish_id: Mapped[int] = mapped_column(ForeignKey('dish.id'), index=True)
	title: Mapped[str] = mapped_column(String(200), nullable=False)
	qty: Mapped[float | None] = mapped_column()
	unit: Mapped[str | None] = mapped_column(String(20))

	dish: Mapped[Dish] = relationship(back_populates='ingredients')


class PlannedMeal(Base):
	__tablename__ = 'planned_meal'

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	family_id: Mapped[int] = mapped_column(ForeignKey('family.id'), index=True)
	date: Mapped[Date] = mapped_column(Date, index=True)
	dish_id: Mapped[int] = mapped_column(ForeignKey('dish.id'), index=True)
	notes: Mapped[str | None] = mapped_column(String)




