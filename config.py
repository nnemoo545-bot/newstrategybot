import os
from dotenv import load_dotenv

# Load .env file (if present)
load_dotenv()

class Settings:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    OWNER_TELEGRAM_ID: int = int(os.getenv("OWNER_TELEGRAM_ID") or 0)
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    BINANCE_TESTNET: bool = os.getenv("BINANCE_TESTNET", "true").lower() in ("1", "true", "yes")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trading.db")
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS") or 5)

settings = Settings()
