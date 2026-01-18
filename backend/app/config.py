from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    resend_api_key: str = ""

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # App Config
    demo_alert_email: str = "alerts@kliuiev.com"
    frontend_url: str = "https://dealhunter.kliuiev.com"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
