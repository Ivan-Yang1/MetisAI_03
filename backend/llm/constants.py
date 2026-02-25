"""
LLM 常量模块
定义 LLM 集成系统的常量和配置
"""

from enum import Enum


class SUPPORTED_LLM_PROVIDERS(Enum):
    """支持的 LLM 提供商"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"


class MODEL_CATEGORIES(Enum):
    """模型分类"""

    CHAT = "chat"
    CODE = "code"
    EMBEDDING = "embedding"
    ANALYSIS = "analysis"
    MULTIMODAL = "multimodal"


class MODEL_PRICING_TIERS(Enum):
    """模型定价层级"""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


# 默认模型配置
DEFAULT_MODEL_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "timeout": 60,
}

# 模型信息字典
MODEL_INFO = {
    "gpt-4": {
        "name": "GPT-4",
        "provider": "openai",
        "category": "multimodal",
        "max_tokens": 8192,
        "pricing": {"input": 0.03, "output": 0.06},
        "description": "最强大的 GPT 模型，适合复杂任务",
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "category": "multimodal",
        "max_tokens": 128000,
        "pricing": {"input": 0.01, "output": 0.03},
        "description": "GPT-4 的最新版本，支持更长上下文",
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "category": "chat",
        "max_tokens": 16384,
        "pricing": {"input": 0.0010, "output": 0.0020},
        "description": "平衡性能和成本的聊天模型",
    },
    "claude-3-opus": {
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "category": "multimodal",
        "max_tokens": 200000,
        "pricing": {"input": 0.0150, "output": 0.0750},
        "description": "Claude 系列最强大的模型",
    },
    "claude-3-sonnet": {
        "name": "Claude 3 Sonnet",
        "provider": "anthropic",
        "category": "chat",
        "max_tokens": 200000,
        "pricing": {"input": 0.0030, "output": 0.0150},
        "description": "平衡性能和成本的智能模型",
    },
    "claude-3-haiku": {
        "name": "Claude 3 Haiku",
        "provider": "anthropic",
        "category": "chat",
        "max_tokens": 200000,
        "pricing": {"input": 0.00025, "output": 0.00125},
        "description": "轻量级和成本效益高的智能模型",
    },
    "claude-3-5-sonnet": {
        "name": "Claude 3.5 Sonnet",
        "provider": "anthropic",
        "category": "multimodal",
        "max_tokens": 200000,
        "pricing": {"input": 0.0030, "output": 0.0150},
        "description": "Claude 3 Sonnet 的增强版本，支持更多功能",
    },
    "gemini-pro": {
        "name": "Gemini Pro",
        "provider": "google",
        "category": "multimodal",
        "max_tokens": 8192,
        "pricing": {"input": 0.0005, "output": 0.0015},
        "description": "Google 的 Gemini Pro 模型",
    },
    "gemini-1.5-pro": {
        "name": "Gemini 1.5 Pro",
        "provider": "google",
        "category": "multimodal",
        "max_tokens": 200000,
        "pricing": {"input": 0.00125, "output": 0.00375},
        "description": "Google 的最强大模型，支持更长上下文",
    },
    "deepseek-coder": {
        "name": "DeepSeek Coder",
        "provider": "deepseek",
        "category": "code",
        "max_tokens": 8192,
        "pricing": {"input": 0.0002, "output": 0.0005},
        "description": "专为编程任务优化的模型",
    },
}

# 常用提示词模板
PROMPT_TEMPLATES = {
    "code_review": """请帮我审核以下代码，找出潜在的问题：
{{code}}

请从以下方面进行审核：
1. 语法和逻辑错误
2. 安全性问题
3. 性能问题
4. 代码风格和最佳实践
5. 潜在的 Bug 和边界情况

返回详细的审核结果。""",
    "code_explanation": """请帮我解释以下代码的功能和实现原理：
{{code}}

请提供：
1. 代码的整体功能
2. 关键算法和数据结构
3. 实现细节和设计决策
4. 可能的优化建议

返回详细的解释。""",
    "documentation": """请帮我为以下代码创建文档：
{{code}}

请创建：
1. 文件头部注释（描述文件用途）
2. 类和方法文档字符串
3. 关键变量和常量说明
4. 示例使用方法

遵循标准的文档格式。""",
}

# 聊天消息类型
CHAT_MESSAGE_TYPES = {
    "system": "系统消息",
    "user": "用户消息",
    "assistant": "助手消息",
}

# 错误类型
LLM_ERROR_TYPES = {
    "rate_limit": "请求频率超限",
    "invalid_api_key": "API 密钥无效",
    "model_not_found": "模型未找到",
    "request_timeout": "请求超时",
    "content_policy": "内容违反政策",
    "server_error": "服务器错误",
}
