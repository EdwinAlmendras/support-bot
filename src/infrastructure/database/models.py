from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class SeenLink(Base):
    __tablename__ = "seen_links"

    hash = Column(String, primary_key=True)
    url = Column(String)
    chat_id = Column(BigInteger, primary_key=True)
    first_seen = Column(DateTime, default=datetime.utcnow)

class ManagedGroup(Base):
    __tablename__ = "managed_groups"
    
    chat_id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

class SeenMessage(Base):
    __tablename__ = "seen_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    message_hash = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())

class BotSetting(Base):
    __tablename__ = "bot_settings"
    
    chat_id = Column(Integer, primary_key=True)
    key = Column(String, primary_key=True)
    value = Column(String) # Stored as string, converted in service (e.g., "true"/"false")
    description = Column(String, nullable=True)

class ChatState(Base):
    __tablename__ = "chat_states"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    key = Column(String, index=True) # e.g., "last_welcome_id"
    value = Column(String) # e.g., "1234"

class BroadcastQueue(Base):
    __tablename__ = "broadcast_queue"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, index=True) # Per-group queue
    link = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
    sent = Column(Integer, default=0) # 0 = pending, 1 = sent

class BroadcastSettings(Base):
    __tablename__ = "broadcast_settings"
    
    key = Column(String, primary_key=True) # "interval", "active"
    value = Column(String)



