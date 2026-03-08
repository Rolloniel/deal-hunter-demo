from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    resend_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dealhunter"

    # Auth
    jwt_secret: str = "change-me-in-production"
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    # App Config
    demo_alert_email: str = "alerts@kliuiev.com"
    frontend_url: str = "https://deals.kliuiev.com"
    backend_url: str = "https://api-deals.kliuiev.com"

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
