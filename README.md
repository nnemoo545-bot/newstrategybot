# Trading Bot — Project Template

Этот репозиторий — шаблон для системы управления ручной торговлей через Telegram + VPS + Binance Futures.

Ключевые идеи:
- Ты остаёшься трейдером: система управляет открытыми позициями по твоим правилам (блоки, SL, TP, PnL).
- Telegram — только пульт управления (команды) + канал уведомлений.
- Engine на VPS — проверяет Binance, считает PnL, закрывает блоки по правилам.

Структура и инструкции по развёртыванию — см. файлы в корне.

Quickstart (dev / testnet)
1. Клонируй репо.
2. Создай .env на основе .env.example с тестовыми ключами Binance (testnet) и Telegram token.
3. Установи зависимости: `pip install -r requirements.txt`.
4. Запусти: `python main.py` (локально: бот + engine).
5. Разворачивай на VPS через Docker или systemd (см. deploy/trading_bot.service).

Безопасность
- Никогда не хранить реальные API‑ключи в репо.
- Для продакшена используйте Docker secrets, Vault или environment variables.

Дальше: можешь попросить меня сгенерировать реализацию функций (binance wrapper, блок‑менеджер) или залить это в GitHub репо.
