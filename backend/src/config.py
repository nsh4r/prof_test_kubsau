from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # database
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def postgres_url(self):
        # Экранируем специальные символы в пароле
        safe_password = quote_plus(self.DB_PASSWORD)
        return f'postgresql+asyncpg://{self.DB_USER}:{safe_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def test_postgres_url(self):
        safe_password = quote_plus(self.DB_PASSWORD)
        return f'postgresql+asyncpg://{self.DB_USER}:{safe_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}_test'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )

settings = Settings()
