from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=('.env', 'env'), env_file_encoding='utf-8', env_prefix='HMB_')

	BOT_TOKEN: str = Field(..., description='Telegram bot token')
	DB_URL: str = Field('sqlite:///home_manager.db', description='SQLAlchemy database URL')
	TIMEZONE: str = Field('Europe/Moscow', description='Default timezone')
	LOG_LEVEL: str = Field('INFO', description='Logging level')

	# Feature flags
	ENABLE_SCHEDULER: bool = Field(True, description='Enable APScheduler for reminders')


def get_settings() -> Settings:
	return Settings()  # type: ignore[call-arg]


