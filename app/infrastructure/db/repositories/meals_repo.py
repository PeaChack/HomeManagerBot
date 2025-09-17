from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import Dish, DishIngredient, PlannedMeal


class MealsRepository:
	def __init__(self, session: Session) -> None:
		self.session = session

	def add_dish(self, *, family_id: int, title: str, created_by: int | None = None) -> Dish:
		dish = Dish(family_id=family_id, title=title, created_by=created_by)
		self.session.add(dish)
		return dish

	def list_dishes(self, *, family_id: int) -> Sequence[Dish]:
		stmt = select(Dish).where(Dish.family_id == family_id).order_by(Dish.title.asc())
		return list(self.session.execute(stmt).scalars().all())

	def add_ingredient(self, *, dish_id: int, title: str) -> DishIngredient:
		ing = DishIngredient(dish_id=dish_id, title=title)
		self.session.add(ing)
		return ing

	def plan_meal(self, *, family_id: int, on_date: date, dish_id: int, notes: str | None = None) -> PlannedMeal:
		pm = PlannedMeal(family_id=family_id, date=on_date, dish_id=dish_id, notes=notes)
		self.session.add(pm)
		return pm

	def list_meals(self, *, family_id: int, on_date: date) -> Sequence[PlannedMeal]:
		stmt = select(PlannedMeal).where(PlannedMeal.family_id == family_id, PlannedMeal.date == on_date)
		return list(self.session.execute(stmt).scalars().all())


