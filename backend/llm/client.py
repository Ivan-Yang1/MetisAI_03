"""
LLM 集成系统模块
使用 litellm 库与各种 LLM 模型进行交互
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

import litellm

from llm.config import LLMConfig, LLMModelType

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端 - 与 LLM 模型进行交互的抽象层"""

    _instance: Optional["LLMClient"] = None

    def __new__(cls, config: Optional[LLMConfig] = None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初始化 LLM 客户端

        Args:
            config: LLM 配置
        """
        if self._initialized:
            return

        self._initialized = True
        self.config = config or LLMConfig()
        self._init_litellm()
        logger.info("LLM 客户端初始化完成")

    def _init_litellm(self):
        """初始化 litellm 库"""
        # 配置 litellm
        litellm.set_verbose(self.config.verbose)
        litellm.set_custom_llm_provider("openai", "https://api.openai.com/v1")

        # 配置 API 密钥
        self._configure_api_keys()

        if self.config.debug:
            logger.debug("litellm 初始化完成")

    def _configure_api_keys(self):
        """配置 API 密钥"""
        # 从配置中设置 API 密钥
        if self.config.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
        if self.config.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.config.anthropic_api_key
        if self.config.azure_api_key:
            os.environ["AZURE_API_KEY"] = self.config.azure_api_key

        # 设置默认 API 密钥（如果有）
        if self.config.default_api_key:
            litellm.api_key = self.config.default_api_key

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成 LLM 响应

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "消息内容"}]
            config: 生成配置，覆盖默认配置

        Returns:
            str: LLM 响应内容
        """
        try:
            logger.debug(f"LLM 生成响应，配置: {config}")

            # 合并配置
            generation_config = self.config.generation_config.model_dump()
            if config:
                generation_config.update(config)

            # 使用 litellm 生成响应
            model_name = generation_config.get("model", self.config.default_model)
            logger.debug(f"使用模型: {model_name}")

            response = await litellm.acompletion(
                model=model_name,
                messages=messages,
                temperature=generation_config.get("temperature", 0.7),
                max_tokens=generation_config.get("max_tokens", 4096),
                top_p=generation_config.get("top_p", 1.0),
                frequency_penalty=generation_config.get("frequency_penalty", 0.0),
                presence_penalty=generation_config.get("presence_penalty", 0.0),
                timeout=generation_config.get("timeout", 60),
            )

            content = response.choices[0].message.content
            logger.debug(f"LLM 响应生成成功，长度: {len(content)}")

            return content

        except Exception as e:
            logger.error(f"LLM 生成响应失败: {str(e)}")
            raise

    async def generate_text(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成文本响应（简化版本）

        Args:
            prompt: 提示文本
            config: 生成配置

        Returns:
            str: LLM 响应
        """
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": prompt},
        ]

        return await self.generate_response(messages, config)

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取模型信息

        Args:
            model_name: 模型名称

        Returns:
            Optional[Dict[str, Any]]: 模型信息
        """
        try:
            from litellm import get_model_info

            info = get_model_info(model_name)
            return info
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return None

    def list_supported_models(self) -> List[str]:
        """
        获取支持的模型列表

        Returns:
            List[str]: 支持的模型列表
        """
        # 使用 litellm 支持的模型
        from litellm import get_model_list

        return get_model_list()

    def is_model_supported(self, model_name: str) -> bool:
        """
        检查模型是否被支持

        Args:
            model_name: 模型名称

        Returns:
            bool: 是否支持
        """
        return model_name in self.list_supported_models()

    async def generate_embedding(
        self, text: str, model: Optional[str] = None
    ) -> List[float]:
        """
        生成文本嵌入

        Args:
            text: 要嵌入的文本
            model: 嵌入模型名称

        Returns:
            List[float]: 嵌入向量
        """
        try:
            model_name = model or "text-embedding-3-small"
            response = await litellm.aembedding(
                model=model_name,
                input=text,
                timeout=self.config.model_config.timeout,
            )

            return response.data[0].embedding
        except Exception as e:
            logger.error(f"生成嵌入失败: {str(e)}")
            raise

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成完整的聊天完成响应（包含详细信息）

        Args:
            messages: 消息列表
            model: 模型名称
            config: 生成配置

        Returns:
            Dict[str, Any]: 完整响应
        """
        try:
            generation_config = self.config.model_config.dict()
            if config:
                generation_config.update(config)

            response = await litellm.acompletion(
                model=model or self.config.default_model,
                messages=messages,
                **generation_config,
            )

            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "model": response.model,
            }

        except Exception as e:
            logger.error(f"聊天完成失败: {str(e)}")
            raise


class LLMClientFactory:
    """LLM 客户端工厂类"""

    @staticmethod
    async def create_client(config: Optional[LLMConfig] = None) -> LLMClient:
        """
        创建 LLM 客户端实例

        Args:
            config: LLM 配置

        Returns:
            LLMClient: LLM 客户端实例
        """
        return LLMClient(config)

    @staticmethod
    async def get_instance() -> LLMClient:
        """
        获取单例 LLM 客户端实例

        Returns:
            LLMClient: LLM 客户端实例
        """
        if LLMClient._instance is None:
            LLMClient._instance = LLMClient()
        return LLMClient._instance


async def get_llm_client() -> LLMClient:
    """
    获取全局 LLM 客户端实例

    Returns:
        LLMClient: LLM 客户端实例
    """
    return await LLMClientFactory.get_instance()
