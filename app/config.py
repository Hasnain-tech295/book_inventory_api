from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Book Inventory API"
    app_version: str = "1.0.0"
    debug: bool = False

    # # Server
    # host: str = "[IP_ADDRESS]"
    # port: int = 8000

    # Database 
    database_url: str = "sqlite:///./books.db"

    # Security
    secret_key: str = "change-me-in-production!"
    # token_expire_minutes: int = 30

    class Config:
        # Load from .env file automatically
        env_file = ".env"
        # env_file_encoding = "utf-8"

        # Allow extra fields without error
        extra = "ignore"

# lru_cache means Settings() is only created ONCE per process.
# Every call to get_settings() returns the same object.
# This is the correct pattern — don't create Settings() on every request
@lru_cache()
def get_settings():
    return Settings()