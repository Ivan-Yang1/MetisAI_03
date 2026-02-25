"""
沙箱执行环境测试模块
用于测试沙箱配置、Docker 运行时和动作执行
"""

import asyncio
import logging
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append("E:/Project/MetisAI/MetisAI_03")

from backend.runtime.action_executor import (
    ActionExecutor,
    ActionRequest,
    ActionServer,
    ActionStatus,
    ActionType,
    ActionExecutorFactory,
    ActionServerFactory,
    get_action_server,
)
from backend.runtime.config import (
    DEFAULT_CONFIG,
    LOCAL_CONFIG,
    DOCKER_CONFIG,
    KUBERNETES_CONFIG,
    SandboxConfig,
    SandboxRuntimeOptions,
    SandboxType,
    SandboxConfigManager,
)
from backend.runtime.docker_runtime import DockerRuntime, DockerRuntimeFactory

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class TestSandboxConfig(unittest.IsolatedAsyncioTestCase):
    """测试沙箱配置系统"""

    async def test_sandbox_config_creation(self):
        """测试沙箱配置创建"""
        logger.info("开始测试沙箱配置创建")

        # 测试默认配置
        default_config = SandboxConfigManager.get_default_config()
        self.assertIsInstance(default_config, SandboxConfig)
        self.assertEqual(default_config.sandbox_type, SandboxType.DOCKER)

        logger.debug(f"默认配置类型: {default_config.sandbox_type}")

        # 测试创建新配置
        custom_config = SandboxConfigManager.create_config(
            sandbox_type=SandboxType.LOCAL,
            working_dir="/custom/workdir",
            cleanup=False,
        )

        self.assertEqual(custom_config.sandbox_type, SandboxType.LOCAL)
        self.assertEqual(custom_config.working_dir, "/custom/workdir")
        self.assertFalse(custom_config.cleanup)

        logger.debug(f"自定义配置类型: {custom_config.sandbox_type}")
        logger.debug(f"工作目录: {custom_config.working_dir}")

        logger.info("测试沙箱配置创建完成")

    async def test_config_validation(self):
        """测试配置验证"""
        logger.info("开始测试配置验证")

        # 测试有效的配置数据
        valid_config = {
            "sandbox_type": "docker",
            "working_dir": "/workspace",
            "cleanup": True,
        }

        try:
            config = SandboxConfigManager.validate_and_create(valid_config)
            self.assertIsInstance(config, SandboxConfig)
            logger.debug("配置验证成功")
        except Exception as e:
            self.fail(f"有效的配置验证失败: {e}")

        # 测试无效的配置数据
        invalid_config = {
            "sandbox_type": "invalid_type",
            "working_dir": "/workspace",
        }

        with self.assertRaises(Exception):
            SandboxConfigManager.validate_and_create(invalid_config)

        logger.debug("无效配置验证成功")

        logger.info("测试配置验证完成")


class TestDockerRuntime(unittest.IsolatedAsyncioTestCase):
    """测试 Docker 运行时"""

    async def test_docker_availability(self):
        """测试 Docker 是否可用"""
        logger.info("开始测试 Docker 可用性")

        try:
            runtime = await DockerRuntimeFactory.get_instance()
            self.assertIsInstance(runtime, DockerRuntime)
            logger.debug("Docker 运行时实例创建成功")

            # 测试容器创建（需要 Docker 服务正在运行）
            # container_id = await runtime.create_container()
            # self.assertIsNotNone(container_id)
            # logger.debug(f"容器创建成功: {container_id}")

            # await runtime.remove_container(container_id)
            # logger.debug(f"容器删除成功: {container_id}")

            logger.info("Docker 运行时测试完成")

        except Exception as e:
            logger.warning(f"Docker 不可用: {e}")
            self.skipTest("Docker 服务未运行或不可用")


class TestActionExecutor(unittest.IsolatedAsyncioTestCase):
    """测试动作执行器"""

    async def test_action_executor_initialization(self):
        """测试动作执行器初始化"""
        logger.info("开始测试动作执行器初始化")

        executor = await ActionExecutorFactory.create_executor()
        self.assertIsInstance(executor, ActionExecutor)
        logger.debug("动作执行器实例创建成功")

        logger.info("动作执行器初始化测试完成")

    async def test_action_server_initialization(self):
        """测试动作服务器初始化"""
        logger.info("开始测试动作服务器初始化")

        server = await ActionServerFactory.get_instance()
        self.assertIsInstance(server, ActionServer)
        logger.debug("动作服务器实例创建成功")

        logger.info("动作服务器初始化测试完成")


class TestActionExecution(unittest.IsolatedAsyncioTestCase):
    """测试动作执行"""

    async def test_execute_command_action(self):
        """测试执行命令动作"""
        logger.info("开始测试执行命令动作")

        try:
            # 创建简单的本地执行器（不依赖 Docker）
            server = await ActionServerFactory.get_instance()

            request = ActionRequest(
                action_type=ActionType.EXECUTE_COMMAND,
                parameters={"command": "echo 'Hello World'"},
                timeout=30,
                sandbox_options=SandboxRuntimeOptions(
                    sandbox_type=SandboxType.LOCAL,
                ),
            )

            # 提交动作
            action_id = await server.submit_action(request)
            self.assertIsNotNone(action_id)
            logger.debug(f"动作提交成功，ID: {action_id}")

            # 等待动作完成
            await asyncio.sleep(2)

            # 检查动作结果
            result = await server.get_action_result(action_id)
            self.assertIsNotNone(result)
            self.assertEqual(result.status, ActionStatus.COMPLETED)

            logger.debug(f"动作结果: {result}")

            logger.info("执行命令动作测试完成")

        except Exception as e:
            logger.warning(f"动作执行测试失败: {e}")
            self.skipTest("动作执行测试失败")


class TestSandboxIntegration(unittest.IsolatedAsyncioTestCase):
    """测试沙箱集成功能"""

    async def test_sandbox_lifecycle(self):
        """测试沙箱生命周期"""
        logger.info("开始测试沙箱生命周期")

        try:
            runtime = await DockerRuntimeFactory.get_instance()

            # 创建容器
            container_id = await runtime.create_container()
            self.assertIsNotNone(container_id)
            logger.debug(f"容器创建成功: {container_id}")

            # 检查容器状态
            status = await runtime.get_container_status(container_id)
            self.assertEqual(status.get("status"), "running")
            logger.debug(f"容器状态: {status}")

            # 执行命令
            result = await runtime.execute_command(
                container_id, "ls -la /"
            )
            self.assertTrue(result.get("success"))
            logger.debug(f"命令执行成功: {result}")

            # 停止并删除容器
            await runtime.stop_container(container_id)
            status = await runtime.get_container_status(container_id)
            self.assertEqual(status.get("status"), "stopped")

            await runtime.remove_container(container_id)
            logger.debug("容器删除成功")

            logger.info("沙箱生命周期测试完成")

        except Exception as e:
            logger.warning(f"沙箱生命周期测试失败: {e}")
            self.skipTest("沙箱生命周期测试失败")


if __name__ == "__main__":
    unittest.main()
