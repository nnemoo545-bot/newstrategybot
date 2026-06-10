# Copilot prompt:
# "Create SQLAlchemy ORM declarative models for Block and BlockPosition plus enums and simple trades/history table."
import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class BlockStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    ERROR = "ERROR"

class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    owner = Column(Integer, nullable=True)  # telegram user id
    status = Column(Enum(BlockStatus), default=BlockStatus.ACTIVE, nullable=False)
    stop_line = Column(Float, nullable=True)
    tp_value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    positions = relationship("BlockPosition", back_populates="block", cascade="all, delete-orphan")

class BlockPosition(Base):
    __tablename__ = "block_positions"
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"))
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY/SELL
    entry_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    leverage = Column(Integer, default=1)
    binance_order_id = Column(String, nullable=True)
    status = Column(String, default="OPEN")
    opened_at = Column(DateTime, default=datetime.datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    pnl_snapshot = Column(Float, nullable=True)
    block = relationship("Block", back_populates="positions")

class TradeHistory(Base):
    __tablename__ = "trades_history"
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, nullable=True)
    position_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)  # open/close
    price = Column(Float, nullable=True)
    qty = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    note = Column(Text, nullable=True)
