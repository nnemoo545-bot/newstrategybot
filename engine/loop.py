# Copilot prompt:
# "Implement engine loop: every POLL_INTERVAL_SECONDS read Binance open positions, read ACTIVE blocks from DB, call block_manager to evaluate and close blocks if needed. Send Telegram notifications on errors."
import asyncio
import logging
from ..config import settings
from ..exchange.binance_client import BinanceClient
from ..engine.block_manager import evaluate_blocks
from ..database.db import get_session
from sqlalchemy.future import select
from ..database.models import Block, BlockStatus

logger = logging.getLogger("engine.loop")

async def engine_loop():
    bc = BinanceClient(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET, settings.BINANCE_TESTNET)
    poll = int(settings.POLL_INTERVAL_SECONDS)
    while True:
        try:
            # fetch positions from Binance
            positions = bc.get_open_positions()
            # load active blocks from DB (async SQLAlchemy)
            async with get_session() as session:
                result = await session.execute(select(Block).where(Block.status == BlockStatus.ACTIVE))
                active_blocks = result.scalars().all()
            # evaluate each block
            await evaluate_blocks(active_blocks, positions, bc)
        except Exception as e:
            logger.exception("Engine loop error: %s", e)
            # TODO: send Telegram alert via telegram_client
        await asyncio.sleep(poll)
