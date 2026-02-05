from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Store API"
    # Mantemos apenas uma declaração com o valor padrão
    DATABASE_URL: str = "mongodb://localhost:27017/tdd_store"
    ROOT_PATH: str = "/"

    # O SettingsConfigDict garante que, se existir um arquivo .env,
    # os valores lá dentro terão prioridade sobre os padrões acima.
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
