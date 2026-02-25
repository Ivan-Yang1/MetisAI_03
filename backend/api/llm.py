"""
LLM 集成 API
负责与 LLM 模型交互的 API 接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from llm.client import get_llm_client
from llm.config import LLMConfig, LLMModelType
from llm.constants import PROMPT_TEMPLATES

router = APIRouter(prefix="/api/llm", tags=["LLM 集成"])


class Message(BaseModel):
    """消息模型"""

    role: str
    content: str


class GenerationConfig(BaseModel):
    """生成配置模型"""

    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


class LLMRequest(BaseModel):
    """LLM 请求模型"""

    messages: List[Message]
    config: Optional[GenerationConfig] = None


class LLMResponse(BaseModel):
    """LLM 响应模型"""

    response: str
    model: str
    generation_time: float


class CodeGenerationRequest(BaseModel):
    """代码生成请求模型"""

    prompt: str
    language: Optional[str] = "python"
    config: Optional[GenerationConfig] = None


class CodeGenerationResponse(BaseModel):
    """代码生成响应模型"""

    code: str
    language: str
    model: str
    generation_time: float


@router.post("/generate", response_model=LLMResponse)
async def generate_response(
    request: LLMRequest,
    client=Depends(get_llm_client),
):
    """
    生成 LLM 响应

    Args:
        request: LLM 请求，包含消息列表和配置

    Returns:
        LLM 响应
    """
    try:
        # 准备配置
        generation_config = {}
        if request.config:
            generation_config = request.config.dict(exclude_unset=True)

        # 生成响应
        response = await client.generate_response(request.messages, generation_config)

        return LLMResponse(
            response=response,
            model=generation_config.get("model", "claude-3-sonnet"),
            generation_time=0.0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成响应失败: {str(e)}"
        )


@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    client=Depends(get_llm_client),
):
    """
    生成代码

    Args:
        request: 代码生成请求，包含提示和配置

    Returns:
        代码生成响应
    """
    try:
        # 准备配置
        generation_config = {}
        if request.config:
            generation_config = request.config.dict(exclude_unset=True)

        # 准备提示
        prompt = (
            f"你是一个专业的 {request.language} 代码生成助手。"
            f"请为以下需求生成 {request.language} 代码：\n{request.prompt}\n\n"
            "要求：\n"
            "- 代码必须符合最佳实践\n"
            "- 包含适当的注释\n"
            "- 确保代码可正常运行\n"
            "- 提供使用示例\n"
        )

        # 生成响应
        response = await client.generate_response([{"role": "user", "content": prompt}], generation_config)

        # 从响应中提取代码（简单的正则表达式）
        import re

        code_match = re.search(r"```[\w]*\s*([\s\S]*?)```", response)
        code = code_match.group(1) if code_match else response

        return CodeGenerationResponse(
            code=code.strip(),
            language=request.language,
            model=generation_config.get("model", "claude-3-sonnet"),
            generation_time=0.0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"代码生成失败: {str(e)}"
        )


@router.get("/models", response_model=List[str])
async def get_supported_models():
    """
    获取支持的 LLM 模型列表

    Returns:
        支持的模型列表
    """
    try:
        # 获取所有支持的模型
        models = [e.value for e in LLMModelType]
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型列表失败: {str(e)}"
        )


@router.get("/templates", response_model=List[str])
async def get_prompt_templates():
    """
    获取提示模板列表

    Returns:
        提示模板列表
    """
    try:
        return list(PROMPT_TEMPLATES.keys())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取提示模板失败: {str(e)}"
        )


@router.get("/template/{name}")
async def get_prompt_template(name: str):
    """
    获取特定提示模板

    Args:
        name: 模板名称

    Returns:
        提示模板内容
    """
    try:
        template = PROMPT_TEMPLATES.get(name)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"提示模板 {name} 不存在"
            )

        return {"name": name, "template": template}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取提示模板失败: {str(e)}"
        )
