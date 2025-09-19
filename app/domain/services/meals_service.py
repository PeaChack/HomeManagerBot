from datetime import date
from typing import Sequence

from sqlalchemy.orm import Session

from app.domain.models import Dish, DishIngredient, PlannedMeal
from app.infrastructure.db.repositories.meals_repo import MealsRepository


class MealsService:
	def __init__(self, session: Session) -> None:
		self.repo = MealsRepository(session)

	def add_dish(self, *, family_id: int, title: str, created_by: int | None = None) -> Dish:
		return self.repo.add_dish(family_id=family_id, title=title, created_by=created_by)

	def list_dishes(self, *, family_id: int) -> Sequence[Dish]:
		return self.repo.list_dishes(family_id=family_id)

	def add_ingredient(self, *, dish_id: int, title: str) -> DishIngredient:
		return self.repo.add_ingredient(dish_id=dish_id, title=title)

	def list_ingredients(self, *, dish_id: int) -> Sequence[DishIngredient]:
		return self.repo.list_ingredients(dish_id=dish_id)

	def plan_meal(self, *, family_id: int, on_date: date, dish_id: int, notes: str | None = None) -> PlannedMeal:
		return self.repo.plan_meal(family_id=family_id, on_date=on_date, dish_id=dish_id, notes=notes)

	def list_meals(self, *, family_id: int, on_date: date) -> Sequence[PlannedMeal]:
		return self.repo.list_meals(family_id=family_id, on_date=on_date)


