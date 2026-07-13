from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Loaded dynamically from the .env file (to keep credentials secure)
    DATABASE_URL: str
    PROJECT_NAME: str = "Smart Civic Platform API"
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
