"""
动作执行服务器模块
负责处理和执行各种类型的动作
"""

import asyncio
import logging
import subprocess
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from backend.runtime.config import (
    DEFAULT_CONFIG,
    ResourceLimits,
    SandboxConfig,
    SandboxRuntimeOptions,
    SandboxType,
)
from backend.runtime.docker_runtime import DockerRuntime, DockerRuntimeFactory

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """动作类型枚举"""

    EXECUTE_COMMAND = "execute_command"
    RUN_CODE = "run_code"
    TRANSFER_FILE = "transfer_file"
    GET_FILE = "get_file"
    PUT_FILE = "put_file"
    DELETE_FILE = "delete_file"
    LIST_DIRECTORY = "list_directory"
    CHECK_STATUS = "check_status"
    CUSTOM = "custom"


class ActionStatus(str, Enum):
    """动作状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


class ActionRequest(BaseModel):
    """动作请求模型"""

    action_type: ActionType = Field(..., description="动作类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="动作参数")
    sandbox_options: Optional[SandboxRuntimeOptions] = Field(
        default=None, description="沙箱运行时选项"
    )
    timeout: int = Field(default=300, description="动作超时时间（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ActionResponse(BaseModel):
    """动作响应模型"""

    action_id: str = Field(..., description="动作 ID")
    status: ActionStatus = Field(..., description="动作状态")
    result: Optional[Dict[str, Any]] = Field(default=None, description="动作结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    execution_time: float = Field(default=0.0, description="执行时间（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ActionExecutor:
    """
    动作执行器
    负责处理和执行各种类型的动作
    """

    def __init__(self, runtime: Optional[Union["DockerRuntime", "LocalRuntime"]] = None):
        """
        初始化动作执行器

        Args:
            runtime: 沙箱运行时实例
        """
        self._runtime = runtime
        self._action_handlers: Dict[ActionType, Callable] = {}
        self._running_actions: Dict[str, asyncio.Task] = {}
        self._action_lock = asyncio.Lock()

        # 注册默认动作处理程序（同步版本）
        self._register_default_handlers_sync()

    def _register_default_handlers_sync(self):
        """同步注册默认动作处理程序"""
        self._action_handlers[ActionType.EXECUTE_COMMAND] = self._handle_execute_command
        self._action_handlers[ActionType.RUN_CODE] = self._handle_run_code
        self._action_handlers[ActionType.TRANSFER_FILE] = self._handle_transfer_file
        self._action_handlers[ActionType.GET_FILE] = self._handle_get_file
        self._action_handlers[ActionType.PUT_FILE] = self._handle_put_file
        self._action_handlers[ActionType.DELETE_FILE] = self._handle_delete_file
        self._action_handlers[ActionType.LIST_DIRECTORY] = self._handle_list_directory
        self._action_handlers[ActionType.CHECK_STATUS] = self._handle_check_status

    async def _register_default_handlers(self):
        """注册默认动作处理程序"""
        self._action_handlers[ActionType.EXECUTE_COMMAND] = self._handle_execute_command
        self._action_handlers[ActionType.RUN_CODE] = self._handle_run_code
        self._action_handlers[ActionType.TRANSFER_FILE] = self._handle_transfer_file
        self._action_handlers[ActionType.GET_FILE] = self._handle_get_file
        self._action_handlers[ActionType.PUT_FILE] = self._handle_put_file
        self._action_handlers[ActionType.DELETE_FILE] = self._handle_delete_file
        self._action_handlers[ActionType.LIST_DIRECTORY] = self._handle_list_directory
        self._action_handlers[ActionType.CHECK_STATUS] = self._handle_check_status

    async def execute_action(
        self,
        action_request: ActionRequest,
        action_id: Optional[str] = None,
    ) -> ActionResponse:
        """
        执行动作

        Args:
            action_request: 动作请求
            action_id: 动作 ID（可选，自动生成）

        Returns:
            ActionResponse: 动作响应
        """
        if action_id is None:
            import uuid

            action_id = str(uuid.uuid4())

        logger.info(f"执行动作: {action_id} ({action_request.action_type})")

        # 初始化运行时
        if self._runtime is None:
            self._runtime = await DockerRuntimeFactory.get_instance()

        # 创建动作响应
        action_response = ActionResponse(
            action_id=action_id,
            status=ActionStatus.RUNNING,
            metadata=action_request.metadata,
        )

        try:
            # 查找动作处理程序
            handler = self._action_handlers.get(action_request.action_type)
            if not handler:
                raise Exception(f"不支持的动作类型: {action_request.action_type}")

            # 执行动作
            start_time = datetime.now()

            result = await handler(action_request, action_response)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            # 更新响应
            action_response.status = ActionStatus.COMPLETED
            action_response.result = result
            action_response.execution_time = execution_time

            logger.info(f"动作执行完成: {action_id}，耗时: {execution_time:.2f}秒")

        except asyncio.TimeoutError:
            action_response.status = ActionStatus.TIMED_OUT
            action_response.error = "动作执行超时"
            logger.error(f"动作执行超时: {action_id}")

        except Exception as e:
            action_response.status = ActionStatus.FAILED
            action_response.error = str(e)
            logger.error(f"动作执行失败: {action_id}，错误: {e}")

        return action_response

    async def _handle_execute_command(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理执行命令动作"""
        command = request.parameters.get("command")
        if not command:
            raise Exception("命令参数缺失")

        container_id = request.parameters.get("container_id")
        if not container_id:
            # 创建临时容器
            container_id = await self._runtime.create_container(request.sandbox_options)
            response.metadata["temp_container"] = container_id

        result = await self._runtime.execute_command(
            container_id, command, request.timeout
        )

        return {
            "output": result.get("output", ""),
            "return_code": result.get("return_code", -1),
            "success": result.get("success", False),
        }

    async def _handle_run_code(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理运行代码动作"""
        code = request.parameters.get("code")
        language = request.parameters.get("language", "python")
        filename = request.parameters.get("filename", "temp_code")

        if not code:
            raise Exception("代码参数缺失")

        # 创建代码执行命令
        if language == "python":
            command = f"python -c \"{code.replace('\"', '\\\\\"')}\""
        elif language == "javascript":
            command = f"node -e \"{code.replace('\"', '\\\\\"')}\""
        elif language == "bash":
            command = code
        else:
            raise Exception(f"不支持的语言: {language}")

        container_id = request.parameters.get("container_id")
        if not container_id:
            container_id = await self._runtime.create_container(request.sandbox_options)
            response.metadata["temp_container"] = container_id

        result = await self._runtime.execute_command(
            container_id, command, request.timeout
        )

        return {
            "output": result.get("output", ""),
            "return_code": result.get("return_code", -1),
            "success": result.get("success", False),
            "language": language,
        }

    async def _handle_transfer_file(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理文件传输动作"""
        source_path = request.parameters.get("source_path")
        destination_path = request.parameters.get("destination_path")
        container_id = request.parameters.get("container_id")

        if not source_path or not destination_path:
            raise Exception("源路径和目标路径参数缺失")

        if not container_id:
            raise Exception("容器 ID 参数缺失")

        await self._runtime.copy_to_container(
            container_id, source_path, destination_path
        )

        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
        }

    async def _handle_get_file(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理获取文件动作"""
        container_path = request.parameters.get("container_path")
        host_path = request.parameters.get("host_path")
        container_id = request.parameters.get("container_id")

        if not container_path or not host_path:
            raise Exception("容器路径和主机路径参数缺失")

        if not container_id:
            raise Exception("容器 ID 参数缺失")

        await self._runtime.copy_from_container(
            container_id, container_path, host_path
        )

        return {
            "success": True,
            "container_path": container_path,
            "host_path": host_path,
        }

    async def _handle_put_file(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理放置文件动作"""
        return await self._handle_transfer_file(request, response)

    async def _handle_delete_file(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理删除文件动作"""
        file_path = request.parameters.get("file_path")
        container_id = request.parameters.get("container_id")

        if not file_path:
            raise Exception("文件路径参数缺失")

        if not container_id:
            raise Exception("容器 ID 参数缺失")

        command = f"rm -f {file_path}"
        result = await self._runtime.execute_command(
            container_id, command, request.timeout
        )

        return {
            "success": result.get("success", False),
            "file_path": file_path,
        }

    async def _handle_list_directory(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理列出目录动作"""
        directory_path = request.parameters.get("directory_path")
        container_id = request.parameters.get("container_id")

        if not directory_path:
            raise Exception("目录路径参数缺失")

        if not container_id:
            raise Exception("容器 ID 参数缺失")

        command = f"ls -la {directory_path}"
        result = await self._runtime.execute_command(
            container_id, command, request.timeout
        )

        return {
            "success": result.get("success", False),
            "directory": directory_path,
            "content": result.get("output", ""),
        }

    async def _handle_check_status(
        self, request: ActionRequest, response: ActionResponse
    ) -> Dict[str, Any]:
        """处理检查状态动作"""
        container_id = request.parameters.get("container_id")
        if not container_id:
            raise Exception("容器 ID 参数缺失")

        status = await self._runtime.get_container_status(container_id)

        return {
            "success": True,
            "container_status": status,
        }

    def register_action_handler(
        self, action_type: ActionType, handler: Callable
    ) -> None:
        """
        注册自定义动作处理程序

        Args:
            action_type: 动作类型
            handler: 动作处理程序
        """
        self._action_handlers[action_type] = handler
        logger.debug(f"动作处理程序已注册: {action_type}")


class ActionExecutorFactory:
    """动作执行器工厂类"""

    @staticmethod
    async def create_executor(
        runtime: Optional[Union["DockerRuntime", "LocalRuntime"]] = None,
    ) -> "ActionExecutor":
        """
        创建动作执行器实例

        Args:
            runtime: 沙箱运行时实例

        Returns:
            ActionExecutor: 动作执行器实例
        """
        if not runtime:
            runtime = await DockerRuntimeFactory.get_instance()

        return ActionExecutor(runtime)


class ActionServer:
    """动作执行服务器"""

    def __init__(self, executor: Optional[ActionExecutor] = None):
        """
        初始化动作服务器

        Args:
            executor: 动作执行器实例
        """
        self._executor = executor or ActionExecutor()
        self._running_actions: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """初始化动作服务器"""
        logger.info("动作执行服务器初始化中...")

        # 这里可以添加服务器初始化逻辑，如：
        # - 配置服务器参数
        # - 初始化网络连接
        # - 启动后台任务

        logger.info("动作执行服务器初始化完成")

    async def submit_action(self, request: ActionRequest) -> str:
        """
        提交动作请求

        Args:
            request: 动作请求

        Returns:
            str: 动作 ID
        """
        import uuid

        action_id = str(uuid.uuid4())

        # 创建任务
        task = asyncio.create_task(
            self._executor.execute_action(request, action_id)
        )

        # 存储任务
        async with self._lock:
            self._running_actions[action_id] = task

        return action_id

    async def get_action_result(self, action_id: str) -> Optional[ActionResponse]:
        """
        获取动作结果

        Args:
            action_id: 动作 ID

        Returns:
            Optional[ActionResponse]: 动作响应
        """
        task = self._running_actions.get(action_id)
        if not task:
            return None

        # 检查任务是否完成
        if task.done():
            async with self._lock:
                del self._running_actions[action_id]

            return task.result()

        return None

    async def cancel_action(self, action_id: str) -> bool:
        """
        取消动作执行

        Args:
            action_id: 动作 ID

        Returns:
            bool: 是否成功取消
        """
        task = self._running_actions.get(action_id)
        if not task or task.done():
            return False

        try:
            task.cancel()
            await task

            async with self._lock:
                del self._running_actions[action_id]

            logger.info(f"动作已取消: {action_id}")
            return True

        except asyncio.CancelledError:
            logger.info(f"动作已取消: {action_id}")
            return True

        except Exception as e:
            logger.error(f"取消动作失败: {action_id}，错误: {e}")
            return False

    async def get_running_actions(self) -> List[str]:
        """获取正在运行的动作列表"""
        async with self._lock:
            return list(self._running_actions.keys())


class ActionServerFactory:
    """动作服务器工厂类"""

    _instance: Optional["ActionServer"] = None

    @staticmethod
    async def get_instance() -> "ActionServer":
        """获取动作服务器实例（单例）"""
        if ActionServerFactory._instance is None:
            ActionServerFactory._instance = ActionServer()
            await ActionServerFactory._instance.initialize()
        return ActionServerFactory._instance


# 默认动作服务器
_default_server: Optional["ActionServer"] = None


async def get_action_server() -> ActionServer:
    """获取默认动作服务器实例"""
    global _default_server

    if _default_server is None:
        _default_server = ActionServer()
        await _default_server.initialize()

    return _default_server
