# Copilot prompt:
# "Small wrapper to send Telegram messages using python-telegram-bot Application or Bot. Provide send_message(chat_id, text)."
from telegram import Bot
from ..config import settings

_bot = Bot(token=settings.TELEGRAM_TOKEN)

def send_message(chat_id: int, text: str):
    return _bot.send_message(chat_id=chat_id, text=text)
