"""
智能体控制器模块
实现智能体的创建、管理和控制
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from agents.base import AgentState, BaseAgent, SimpleChatAgent
from agents.codeact import CodeActAgent, CodeActAgentConfig, CodeActAgentFactory
from models.agent import Agent, AgentStatus, AgentType
from services.db_service import DatabaseService

logger = logging.getLogger(__name__)


class AgentController:
    """
    智能体控制器
    负责智能体的创建、管理和控制
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化控制器"""
        if AgentController._initialized:
            return
        AgentController._initialized = True

        self._agents: Dict[int, BaseAgent] = {}
        self._agent_lock: asyncio.Lock = asyncio.Lock()
        self._task_lock: asyncio.Lock = asyncio.Lock()
        self._running_tasks: Dict[int, asyncio.Task] = {}

    async def initialize(self) -> None:
        """
        初始化控制器
        从数据库加载已有的智能体
        """
        logger.info("正在初始化智能体控制器...")

        async with self._agent_lock:
            # 从数据库加载智能体
            agents = await DatabaseService.get_all_agents()

            for agent in agents:
                if agent.status == AgentStatus.ACTIVE:
                    await self._create_agent_instance(agent)

            logger.info(f"成功初始化 {len(self._agents)} 个智能体")

    async def _create_agent_instance(self, db_agent: Agent) -> Optional[BaseAgent]:
        """
        创建智能体实例

        Args:
            db_agent: 数据库中的智能体记录

        Returns:
            Optional[BaseAgent]: 创建的智能体实例
        """
        try:
            if db_agent.type == AgentType.CODEACT:
                agent = CodeActAgentFactory.create_agent_from_db_model(db_agent)
            else:
                agent = SimpleChatAgent(
                    agent_id=db_agent.id,
                    name=db_agent.name,
                    type=db_agent.type,
                    description=db_agent.description,
                )

            self._agents[db_agent.id] = agent
            logger.debug(f"已创建智能体实例: {agent.state_dict}")
            return agent
        except Exception as e:
            logger.error(f"创建智能体实例失败: {e}")
            return None

    async def create_agent(
        self,
        name: str,
        type: AgentType = AgentType.CHAT,
        description: str = None,
        config: Dict[str, Any] = None,
    ) -> Optional[BaseAgent]:
        """
        创建新智能体

        Args:
            name: 智能体名称
            type: 智能体类型
            description: 智能体描述
            config: 智能体配置

        Returns:
            Optional[BaseAgent]: 新创建的智能体实例
        """
        async with self._agent_lock:
            try:
                # 在数据库中创建智能体
                db_agent = await DatabaseService.create_agent(
                    name=name,
                    type=type,
                    description=description,
                    config=config,
                    status=AgentStatus.ACTIVE,
                )

                # 创建智能体实例
                agent = await self._create_agent_instance(db_agent)

                logger.info(f"成功创建智能体: {agent.state_dict}")
                return agent
            except Exception as e:
                logger.error(f"创建智能体失败: {e}")
                return None

    async def get_agent(self, agent_id: int) -> Optional[BaseAgent]:
        """
        获取智能体实例

        Args:
            agent_id: 智能体 ID

        Returns:
            Optional[BaseAgent]: 智能体实例
        """
        async with self._agent_lock:
            return self._agents.get(agent_id)

    async def get_all_agents(self) -> List[BaseAgent]:
        """
        获取所有智能体实例

        Returns:
            List[BaseAgent]: 智能体实例列表
        """
        async with self._agent_lock:
            return list(self._agents.values())

    async def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """
        按名称获取智能体实例

        Args:
            name: 智能体名称

        Returns:
            Optional[BaseAgent]: 智能体实例
        """
        async with self._agent_lock:
            for agent in self._agents.values():
                if agent.name == name:
                    return agent
            return None

    async def run_agent(
        self,
        agent_id: int,
        input_data: Any,
        background: bool = False,
    ) -> Optional[Any]:
        """
        运行智能体

        Args:
            agent_id: 智能体 ID
            input_data: 输入数据
            background: 是否在后台运行

        Returns:
            Optional[Any]: 智能体响应
        """
        agent = await self.get_agent(agent_id)

        if not agent:
            logger.error(f"智能体未找到: {agent_id}")
            return None

        if not agent.is_active:
            logger.error(f"智能体不可用: {agent_id} (状态: {agent.state})")
            return None

        if background:
            task = asyncio.create_task(self._run_agent_task(agent, input_data))
            self._running_tasks[agent_id] = task
            logger.debug(f"智能体任务已在后台运行: {agent_id}")
            return None
        else:
            return await self._run_agent_task(agent, input_data)

    async def _run_agent_task(self, agent: BaseAgent, input_data: Any) -> Any:
        """
        内部方法：运行智能体任务

        Args:
            agent: 智能体实例
            input_data: 输入数据

        Returns:
            Any: 智能体响应
        """
        async with self._task_lock:
            try:
                logger.debug(f"开始运行智能体: {agent.agent_id}")
                result = await agent.run(input_data)
                logger.debug(f"智能体运行完成: {agent.agent_id}")
                return result
            except Exception as e:
                logger.error(f"运行智能体失败: {e}")
                return None
            finally:
                if agent.agent_id in self._running_tasks:
                    del self._running_tasks[agent.agent_id]

    async def stop_agent(self, agent_id: int) -> bool:
        """
        停止正在运行的智能体

        Args:
            agent_id: 智能体 ID

        Returns:
            bool: 是否成功停止
        """
        async with self._agent_lock:
            if agent_id in self._running_tasks:
                try:
                    task = self._running_tasks[agent_id]
                    task.cancel()

                    try:
                        await task
                    except asyncio.CancelledError:
                        logger.debug(f"智能体任务已取消: {agent_id}")

                    del self._running_tasks[agent_id]
                    return True
                except Exception as e:
                    logger.error(f"停止智能体失败: {e}")
                    return False

            agent = self._agents.get(agent_id)
            if agent:
                await agent.set_state(AgentState.IDLE)
                return True

            return False

    async def destroy_agent(self, agent_id: int) -> bool:
        """
        销毁智能体

        Args:
            agent_id: 智能体 ID

        Returns:
            bool: 是否成功销毁
        """
        async with self._agent_lock:
            try:
                # 停止正在运行的任务
                await self.stop_agent(agent_id)

                # 从控制器中移除
                agent = self._agents.pop(agent_id, None)

                if agent:
                    await agent.destroy()
                    logger.debug(f"智能体实例已销毁: {agent_id}")

                # 更新数据库状态
                await DatabaseService.update_agent(
                    agent_id, status=AgentStatus.INACTIVE
                )

                logger.info(f"智能体已成功销毁: {agent_id}")
                return True
            except Exception as e:
                logger.error(f"销毁智能体失败: {e}")
                return False

    async def destroy_all_agents(self) -> None:
        """
        销毁所有智能体
        """
        async with self._agent_lock:
            for agent_id in list(self._agents.keys()):
                await self.destroy_agent(agent_id)
        logger.info("所有智能体已销毁")

    async def update_agent(
        self, agent_id: int, **kwargs
    ) -> bool:
        """
        更新智能体信息

        Args:
            agent_id: 智能体 ID
            **kwargs: 要更新的字段

        Returns:
            bool: 是否成功更新
        """
        async with self._agent_lock:
            try:
                # 更新数据库中的智能体信息
                await DatabaseService.update_agent(agent_id, **kwargs)

                # 更新内存中的智能体信息
                agent = self._agents.get(agent_id)
                if agent:
                    for key, value in kwargs.items():
                        if hasattr(agent, key):
                            setattr(agent, key, value)
                    logger.debug(f"智能体信息已更新: {agent_id}")

                logger.info(f"智能体信息已更新: {agent_id}")
                return True
            except Exception as e:
                logger.error(f"更新智能体信息失败: {e}")
                return False

    async def update_agent_config(
        self, agent_id: int, config: Dict[str, Any]
    ) -> bool:
        """
        更新智能体配置

        Args:
            agent_id: 智能体 ID
            config: 新配置

        Returns:
            bool: 是否成功更新
        """
        async with self._agent_lock:
            try:
                # 更新数据库配置
                await DatabaseService.update_agent(agent_id, config=config)

                # 更新内存中的智能体配置
                agent = self._agents.get(agent_id)
                if agent:
                    if hasattr(agent, "config") and hasattr(agent.config, "update"):
                        agent.config = agent.config.copy(update=config)
                    logger.debug(f"智能体配置已更新: {agent_id}")

                logger.info(f"智能体配置已更新: {agent_id}")
                return True
            except Exception as e:
                logger.error(f"更新智能体配置失败: {e}")
                return False

    async def get_agent_status(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """
        获取智能体状态

        Args:
            agent_id: 智能体 ID

        Returns:
            Optional[Dict[str, Any]]: 智能体状态信息
        """
        agent = await self.get_agent(agent_id)

        if agent:
            status = agent.state_dict
            status["task_running"] = agent_id in self._running_tasks
            return status
        else:
            logger.warning(f"获取智能体状态时未找到智能体: {agent_id}")
            return None

    async def get_running_agents(self) -> List[Dict[str, Any]]:
        """
        获取正在运行的智能体列表

        Returns:
            List[Dict[str, Any]]: 运行中的智能体状态信息
        """
        async with self._agent_lock:
            running = []
            for agent in self._agents.values():
                status = agent.state_dict
                status["task_running"] = agent.agent_id in self._running_tasks
                if status["task_running"]:
                    running.append(status)
            return running

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            Dict[str, Any]: 健康检查结果
        """
        async with self._agent_lock:
            total_agents = len(self._agents)
            active_agents = len([a for a in self._agents.values() if a.is_active])
            running_tasks = len(self._running_tasks)

            return {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "running_tasks": running_tasks,
                "status": "healthy" if active_agents > 0 else "warning",
                "timestamp": asyncio.get_running_loop().time(),
            }


# 创建全局控制器实例
_controller = None


async def get_agent_controller() -> AgentController:
    """
    获取全局控制器实例

    Returns:
        AgentController: 控制器实例
    """
    global _controller

    if _controller is None:
        _controller = AgentController()
        await _controller.initialize()

    return _controller
