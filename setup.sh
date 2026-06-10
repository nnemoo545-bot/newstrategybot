#!/usr/bin/env bash
set -euo pipefail

echo "Running setup for trading bot..."
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# 1) Create venv if missing
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate venv for the rest of the script
# shellcheck source=/dev/null
. venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

# 2) Install minimal safe dependencies
# We avoid installing 'pydantic' v2 and uvloop issues; use python-dotenv and sqlalchemy/requests
pip install python-dotenv sqlalchemy>=1.4 alembic requests python-telegram-bot~=20.3 pytest aiosqlite

# 3) Add pydantic-settings compatibility if pydantic v2 is present
if pip show pydantic >/dev/null 2>&1; then
  echo "pydantic is installed; ensuring pydantic-settings is present"
  pip install pydantic-settings || true
fi

# 4) Create .env from example if missing
if [ ! -f .env ]; then
  echo "Creating .env from .env.example (PLEASE EDIT .env and fill secrets)"
  cp .env.example .env
  echo "Remember to fill TELEGRAM_TOKEN, OWNER_TELEGRAM_ID, BINANCE_API_KEY, BINANCE_API_SECRET in .env"
fi

# 5) Create DB
python create_db.py || true

echo "Setup finished. Edit .env and then run: source venv/bin/activate && python main.py"
