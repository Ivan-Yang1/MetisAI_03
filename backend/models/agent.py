"""
智能体模型
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Enum as SQLAlchemyEnum, Integer, String

from backend.models.base import Base


class AgentType(str, Enum):
    """智能体类型枚举"""

    CODEACT = "codeact"
    CHAT = "chat"
    TOOL = "tool"


class AgentStatus(str, Enum):
    """智能体状态枚举"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class Agent(Base):
    """
    智能体模型
    表示一个可以执行任务的 AI 智能体
    """

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLAlchemyEnum(AgentType), nullable=False, default=AgentType.CODEACT)
    description = Column(String(500), nullable=True)
    config = Column(JSON, nullable=True)  # 智能体配置（JSON 格式）
    status = Column(
        SQLAlchemyEnum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"
