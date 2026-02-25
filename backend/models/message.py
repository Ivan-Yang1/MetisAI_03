"""
消息模型
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from models.base import Base
from models.conversation import Conversation


class MessageRole(str, Enum):
    """消息角色枚举"""

    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message(Base):
    """
    消息模型
    表示会话中的一条消息
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(SQLAlchemyEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)  # 消息元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    conversation = relationship("Conversation")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role='{self.role}')>"
