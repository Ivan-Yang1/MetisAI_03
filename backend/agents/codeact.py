"""
CodeAct 智能体模块
实现可以执行代码的智能体
"""

import asyncio
import json
import re
import subprocess
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, validator

from backend.agents.base import AgentConfig, AgentInput, AgentOutput, AgentState, BaseAgent
from backend.models.agent import Agent, AgentType


class CodeActAgentConfig(AgentConfig):
    """CodeAct 智能体配置"""

    enable_code_execution: bool = Field(default=True, description="是否启用代码执行")
    code_language: str = Field(default="python", description="默认代码执行语言")
    max_code_lines: int = Field(default=100, description="最大代码行数", gt=0)
    sandbox_timeout: float = Field(
        default=30.0, description="沙箱执行超时时间", gt=0
    )
    enable_auto_retry: bool = Field(default=True, description="是否启用自动重试")

    @validator("code_language")
    def valid_code_language(cls, v: str) -> str:
        """验证代码语言"""
        valid_languages = ["python", "javascript", "typescript", "bash"]
        if v.lower() not in valid_languages:
            raise ValueError(f"不支持的代码语言: {v}")
        return v


class CodeActAgent(BaseAgent):
    """
    CodeAct 智能体
    可以执行代码的智能体
    """

    def __init__(
        self,
        agent_id: int,
        name: str,
        config: Optional[CodeActAgentConfig] = None,
    ):
        super().__init__(agent_id, name, AgentType.CODEACT, config or CodeActAgentConfig())
        self.config: CodeActAgentConfig = config or CodeActAgentConfig()
        self.code_execution_count: int = 0
        self.last_code_output: Optional[str] = None

    async def run(self, input_data: Union[AgentInput, str]) -> AgentOutput:
        """
        运行 CodeAct 智能体

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
                user_input = "你好！我是 CodeAct 智能体，我可以帮你编写和执行代码。"

        await self.set_state(AgentState.EXECUTING)

        try:
            # 尝试从用户输入中提取代码
            code = self._extract_code_from_input(user_input)

            if code and self.config.enable_code_execution:
                output = await self._execute_code(code)
                response = self._format_response(user_input, code, output)
            else:
                response = self._generate_text_response(user_input)

            await self.set_state(AgentState.COMPLETED)
            metadata = {
                "model": self.config.model,
                "temperature": self.config.temperature,
                "code_execution": bool(code),
                "execution_count": self.code_execution_count,
            }

            if code and self.config.enable_code_execution:
                metadata["output"] = output

            output = AgentOutput(
                response=response, state=AgentState.COMPLETED, metadata=metadata
            )

        except Exception as e:
            await self.set_state(AgentState.ERROR)
            response = f"执行代码时出错: {str(e)}\n\n请检查您的代码是否有语法错误或逻辑问题。"
            output = AgentOutput(
                response=response, state=AgentState.ERROR, metadata={"error": str(e)}
            )

        self.add_history(output)
        return output

    def _extract_code_from_input(self, input_text: str) -> Optional[str]:
        """
        从用户输入中提取代码块

        Args:
            input_text: 用户输入文本

        Returns:
            Optional[str]: 提取的代码，如果没有代码块则返回 None
        """
        # 支持多种代码块格式
        patterns = [
            # Markdown 代码块: ```python ... ```
            re.compile(r"```[\w]*\s*([\s\S]*?)```", re.DOTALL),
            # 简单代码块: ``` ... ```
            re.compile(r"```\s*([\s\S]*?)```", re.DOTALL),
            # 缩进代码块
            re.compile(r"^\s{4}([\s\S]*?)$", re.MULTILINE),
        ]

        for pattern in patterns:
            match = pattern.search(input_text)
            if match:
                code = match.group(1).strip()
                if code and len(code) <= self.config.max_code_lines:
                    return code

        return None

    async def _execute_code(self, code: str) -> str:
        """
        执行代码

        Args:
            code: 要执行的代码

        Returns:
            str: 执行结果
        """
        self.code_execution_count += 1

        try:
            if self.config.code_language == "python":
                return await self._execute_python_code(code)
            elif self.config.code_language == "javascript":
                return await self._execute_javascript_code(code)
            elif self.config.code_language == "bash":
                return await self._execute_bash_code(code)
            else:
                return f"不支持的代码语言: {self.config.code_language}"

        except Exception as e:
            return f"执行代码时出错: {str(e)}"

    async def _execute_python_code(self, code: str) -> str:
        """执行 Python 代码"""
        proc = await asyncio.create_subprocess_shell(
            f'python -c "{code}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.config.sandbox_timeout
            )

            if stdout:
                result = stdout.decode().strip()
            else:
                result = "没有输出"

            if stderr:
                result += f"\n错误: {stderr.decode().strip()}"

            return result

        except asyncio.TimeoutError:
            return "代码执行超时"

    async def _execute_javascript_code(self, code: str) -> str:
        """执行 JavaScript 代码"""
        proc = await asyncio.create_subprocess_shell(
            f'node -e "{code}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.config.sandbox_timeout
            )

            if stdout:
                result = stdout.decode().strip()
            else:
                result = "没有输出"

            if stderr:
                result += f"\n错误: {stderr.decode().strip()}"

            return result

        except asyncio.TimeoutError:
            return "代码执行超时"

    async def _execute_bash_code(self, code: str) -> str:
        """执行 Bash 代码"""
        proc = await asyncio.create_subprocess_shell(
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.config.sandbox_timeout
            )

            if stdout:
                result = stdout.decode().strip()
            else:
                result = "没有输出"

            if stderr:
                result += f"\n错误: {stderr.decode().strip()}"

            return result

        except asyncio.TimeoutError:
            return "代码执行超时"

    def _generate_text_response(self, input_text: str) -> str:
        """
        生成文本响应（不执行代码）

        Args:
            input_text: 用户输入文本

        Returns:
            str: 文本响应
        """
        responses = [
            "我理解你的需求，但我需要看到代码块才能执行。请将你的代码放在三个反引号之间，例如：\n```python\nprint('Hello, World!')\n```",
            "我可以帮你编写和执行代码。请提供你想要运行的代码示例。",
            "请提供代码块，我会帮你执行。支持 Python、JavaScript 和 Bash 代码。",
        ]

        # 根据输入长度选择响应
        if len(input_text) > 100:
            return responses[0]
        elif len(input_text) > 50:
            return responses[1]
        else:
            return responses[2]

    def _format_response(self, user_input: str, code: str, output: str) -> str:
        """
        格式化响应

        Args:
            user_input: 用户输入
            code: 执行的代码
            output: 执行结果

        Returns:
            str: 格式化后的响应
        """
        return (
            f"我已经执行了你的代码：\n\n```python\n{code}\n```\n\n执行结果：\n{output}\n\n"
            "如果需要修改代码或有其他需求，请告诉我。"
        )


class CodeActAgentFactory:
    """
    CodeAct 智能体工厂类
    用于创建不同类型的 CodeAct 智能体实例
    """

    @staticmethod
    def create_agent(
        agent_id: int, name: str, config: Optional[CodeActAgentConfig] = None
    ) -> CodeActAgent:
        """
        创建 CodeAct 智能体实例

        Args:
            agent_id: 智能体 ID
            name: 智能体名称
            config: 智能体配置

        Returns:
            CodeActAgent: 智能体实例
        """
        return CodeActAgent(agent_id, name, config or CodeActAgentConfig())

    @staticmethod
    def create_agent_from_db_model(db_agent: Agent) -> CodeActAgent:
        """
        从数据库模型创建智能体实例

        Args:
            db_agent: 数据库中的智能体记录

        Returns:
            CodeActAgent: 智能体实例
        """
        config = CodeActAgentConfig(**(db_agent.config or {}))
        agent = CodeActAgent(
            db_agent.id, db_agent.name, config
        )
        return agent
