# Copilot prompt:
# "Provide typed settings using pydantic BaseSettings for Telegram token, owner id, Binance keys, DB url, poll interval and testnet flag."
from pydantic import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    OWNER_TELEGRAM_ID: int
    BINANCE_API_KEY: str
    BINANCE_API_SECRET: str
    BINANCE_TESTNET: bool = True
    DATABASE_URL: str = "sqlite:///./trading.db"
    POLL_INTERVAL_SECONDS: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
