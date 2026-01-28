from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class SeenLink(Base):
    __tablename__ = "seen_links"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    link_hash = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())

class SeenMessage(Base):
    __tablename__ = "seen_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    message_hash = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())

class BotSetting(Base):
    __tablename__ = "bot_settings"
    
    key = Column(String, primary_key=True)
    value = Column(String) # Stored as string, converted in service (e.g., "true"/"false")
    description = Column(String, nullable=True)

class ChatState(Base):
    __tablename__ = "chat_states"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, index=True)
    key = Column(String, index=True) # e.g., "last_welcome_id"
    value = Column(String) # e.g., "1234"


