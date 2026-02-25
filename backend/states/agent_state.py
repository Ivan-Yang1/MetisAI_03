"""
智能体状态管理系统模块
实现智能体状态的存储和管理
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import redis
from pydantic import BaseModel, Field

from backend.agents.base import AgentState, BaseAgent
from backend.controllers.agent_controller import get_agent_controller
from models.agent import Agent, AgentStatus, AgentType
from backend.services.db_service import DatabaseService

logger = logging.getLogger(__name__)


class StateType(str, Enum):
    """状态类型枚举"""

    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"


class AgentStateData(BaseModel):
    """智能体状态数据模型"""

    agent_id: int = Field(..., description="智能体 ID")
    name: str = Field(..., description="智能体名称")
    type: AgentType = Field(..., description="智能体类型")
    state: AgentState = Field(..., description="智能体状态")
    config: Dict[str, Any] = Field(default_factory=dict, description="智能体配置")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="历史记录")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class AgentStateManager:
    """
    智能体状态管理器
    负责智能体状态的存储、加载和管理
    """

    def __init__(self, state_type: StateType = StateType.MEMORY):
        """
        初始化状态管理器

        Args:
            state_type: 状态存储类型
        """
        self._state_type: StateType = state_type
        self._memory_states: Dict[int, AgentStateData] = {}
        self._redis_client: Optional[redis.Redis] = None

        if state_type == StateType.REDIS:
            self._init_redis()

    def _init_redis(self) -> None:
        """
        初始化 Redis 客户端
        """
        try:
            self._redis_client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True
            )

            # 测试连接
            self._redis_client.ping()
            logger.info("Redis 连接成功")

        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            self._state_type = StateType.MEMORY
            logger.warning("已降级为内存存储")

    async def save_state(self, agent: BaseAgent) -> bool:
        """
        保存智能体状态

        Args:
            agent: 智能体实例

        Returns:
            bool: 是否成功保存
        """
        try:
            state_data = AgentStateData(
                agent_id=agent.agent_id,
                name=agent.name,
                type=agent.type,
                state=agent.state,
                config=agent.config.dict(),
                created_at=agent.created_at,
                updated_at=agent.updated_at,
                history=[h.dict() for h in agent.history],
            )

            if self._state_type == StateType.MEMORY:
                self._memory_states[agent.agent_id] = state_data

            elif self._state_type == StateType.DISK:
                await self._save_to_disk(agent.agent_id, state_data)

            elif self._state_type == StateType.REDIS:
                await self._save_to_redis(agent.agent_id, state_data)

            logger.debug(f"智能体状态已保存: {agent.agent_id}")
            return True

        except Exception as e:
            logger.error(f"保存智能体状态失败: {e}")
            return False

    async def load_state(self, agent_id: int) -> Optional[AgentStateData]:
        """
        加载智能体状态

        Args:
            agent_id: 智能体 ID

        Returns:
            Optional[AgentStateData]: 状态数据
        """
        try:
            if self._state_type == StateType.MEMORY:
                return self._memory_states.get(agent_id)

            elif self._state_type == StateType.DISK:
                return await self._load_from_disk(agent_id)

            elif self._state_type == StateType.REDIS:
                return await self._load_from_redis(agent_id)

            return None
        except Exception as e:
            logger.error(f"加载智能体状态失败: {e}")
            return None

    async def _save_to_disk(self, agent_id: int, state_data: AgentStateData) -> None:
        """
        保存到磁盘

        Args:
            agent_id: 智能体 ID
            state_data: 状态数据
        """
        filename = f"agent_state_{agent_id}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state_data.dict(), f, default=str, indent=4)

    async def _load_from_disk(self, agent_id: int) -> Optional[AgentStateData]:
        """
        从磁盘加载

        Args:
            agent_id: 智能体 ID

        Returns:
            Optional[AgentStateData]: 状态数据
        """
        filename = f"agent_state_{agent_id}.json"

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 转换日期字符串为 datetime 对象
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

            return AgentStateData(**data)
        except FileNotFoundError:
            logger.debug(f"智能体状态文件未找到: {agent_id}")
            return None
        except Exception as e:
            logger.error(f"从磁盘加载智能体状态失败: {e}")
            return None

    async def _save_to_redis(self, agent_id: int, state_data: AgentStateData) -> None:
        """
        保存到 Redis

        Args:
            agent_id: 智能体 ID
            state_data: 状态数据
        """
        key = f"agent:{agent_id}"
        value = state_data.json()
        self._redis_client.set(key, value)
        self._redis_client.expire(key, 60 * 60 * 24)

    async def _load_from_redis(self, agent_id: int) -> Optional[AgentStateData]:
        """
        从 Redis 加载

        Args:
            agent_id: 智能体 ID

        Returns:
            Optional[AgentStateData]: 状态数据
        """
        key = f"agent:{agent_id}"
        value = self._redis_client.get(key)

        if value:
            return AgentStateData.parse_raw(value)
        else:
            return None

    async def delete_state(self, agent_id: int) -> bool:
        """
        删除智能体状态

        Args:
            agent_id: 智能体 ID

        Returns:
            bool: 是否成功删除
        """
        try:
            if self._state_type == StateType.MEMORY:
                if agent_id in self._memory_states:
                    del self._memory_states[agent_id]

            elif self._state_type == StateType.DISK:
                import os

                filename = f"agent_state_{agent_id}.json"
                if os.path.exists(filename):
                    os.remove(filename)

            elif self._state_type == StateType.REDIS:
                self._redis_client.delete(f"agent:{agent_id}")

            logger.debug(f"智能体状态已删除: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"删除智能体状态失败: {e}")
            return False

    async def get_all_states(self) -> List[AgentStateData]:
        """
        获取所有智能体状态

        Returns:
            List[AgentStateData]: 智能体状态列表
        """
        states = []

        if self._state_type == StateType.MEMORY:
            states = list(self._memory_states.values())
        elif self._state_type == StateType.DISK:
            # 实现从磁盘加载所有状态
            pass
        elif self._state_type == StateType.REDIS:
            # 实现从 Redis 加载所有状态
            pass

        return states

    async def sync_with_db(self) -> int:
        """
        与数据库同步

        Returns:
            int: 同步的状态数量
        """
        try:
            agents = await DatabaseService.get_all_agents()
            count = 0

            for agent in agents:
                if agent.status == AgentStatus.ACTIVE:
                    state_data = await self.load_state(agent.id)

                    if state_data:
                        # 更新状态
                        state_data.name = agent.name
                        state_data.type = agent.type
                        state_data.updated_at = datetime.utcnow()

                        await self.save_state(state_data)
                        count += 1

            logger.debug(f"已同步 {count} 个智能体状态")
            return count
        except Exception as e:
            logger.error(f"与数据库同步失败: {e}")
            return 0


class AgentStateManagerFactory:
    """
    智能体状态管理器工厂类
    用于创建不同类型的状态管理器实例
    """

    @staticmethod
    def create_manager(
        state_type: StateType = StateType.MEMORY
    ) -> AgentStateManager:
        """
        创建状态管理器实例

        Args:
            state_type: 状态存储类型

        Returns:
            AgentStateManager: 状态管理器实例
        """
        return AgentStateManager(state_type)


# 默认状态管理器
_default_manager: Optional[AgentStateManager] = None


async def get_state_manager() -> AgentStateManager:
    """
    获取默认状态管理器实例

    Returns:
        AgentStateManager: 状态管理器实例
    """
    global _default_manager

    if _default_manager is None:
        _default_manager = AgentStateManagerFactory.create_manager()

    return _default_manager


async def sync_states_with_db():
    """
    定期同步状态与数据库
    """
    while True:
        try:
            await asyncio.sleep(300)  # 每 5 分钟同步一次
            manager = await get_state_manager()
            await manager.sync_with_db()
        except Exception as e:
            logger.error(f"状态同步失败: {e}")
            continue


if __name__ == "__main__":
    # 简单测试
    import sys

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    asyncio.run(sync_states_with_db())
