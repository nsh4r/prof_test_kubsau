from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # database
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def postgres_url(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env', extra='allow')


settings = Settings()
