"""
智能体基类模块
定义所有智能体都应继承的抽象基类
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from backend.models.agent import Agent, AgentStatus, AgentType


class AgentState(str, Enum):
    """智能体状态枚举"""

    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    ERROR = "error"
    COMPLETED = "completed"


class AgentConfig(BaseModel):
    """智能体配置基类"""

    model: str = Field(default="claude-3-opus", description="使用的 LLM 模型名称")
    temperature: float = Field(default=0.7, description="温度参数", ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, description="最大令牌数", gt=0)
    timeout: float = Field(default=60.0, description="超时时间（秒）", gt=0)

    @validator("model")
    def valid_model(cls, v: str) -> str:
        """验证模型名称"""
        valid_models = [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "gpt-4",
            "gpt-3.5-turbo",
        ]
        if v.lower() not in valid_models:
            raise ValueError(f"不支持的模型: {v}")
        return v


class AgentInput(BaseModel):
    """智能体输入基类"""

    messages: List[Dict[str, Any]] = Field(default_factory=list, description="对话历史")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class AgentOutput(BaseModel):
    """智能体输出基类"""

    response: str = Field(..., description="智能体响应")
    state: AgentState = Field(default=AgentState.COMPLETED, description="智能体状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")


class BaseAgent(ABC):
    """
    智能体抽象基类
    所有智能体都应继承此类并实现抽象方法
    """

    def __init__(
        self,
        agent_id: int,
        name: str,
        type: AgentType = AgentType.CHAT,
        config: Optional[AgentConfig] = None,
    ):
        self.agent_id: int = agent_id
        self.name: str = name
        self.type: AgentType = type
        self.config: AgentConfig = config or AgentConfig()
        self.state: AgentState = AgentState.IDLE
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()
        self.history: List[AgentOutput] = []

    @property
    def is_active(self) -> bool:
        """判断智能体是否处于活动状态"""
        return self.state not in [AgentState.ERROR, AgentState.COMPLETED]

    @property
    def state_dict(self) -> Dict[str, Any]:
        """返回智能体的状态字典"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.type.value,
            "state": self.state.value,
            "config": self.config.dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "history_count": len(self.history),
        }

    @abstractmethod
    async def run(self, input_data: Union[AgentInput, str]) -> AgentOutput:
        """
        运行智能体
        必须由子类实现

        Args:
            input_data: 输入数据，类型为 AgentInput 或字符串

        Returns:
            AgentOutput: 智能体响应
        """
        pass

    async def set_state(self, state: AgentState) -> None:
        """
        设置智能体状态

        Args:
            state: 新状态
        """
        self.state = state
        self.updated_at = datetime.utcnow()

    def add_history(self, output: AgentOutput) -> None:
        """
        添加响应历史记录

        Args:
            output: 响应输出
        """
        self.history.append(output)
        self.updated_at = datetime.utcnow()

    async def destroy(self) -> None:
        """
        销毁智能体
        清理资源和状态
        """
        self.state = AgentState.COMPLETED
        self.updated_at = datetime.utcnow()


class SimpleChatAgent(BaseAgent):
    """
    简单聊天智能体实现
    用于演示和测试目的
    """

    async def run(self, input_data: Union[AgentInput, str]) -> AgentOutput:
        """
        运行聊天智能体

        Args:
            input_data: 输入数据

        Returns:
            AgentOutput: 响应
        """
        await self.set_state(AgentState.THINKING)
        await asyncio.sleep(0.5)

        # 处理输入
        if isinstance(input_data, str):
            user_input = input_data
        else:
            if input_data.messages:
                user_input = input_data.messages[-1]["content"]
            else:
                user_input = "你好！有什么我可以帮助你的吗？"

        # 生成简单响应
        await self.set_state(AgentState.EXECUTING)
        await asyncio.sleep(1.0)

        response = (
            f"我是 {self.name}，一个简单的聊天智能体。"
            f"你刚才说: '{user_input}'"
            f"我正在使用 {self.config.model} 模型。"
        )

        await self.set_state(AgentState.COMPLETED)
        output = AgentOutput(
            response=response,
            state=AgentState.COMPLETED,
            metadata={
                "model": self.config.model,
                "temperature": self.config.temperature,
            },
        )
        self.add_history(output)
        return output
