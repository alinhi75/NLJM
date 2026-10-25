from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://nljm:nljm@localhost:5432/nljm"

    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "nl"

    greenhouse_boards: str = ""

    @property
    def greenhouse_board_list(self) -> list[str]:
        return [b.strip() for b in self.greenhouse_boards.split(",") if b.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
