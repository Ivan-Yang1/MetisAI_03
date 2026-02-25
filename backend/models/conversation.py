"""
会话模型
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.models.base import Base
from backend.models.agent import Agent


class ConversationStatus(str, Enum):
    """会话状态枚举"""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELED = "canceled"
    ERROR = "error"


class Conversation(Base):
    """
    会话模型
    表示用户与智能体之间的一次对话
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    title = Column(String(200), nullable=True)
    status = Column(
        SQLAlchemyEnum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE
    )
    metadata_ = Column("metadata", JSON, nullable=True)  # 会话元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 关联关系
    agent = relationship("Agent", backref="conversations")
    messages = relationship("Message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id='{self.user_id}', title='{self.title}')>"
