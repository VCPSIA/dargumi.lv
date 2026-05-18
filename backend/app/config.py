from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = ""
    numista_api_key: str = ""
    secret_key: str = "changeme"
    database_url: str = "sqlite+aiosqlite:///./kolekcija.db"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    frontend_url: str = "http://localhost:5173"

    google_client_id: str = ""
    facebook_app_id: str = ""
    facebook_app_secret: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
