# Copilot prompt:
# "Implement Telegram command handlers for /start, /close, /sl, /tp, /status, with minimal DB operations: create block, set stop_line, set tp_value, close block (mark closed). Validate user id against OWNER_TELEGRAM_ID."
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ..config import settings
from ..database.db import get_session
from ..database.models import Block, BlockPosition, BlockStatus

logger = logging.getLogger("bot.handlers")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Укажи имя блока: /start A")
        return
    name = args[0].upper()
    async with get_session() as session:
        # check existing
        from sqlalchemy.future import select
        res = await session.execute(select(Block).where(Block.name == name))
        existing = res.scalars().first()
        if existing and existing.status == BlockStatus.ACTIVE:
            await update.message.reply_text(f"Block {name} already ACTIVE")
            return
        if existing:
            existing.status = BlockStatus.ACTIVE
            existing.owner = user_id
            await session.commit()
            await update.message.reply_text(f"Block {name} re-activated")
            return
        b = Block(name=name, owner=user_id, status=BlockStatus.ACTIVE)
        session.add(b)
        await session.commit()
    await update.message.reply_text(f"Block {name} created and set ACTIVE")

async def sl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /sl A 104000")
        return
    name = args[0].upper()
    try:
        sl_value = float(args[1])
    except:
        await update.message.reply_text("SL must be a number")
        return
    async with get_session() as session:
        from sqlalchemy.future import select
        res = await session.execute(select(Block).where(Block.name == name))
        b = res.scalars().first()
        if not b:
            await update.message.reply_text(f"Block {name} not found")
            return
        b.stop_line = sl_value
        await session.commit()
    await update.message.reply_text(f"Stop Line for {name} set to {sl_value}")

async def tp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /tp A 107000")
        return
    name = args[0].upper()
    try:
        tp_value = float(args[1])
    except:
        await update.message.reply_text("TP must be a number")
        return
    async with get_session() as session:
        from sqlalchemy.future import select
        res = await session.execute(select(Block).where(Block.name == name))
        b = res.scalars().first()
        if not b:
            await update.message.reply_text(f"Block {name} not found")
            return
        b.tp_value = tp_value
        await session.commit()
    await update.message.reply_text(f"TP for {name} set to {tp_value}")

async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /close A")
        return
    name = args[0].upper()
    async with get_session() as session:
        from sqlalchemy.future import select
        res = await session.execute(select(Block).where(Block.name == name))
        b = res.scalars().first()
        if not b:
            await update.message.reply_text(f"Block {name} not found")
            return
        # mark block CLOSED — engine will handle actual close via Binance wrapper
        b.status = BlockStatus.CLOSED
        b.closed_at = __import__("datetime").datetime.utcnow()
        await session.commit()
    await update.message.reply_text(f"Block {name} marked CLOSED. Engine will attempt to close positions.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Only owner can request status in template
    if user_id != settings.OWNER_TELEGRAM_ID:
        await update.message.reply_text("Unauthorized")
        return
    args = context.args
    async with get_session() as session:
        from sqlalchemy.future import select
        if args:
            name = args[0].upper()
            res = await session.execute(select(Block).where(Block.name == name))
            b = res.scalars().first()
            if not b:
                await update.message.reply_text(f"Block {name} not found")
                return
            text = f"Block {b.name}\nStatus: {b.status}\nPositions: {len(b.positions)}\nStopLine: {b.stop_line}\nTP: {b.tp_value}"
            await update.message.reply_text(text)
            return
        res = await session.execute(select(Block))
        blocks = res.scalars().all()
        text_lines = []
        for b in blocks:
            text_lines.append(f"{b.name}: {b.status} | pos={len(b.positions)} | PNL~{getattr(b, 'pnl_snapshot', 0)}")
        await update.message.reply_text("\n".join(text_lines) if text_lines else "No blocks")

def build_app():
    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("sl", sl_command))
    app.add_handler(CommandHandler("tp", tp_command))
    app.add_handler(CommandHandler("close", close_command))
    app.add_handler(CommandHandler("status", status_command))
    return app
