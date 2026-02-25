"""
LLM 配置模块
定义 LLM 客户端的配置选项
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from llm.constants import DEFAULT_MODEL_CONFIG, SUPPORTED_LLM_PROVIDERS


class LLMModelType(str, Enum):
    """LLM 模型类型"""

    # OpenAI 模型
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"

    # Claude 3 模型
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240229"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20250219"

    # Google 模型
    GEMINI_PRO = "gemini-pro"
    GEMINI_1_5_PRO = "gemini-1.5-pro-latest"

    # Anthropic 模型
    ANTHROPIC_CLAUDE_3_OPUS = "anthropic/claude-3-opus-20240229"
    ANTHROPIC_CLAUDE_3_SONNET = "anthropic/claude-3-sonnet-20240229"

    # Azure 模型
    AZURE_GPT_4 = "azure/gpt-4"
    AZURE_GPT_3_5 = "azure/gpt-35-turbo"


class LLMModelConfig(BaseModel):
    """LLM 模型配置"""

    model: str = Field(
        default=LLMModelType.CLAUDE_3_SONNET,
        description="默认模型名称",
    )
    temperature: float = Field(
        default=0.7,
        description="温度参数，控制响应的创造性",
        ge=0.0,
        le=2.0,
    )
    max_tokens: int = Field(
        default=4096,
        description="最大令牌数",
        gt=0,
        le=128000,
    )
    top_p: float = Field(
        default=1.0,
        description="Top-p 参数",
        ge=0.0,
        le=1.0,
    )
    frequency_penalty: float = Field(
        default=0.0,
        description="频率惩罚",
        ge=-2.0,
        le=2.0,
    )
    presence_penalty: float = Field(
        default=0.0,
        description="存在惩罚",
        ge=-2.0,
        le=2.0,
    )
    timeout: float = Field(
        default=60.0,
        description="请求超时时间（秒）",
        gt=0,
        le=300,
    )

    @validator("model")
    def valid_model(cls, v: str) -> str:
        """验证模型名称"""
        valid_models = [e.value for e in LLMModelType]
        if v not in valid_models:
            raise ValueError(f"无效的模型名称: {v}, 有效模型: {valid_models}")
        return v


class LLMConfig(BaseModel):
    """LLM 配置"""

    # 基本配置
    default_model: str = Field(
        default=LLMModelType.CLAUDE_3_SONNET,
        description="默认使用的模型",
    )
    verbose: bool = Field(default=False, description="是否启用详细日志")
    debug: bool = Field(default=False, description="是否启用调试模式")

    # 模型配置
    generation_config: LLMModelConfig = Field(
        default_factory=lambda: LLMModelConfig(),
        description="生成配置",
    )

    # API 密钥配置
    openai_api_key: Optional[str] = Field(
        default=os.getenv("OPENAI_API_KEY"),
        description="OpenAI API 密钥",
    )
    anthropic_api_key: Optional[str] = Field(
        default=os.getenv("ANTHROPIC_API_KEY"),
        description="Anthropic API 密钥",
    )
    azure_api_key: Optional[str] = Field(
        default=os.getenv("AZURE_API_KEY"),
        description="Azure OpenAI API 密钥",
    )
    default_api_key: Optional[str] = Field(
        default=None,
        description="默认 API 密钥",
    )

    # 提供商配置
    supported_providers: List[str] = Field(
        default_factory=lambda: [p.value for p in SUPPORTED_LLM_PROVIDERS],
        description="支持的 LLM 提供商列表",
    )

    # 其他配置
    max_retries: int = Field(
        default=3,
        description="最大重试次数",
        ge=0,
        le=10,
    )
    retry_delay: float = Field(
        default=1.0,
        description="重试延迟（秒）",
        ge=0.0,
        le=60.0,
    )
    system_prompt: str = Field(
        default="你是一个 AI 助手，能够帮助用户完成各种编程和开发任务。",
        description="系统提示词",
    )
    streaming: bool = Field(default=False, description="是否启用流式响应")

    @validator("default_model")
    def valid_default_model(cls, v: str) -> str:
        """验证默认模型"""
        valid_models = [e.value for e in LLMModelType]
        if v not in valid_models:
            raise ValueError(f"无效的模型名称: {v}, 有效模型: {valid_models}")
        return v


class LLMProviderConfig(BaseModel):
    """LLM 提供商配置"""

    name: str = Field(..., description="提供商名称")
    api_key: Optional[str] = Field(default=None, description="API 密钥")
    base_url: Optional[str] = Field(default=None, description="API 基础 URL")
    default_model: str = Field(default=LLMModelType.CLAUDE_3_SONNET, description="默认模型")


class ProviderConfig(BaseModel):
    """提供商配置"""

    openai: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            default_model=LLMModelType.GPT_4_TURBO,
        ),
        description="OpenAI 配置",
    )
    anthropic: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            default_model=LLMModelType.CLAUDE_3_SONNET,
        ),
        description="Anthropic 配置",
    )
    azure: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="azure",
            api_key=os.getenv("AZURE_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_BASE_URL"),
            default_model=LLMModelType.AZURE_GPT_4,
        ),
        description="Azure OpenAI 配置",
    )
    google: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="google",
            api_key=os.getenv("GOOGLE_API_KEY"),
            default_model=LLMModelType.GEMINI_1_5_PRO,
        ),
        description="Google 配置",
    )


@dataclass
class ModelInfo:
    """模型信息数据类"""

    model_id: str
    name: str
    description: str
    provider: str
    supported_features: List[str] = field(default_factory=list)
    pricing: Dict[str, float] = field(default_factory=dict)


class ModelInfoManager:
    """模型信息管理"""

    _model_info: Dict[str, ModelInfo] = {}

    @classmethod
    def add_model_info(cls, model_info: ModelInfo):
        """添加模型信息"""
        cls._model_info[model_info.model_id] = model_info

    @classmethod
    def get_model_info(cls, model_id: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        return cls._model_info.get(model_id)

    @classmethod
    def get_all_models(cls) -> List[ModelInfo]:
        """获取所有支持的模型信息"""
        return list(cls._model_info.values())

    @classmethod
    def get_models_by_provider(cls, provider: str) -> List[ModelInfo]:
        """按提供商获取模型信息"""
        return [
            info for info in cls._model_info.values()
            if info.provider == provider
        ]


# 默认配置
DEFAULT_LLM_CONFIG = LLMConfig()

# 配置验证函数
def validate_llm_config(config: Union[Dict[str, Any], LLMConfig]) -> LLMConfig:
    """验证并转换 LLM 配置"""
    if isinstance(config, dict):
        return LLMConfig(**config)
    elif isinstance(config, LLMConfig):
        return config
    else:
        raise ValueError(f"无效的配置类型: {type(config)}")
