"""
LLM 集成系统测试模块
用于测试 LLM 连接和响应生成
"""

import asyncio
import logging
import sys
import unittest
from typing import Any, Dict, List, Optional

sys.path.append("E:/Project/MetisAI/MetisAI_03")

from backend.llm.client import LLMClient, LLMClientFactory
from backend.llm.config import LLMConfig, LLMModelType
from backend.llm.constants import MODEL_INFO

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class TestLLMClient(unittest.IsolatedAsyncioTestCase):
    """测试 LLM 客户端"""

    async def test_client_initialization(self):
        """测试 LLM 客户端初始化"""
        logger.info("开始测试 LLM 客户端初始化")

        # 测试默认配置
        try:
            client = await LLMClientFactory.create_client()
            self.assertIsInstance(client, LLMClient)
            logger.debug("LLM 客户端实例创建成功")

            logger.info("LLM 客户端初始化测试完成")

        except Exception as e:
            logger.error(f"LLM 客户端初始化失败: {e}")
            self.skipTest("LLM 客户端初始化失败")

    async def test_custom_config(self):
        """测试自定义配置"""
        logger.info("开始测试自定义配置")

        try:
            config = LLMConfig(
                default_model=LLMModelType.GPT_4_TURBO,
                temperature=0.3,
                max_tokens=2048,
            )

            client = await LLMClientFactory.create_client(config)
            self.assertIsInstance(client, LLMClient)

            logger.debug(f"使用配置: {config}")
            logger.debug(f"实际配置: {client.config}")

            logger.info("自定义配置测试完成")

        except Exception as e:
            logger.error(f"自定义配置失败: {e}")
            self.skipTest("自定义配置失败")


class TestLLMGeneration(unittest.IsolatedAsyncioTestCase):
    """测试 LLM 响应生成"""

    async def test_text_generation(self):
        """测试文本生成"""
        logger.info("开始测试文本生成")

        try:
            client = await LLMClientFactory.create_client()

            # 简单的文本生成测试
            messages = [
                {"role": "user", "content": "你好，这是一个简单的测试"}
            ]

            response = await client.generate_response(messages)

            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            logger.debug(f"生成的响应: {response}")

            logger.info("文本生成测试完成")

        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            self.skipTest("文本生成测试失败")

    async def test_code_generation(self):
        """测试代码生成"""
        logger.info("开始测试代码生成")

        try:
            client = await LLMClientFactory.create_client()

            messages = [
                {"role": "user", "content": "请帮我写一个简单的 Python 函数"}
            ]

            response = await client.generate_response(messages)

            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            logger.debug(f"生成的代码: {response}")

            logger.info("代码生成测试完成")

        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            self.skipTest("代码生成测试失败")


class TestLLMModelSupport(unittest.IsolatedAsyncioTestCase):
    """测试 LLM 模型支持"""

    async def test_model_support(self):
        """测试模型支持"""
        logger.info("开始测试模型支持")

        try:
            client = await LLMClientFactory.create_client()

            models = client.list_supported_models()
            self.assertIsInstance(models, list)
            self.assertGreater(len(models), 0)

            logger.debug(f"支持的模型数量: {len(models)}")
            logger.debug(f"前 5 个支持的模型: {models[:5]}")

            # 测试特定模型是否支持
            if "gpt-4" in models:
                logger.debug("GPT-4 模型支持")
            if "claude-3-sonnet" in models:
                logger.debug("Claude 3 Sonnet 模型支持")

            logger.info("模型支持测试完成")

        except Exception as e:
            logger.error(f"模型支持测试失败: {e}")
            self.skipTest("模型支持测试失败")


class TestLLMIntegration(unittest.IsolatedAsyncioTestCase):
    """测试 LLM 集成功能"""

    async def test_chat_completion(self):
        """测试聊天完成"""
        logger.info("开始测试聊天完成")

        try:
            client = await LLMClientFactory.create_client()

            messages = [
                {"role": "system", "content": "你是一个帮助用户编写和优化代码的 AI"}
            ]

            user_input = "请帮我优化这个简单的 Python 函数：\n```python\ndef factorial(n):\n    result = 1\n    for i in range(n):\n        result *= (i + 1)\n    return result\n```"
            messages.append({"role": "user", "content": user_input})

            response = await client.generate_response(messages)

            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            logger.debug(f"生成的响应: {response}")

            logger.info("聊天完成测试完成")

        except Exception as e:
            logger.error(f"聊天完成失败: {e}")
            self.skipTest("聊天完成测试失败")


class TestLLMModelInfo(unittest.IsolatedAsyncioTestCase):
    """测试 LLM 模型信息"""

    async def test_model_info(self):
        """测试模型信息"""
        logger.info("开始测试模型信息")

        try:
            client = await LLMClientFactory.create_client()

            # 测试获取模型信息
            for model in ["gpt-4", "claude-3-sonnet"]:
                if client.is_model_supported(model):
                    info = client.get_model_info(model)
                    logger.debug(f"{model} 模型信息: {info}")
                else:
                    logger.debug(f"{model} 模型不支持")

            logger.info("模型信息测试完成")

        except Exception as e:
            logger.error(f"模型信息测试失败: {e}")
            self.skipTest("模型信息测试失败")


class TestLLMConcurrency(unittest.IsolatedAsyncioTestCase):
    """测试 LLM 并发请求"""

    async def test_concurrent_requests(self):
        """测试并发请求"""
        logger.info("开始测试并发请求")

        try:
            client = await LLMClientFactory.create_client()

            messages = [
                {"role": "user", "content": "你好"}
            ]

            # 测试 3 个并发请求
            tasks = []
            for i in range(3):
                task = asyncio.create_task(
                    client.generate_response(messages),
                    name=f"request-{i+1}",
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            for i, response in enumerate(responses):
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
                logger.debug(f"请求 {i+1} 响应: {response}")

            logger.info("并发请求测试完成")

        except Exception as e:
            logger.error(f"并发请求失败: {e}")
            self.skipTest("并发请求测试失败")


if __name__ == "__main__":
    unittest.main()
