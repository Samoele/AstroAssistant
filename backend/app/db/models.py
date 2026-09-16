from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from app.db.session import Base

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default="user_default", index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    emotion = Column(String(30), nullable=True)  # stored for avatar recall
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default="user_default", index=True)
    category = Column(String(50), nullable=False)  # "workout", "nutrition", "sleep", "water"
    value = Column(Float, nullable=True)           # 3.0 (miles), 8.0 (hours), 2500 (calories)
    unit = Column(String(30), nullable=True)       # "miles", "hours", "glasses", "grams"
    notes = Column(Text, nullable=True)            # raw extraction details
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))