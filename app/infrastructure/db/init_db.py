from app.infrastructure.db.base import Base, engine
from app.domain import models  # noqa: F401  ensure models are imported


def create_all() -> None:
	Base.metadata.create_all(bind=engine)


