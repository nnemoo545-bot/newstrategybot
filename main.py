# Copilot prompt:
# "Run Telegram bot and engine loop concurrently. Use python-telegram-bot ApplicationBuilder for polling and asyncio for engine loop."
import asyncio
import logging

from bot.handlers import build_app
from engine.loop import engine_loop

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

def main():
    app = build_app()
    loop = asyncio.get_event_loop()
    loop.create_task(engine_loop())
    # run telegram bot polling (blocking)
    app.run_polling()

if __name__ == "__main__":
    main()
