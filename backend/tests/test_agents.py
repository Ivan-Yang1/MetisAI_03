"""
智能体系统测试模块
用于测试智能体的创建、销毁和运行
"""

import asyncio
import logging
import sys
import unittest
from typing import Any, Dict, List

sys.path.append("E:/Project/MetisAI/MetisAI_03")

from backend.agents.base import AgentConfig, AgentInput, AgentOutput, SimpleChatAgent
from backend.agents.codeact import CodeActAgent, CodeActAgentConfig, CodeActAgentFactory
from backend.controllers.agent_controller import get_agent_controller
from backend.models.agent import AgentType
from backend.services.db_service import DatabaseService

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class TestAgentBase(unittest.IsolatedAsyncioTestCase):
    """测试智能体基类"""

    async def test_agent_base_instantiation(self):
        """测试智能体基类实例化"""
        logger.info("开始测试智能体基类实例化")

        agent = SimpleChatAgent(agent_id=1, name="Test Agent")

        self.assertEqual(agent.agent_id, 1)
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.type, AgentType.CHAT)

        logger.debug(f"智能体状态: {agent.state_dict}")

        logger.info("测试智能体基类实例化完成")

    async def test_agent_state_changes(self):
        """测试智能体状态变化"""
        logger.info("开始测试智能体状态变化")

        agent = SimpleChatAgent(agent_id=2, name="State Test Agent")
        initial_state = agent.state

        logger.debug(f"初始状态: {initial_state}")

        await agent.set_state(agent.state)
        self.assertEqual(agent.state, initial_state)

        await agent.set_state(agent.state)
        self.assertEqual(agent.state, initial_state)

        logger.debug(f"最终状态: {agent.state}")

        logger.info("测试智能体状态变化完成")


class TestCodeActAgent(unittest.IsolatedAsyncioTestCase):
    """测试 CodeAct 智能体"""

    async def test_codeact_agent_creation(self):
        """测试 CodeAct 智能体创建"""
        logger.info("开始测试 CodeAct 智能体创建")

        config = CodeActAgentConfig(
            model="claude-3-sonnet", temperature=0.5, max_tokens=2048
        )
        agent = CodeActAgent(agent_id=3, name="CodeAct Test Agent", config=config)

        self.assertEqual(agent.agent_id, 3)
        self.assertEqual(agent.name, "CodeAct Test Agent")
        self.assertEqual(agent.type, AgentType.CODEACT)
        self.assertEqual(agent.config.model, "claude-3-sonnet")

        logger.debug(f"智能体配置: {agent.config.dict()}")

        logger.info("测试 CodeAct 智能体创建完成")

    async def test_codeact_agent_factory(self):
        """测试 CodeAct 智能体工厂"""
        logger.info("开始测试 CodeAct 智能体工厂")

        db_agent = await DatabaseService.create_agent(
            name="Factory Agent",
            type=AgentType.CODEACT,
            description="Test agent from factory",
            config={"model": "gpt-4"},
        )

        agent = CodeActAgentFactory.create_agent_from_db_model(db_agent)

        self.assertEqual(agent.agent_id, db_agent.id)
        self.assertEqual(agent.name, db_agent.name)
        self.assertEqual(agent.type, AgentType.CODEACT)

        logger.debug(f"工厂创建的智能体: {agent.state_dict}")

        await DatabaseService.delete_agent(db_agent.id)

        logger.info("测试 CodeAct 智能体工厂完成")

    async def test_codeact_agent_run(self):
        """测试 CodeAct 智能体运行"""
        logger.info("开始测试 CodeAct 智能体运行")

        agent = CodeActAgent(agent_id=4, name="Run Test Agent")

        input_data = AgentInput(
            messages=[
                {
                    "role": "user",
                    "content": "请运行以下代码:\n```python\nprint('Hello, World!')\n```",
                }
            ]
        )

        result = await agent.run(input_data)

        self.assertIsNotNone(result)
        self.assertIn("Hello, World!", result.response)

        logger.debug(f"运行结果: {result}")

        logger.info("测试 CodeAct 智能体运行完成")


class TestAgentController(unittest.IsolatedAsyncioTestCase):
    """测试智能体控制器"""

    async def test_agent_controller_instantiation(self):
        """测试智能体控制器实例化"""
        logger.info("开始测试智能体控制器实例化")

        controller = await get_agent_controller()

        self.assertIsNotNone(controller)

        logger.debug("控制器实例化成功")

        logger.info("测试智能体控制器实例化完成")

    async def test_controller_create_agent(self):
        """测试控制器创建智能体"""
        logger.info("开始测试控制器创建智能体")

        controller = await get_agent_controller()

        agent = await controller.create_agent(
            name="Controller Test Agent",
            type=AgentType.CHAT,
            description="Test agent from controller",
        )

        self.assertIsNotNone(agent)
        self.assertIn(agent.agent_id, [a.agent_id for a in await controller.get_all_agents()])

        logger.debug(f"控制器创建的智能体: {agent.state_dict}")

        await controller.destroy_agent(agent.agent_id)

        logger.info("测试控制器创建智能体完成")

    async def test_controller_agent_lifecycle(self):
        """测试控制器智能体生命周期"""
        logger.info("开始测试控制器智能体生命周期")

        controller = await get_agent_controller()

        agent = await controller.create_agent(
            name="Lifecycle Test Agent", type=AgentType.CHAT
        )

        # 获取智能体
        retrieved_agent = await controller.get_agent(agent.agent_id)
        self.assertEqual(retrieved_agent.agent_id, agent.agent_id)

        # 运行智能体
        result = await controller.run_agent(agent.agent_id, "你好!")
        self.assertIsNotNone(result)

        # 停止智能体
        stopped = await controller.stop_agent(agent.agent_id)
        self.assertTrue(stopped)

        # 销毁智能体
        destroyed = await controller.destroy_agent(agent.agent_id)
        self.assertTrue(destroyed)

        # 验证智能体已被删除
        deleted_agent = await controller.get_agent(agent.agent_id)
        self.assertIsNone(deleted_agent)

        logger.info("测试控制器智能体生命周期完成")


class TestAgentIntegration(unittest.IsolatedAsyncioTestCase):
    """测试智能体集成功能"""

    async def test_agent_integration_with_db(self):
        """测试智能体与数据库集成"""
        logger.info("开始测试智能体与数据库集成")

        # 创建智能体
        db_agent = await DatabaseService.create_agent(
            name="DB Integration Agent",
            type=AgentType.CHAT,
            description="Test integration with database",
        )

        # 初始化控制器
        controller = await get_agent_controller()

        # 获取智能体实例
        agent = await controller.get_agent(db_agent.id)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, db_agent.name)

        logger.debug("智能体实例: %s", agent.state_dict)

        await DatabaseService.delete_agent(db_agent.id)
        logger.info("测试智能体与数据库集成完成")

    async def test_agent_health_check(self):
        """测试智能体健康检查"""
        logger.info("开始测试智能体健康检查")

        controller = await get_agent_controller()
        health_info = await controller.health_check()

        logger.debug(f"健康检查信息: {health_info}")

        self.assertGreater(health_info["total_agents"], 0)
        self.assertGreater(health_info["active_agents"], 0)

        logger.info("测试智能体健康检查完成")


if __name__ == "__main__":
    unittest.main()
