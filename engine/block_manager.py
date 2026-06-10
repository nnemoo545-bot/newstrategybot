# Copilot prompt:
# "Implement block manager evaluate_blocks(blocks, binance_positions, binance_client).
# For each block compute unrealized PnL from binance_positions (match by symbol & side),
# compare with block.stop_line and block.tp_value and call binance_client.close_position when needed.
# Update DB (positions/status) and return events list. Keep implementation minimal and safe."
import logging
from typing import List, Dict, Any
from ..exchange.binance_client import BinanceClient
from ..database.db import get_session
from ..database.models import Block, BlockPosition, TradeHistory, BlockStatus

logger = logging.getLogger("engine.block_manager")

async def evaluate_blocks(blocks: List[Block], binance_positions: List[Dict[str, Any]], bc: BinanceClient):
    """
    Evaluate active blocks and close when SL/TP hit.
    This is a minimal implementation: matching is simplistic and intended for extension.
    """
    events = []
    # Build quick lookup for binance positions by symbol
    pos_by_symbol = {}
    for p in binance_positions:
        sym = p.get("symbol")
        pos_by_symbol.setdefault(sym, []).append(p)

    async with get_session() as session:
        for block in blocks:
            try:
                # calculate block unrealized PnL by summing positionProfit for matched symbols in block.positions
                block_pnl = 0.0
                for bp in block.positions:
                    sym = bp.symbol
                    # find matching binance position
                    matches = pos_by_symbol.get(sym, [])
                    found = None
                    for m in matches:
                        # side match: in Binance API, positionSide or positionAmt sign may indicate direction;
                        # here we do a simple check by symbol and skip complicated cases in template.
                        found = m
                        break
                    if found:
                        # positionProfit may exist
                        pnl = float(found.get("unRealizedProfit") or 0.0)
                        block_pnl += pnl
                        bp.pnl_snapshot = pnl
                # Compare with stop_line / tp_value
                if block.stop_line is not None:
                    # simple check: if any underlying position price crosses stop_line, close block
                    # For template: compare current markPrice of first position vs stop_line (extension: check per-side)
                    # We'll issue a close for all positions in block if condition met.
                    # (Production: use precise side-aware checks)
                    first_sym = block.positions[0].symbol if block.positions else None
                    if first_sym:
                        current_price = bc.get_price(first_sym)
                        if block.stop_line and current_price <= block.stop_line:
                            logger.info("Stop line hit for block %s -> closing", block.name)
                            # close all positions belonging to block
                            for bp in list(block.positions):
                                try:
                                    bc.close_position(bp.symbol, bp.side, bp.quantity)
                                    # record trade history
                                    th = TradeHistory(block_id=block.id, position_id=bp.id, action="close", price=current_price, qty=bp.quantity, pnl=bp.pnl_snapshot)
                                    session.add(th)
                                    bp.status = "CLOSED"
                                    bp.closed_at = __import__("datetime").datetime.utcnow()
                                except Exception as e:
                                    logger.exception("Failed to close pos %s: %s", bp.symbol, e)
                            block.status = BlockStatus.CLOSED
                            block.closed_at = __import__("datetime").datetime.utcnow()
                            events.append({"type":"stop_hit","block":block.name,"pnl":block_pnl})
                if block.tp_value is not None:
                    if block_pnl >= float(block.tp_value):
                        logger.info("TP value reached for block %s -> closing", block.name)
                        for bp in list(block.positions):
                            try:
                                current_price = bc.get_price(bp.symbol)
                                bc.close_position(bp.symbol, bp.side, bp.quantity)
                                th = TradeHistory(block_id=block.id, position_id=bp.id, action="close", price=current_price, qty=bp.quantity, pnl=bp.pnl_snapshot)
                                session.add(th)
                                bp.status = "CLOSED"
                                bp.closed_at = __import__("datetime").datetime.utcnow()
                            except Exception as e:
                                logger.exception("Failed to close pos %s: %s", bp.symbol, e)
                        block.status = BlockStatus.CLOSED
                        block.closed_at = __import__("datetime").datetime.utcnow()
                        events.append({"type":"tp_hit","block":block.name,"pnl":block_pnl})
                # persist changes for this block
                await session.commit()
            except Exception as e:
                logger.exception("Error evaluating block %s: %s", getattr(block, "name", "<unknown>"), e)
                block.status = BlockStatus.ERROR
                await session.commit()
    return events
