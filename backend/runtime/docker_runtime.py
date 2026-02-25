"""
Docker 运行时模块
负责实现 Docker 容器沙箱的创建和管理
"""

import asyncio
import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Union

from backend.runtime.config import (
    DEFAULT_CONFIG,
    DockerConfig,
    ResourceLimits,
    SandboxConfig,
    SandboxRuntimeOptions,
    SandboxType,
)

logger = logging.getLogger(__name__)


class DockerRuntime:
    """
    Docker 运行时实现
    负责 Docker 容器的创建、管理和执行
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        初始化 Docker 运行时

        Args:
            config: 沙箱配置
        """
        self.config = config or DEFAULT_CONFIG
        self._containers: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """初始化 Docker 运行时"""
        if self._initialized:
            return

        logger.info("正在初始化 Docker 运行时...")

        try:
            # 检查 Docker 是否可用
            await self._run_docker_command(["version"])
            logger.info("Docker 运行时初始化成功")
            self._initialized = True
        except Exception as e:
            logger.error(f"Docker 运行时初始化失败: {e}")
            raise

    async def _run_docker_command(
        self,
        args: List[str],
        check: bool = True,
        cwd: Optional[str] = None,
    ) -> str:
        """
        运行 Docker 命令

        Args:
            args: 命令参数
            check: 是否检查错误
            cwd: 工作目录

        Returns:
            str: 命令输出
        """
        command = ["docker"] + args
        logger.debug(f"执行 Docker 命令: {' '.join(command)}")

        proc = await asyncio.create_subprocess_shell(
            " ".join(command),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await proc.communicate()

        stdout_str = stdout.decode().strip() if stdout else ""
        stderr_str = stderr.decode().strip() if stderr else ""

        if check and proc.returncode != 0:
            logger.error(f"Docker 命令执行失败: {stderr_str}")
            raise Exception(f"Docker 命令执行失败: {stderr_str}")

        return stdout_str

    async def create_container(
        self,
        options: Optional[SandboxRuntimeOptions] = None,
        **kwargs,
    ) -> str:
        """
        创建 Docker 容器

        Args:
            options: 运行时选项
            **kwargs: 额外参数

        Returns:
            str: 容器 ID
        """
        if not self._initialized:
            await self.initialize()

        options = options or SandboxRuntimeOptions()

        async with self._lock:
            container_config = self._build_container_config(options)

            # 创建容器
            cmd = [
                "create",
                "--name",
                container_config["name"],
                "--workdir",
                options.working_dir,
                "--network",
                options.docker_config.network_mode,
            ]

            # 添加资源限制
            cmd.extend(["--cpus", options.resource_limits.cpu])
            cmd.extend(["--memory", options.resource_limits.memory])

            # 添加挂载卷
            if options.docker_config.volumes:
                for host_path, container_path in options.docker_config.volumes.items():
                    cmd.extend(["-v", f"{host_path}:{container_path}"])

            # 添加环境变量
            if options.docker_config.environment:
                for key, value in options.docker_config.environment.items():
                    cmd.extend(["-e", f"{key}={value}"])

            # 添加特权模式
            if options.docker_config.privileged:
                cmd.append("--privileged")

            cmd.append(options.docker_config.image)

            # 添加入口点和命令
            if options.docker_config.entrypoint:
                cmd.extend(["--entrypoint", options.docker_config.entrypoint])

            if options.docker_config.command:
                cmd.append(options.docker_config.command)

            container_id = await self._run_docker_command(cmd)

            # 启动容器
            await self._run_docker_command(["start", container_id])

            # 记录容器信息
            self._containers[container_id] = {
                "container_id": container_id,
                "name": container_config["name"],
                "options": options.dict(),
                "status": "running",
                "created_at": asyncio.get_event_loop().time(),
            }

            logger.info(f"Docker 容器创建成功: {container_id} ({container_config['name']})")
            return container_id

    def _build_container_config(self, options: SandboxRuntimeOptions) -> Dict[str, Any]:
        """
        构建容器配置

        Args:
            options: 运行时选项

        Returns:
            Dict[str, Any]: 容器配置
        """
        # 生成唯一的容器名称
        import uuid

        container_name = f"openhands-{uuid.uuid4().hex[:12]}"

        return {
            "name": container_name,
            "workdir": options.working_dir,
            "image": options.docker_config.image,
            "network": options.docker_config.network_mode,
        }

    async def execute_command(
        self,
        container_id: str,
        command: str,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        在 Docker 容器中执行命令

        Args:
            container_id: 容器 ID
            command: 要执行的命令
            timeout: 超时时间（秒）
            **kwargs: 额外参数

        Returns:
            Dict[str, Any]: 执行结果
        """
        if container_id not in self._containers:
            raise Exception(f"容器未找到: {container_id}")

        timeout = timeout or self.config.resource_limits.timeout

        logger.debug(f"在容器 {container_id} 中执行命令: {command}")

        try:
            cmd = ["exec", container_id]
            cmd.extend(["sh", "-c", command])

            result = await asyncio.wait_for(
                self._run_docker_command(cmd),
                timeout=timeout,
            )

            logger.debug(f"命令执行成功: {container_id}")
            return {
                "success": True,
                "output": result,
                "return_code": 0,
            }

        except asyncio.TimeoutError:
            logger.error(f"命令执行超时: {container_id}")
            return {
                "success": False,
                "output": "命令执行超时",
                "return_code": -1,
                "error": "Timeout",
            }

        except Exception as e:
            logger.error(f"命令执行失败: {container_id}, {e}")
            return {
                "success": False,
                "output": str(e),
                "return_code": -1,
                "error": str(e),
            }

    async def copy_to_container(
        self,
        container_id: str,
        host_path: str,
        container_path: str,
    ) -> bool:
        """
        复制文件到容器

        Args:
            container_id: 容器 ID
            host_path: 主机路径
            container_path: 容器路径

        Returns:
            bool: 是否成功
        """
        if container_id not in self._containers:
            raise Exception(f"容器未找到: {container_id}")

        try:
            await self._run_docker_command(["cp", host_path, f"{container_id}:{container_path}"])
            logger.debug(f"文件已复制到容器: {container_id}, {host_path} -> {container_path}")
            return True
        except Exception as e:
            logger.error(f"文件复制失败: {container_id}, {e}")
            return False

    async def copy_from_container(
        self,
        container_id: str,
        container_path: str,
        host_path: str,
    ) -> bool:
        """
        从容器复制文件到主机

        Args:
            container_id: 容器 ID
            container_path: 容器路径
            host_path: 主机路径

        Returns:
            bool: 是否成功
        """
        if container_id not in self._containers:
            raise Exception(f"容器未找到: {container_id}")

        try:
            await self._run_docker_command(["cp", f"{container_id}:{container_path}", host_path])
            logger.debug(f"文件已从容器复制到主机: {container_id}, {container_path} -> {host_path}")
            return True
        except Exception as e:
            logger.error(f"文件复制失败: {container_id}, {e}")
            return False

    async def get_container_status(self, container_id: str) -> Dict[str, Any]:
        """
        获取容器状态

        Args:
            container_id: 容器 ID

        Returns:
            Dict[str, Any]: 容器状态信息
        """
        if container_id not in self._containers:
            raise Exception(f"容器未找到: {container_id}")

        try:
            inspect_info = await self._run_docker_command(["inspect", container_id])
            info = json.loads(inspect_info)[0]

            status = info["State"]["Status"]
            cpu_usage = info["Stats"]["cpu_stats"]["cpu_usage"]["total_usage"] if "Stats" in info else 0
            memory_usage = info["Stats"]["memory_stats"]["usage"] if "Stats" in info else 0

            return {
                "container_id": container_id,
                "name": self._containers[container_id]["name"],
                "status": status,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "created_at": self._containers[container_id]["created_at"],
            }

        except Exception as e:
            logger.error(f"获取容器状态失败: {container_id}, {e}")
            return {
                "container_id": container_id,
                "name": self._containers[container_id]["name"],
                "status": "unknown",
                "cpu_usage": 0,
                "memory_usage": 0,
                "created_at": self._containers[container_id]["created_at"],
                "error": str(e),
            }

    async def stop_container(self, container_id: str) -> bool:
        """
        停止容器

        Args:
            container_id: 容器 ID

        Returns:
            bool: 是否成功
        """
        if container_id not in self._containers:
            raise Exception(f"容器未找到: {container_id}")

        try:
            await self._run_docker_command(["stop", container_id])
            self._containers[container_id]["status"] = "stopped"
            logger.info(f"容器已停止: {container_id}")
            return True
        except Exception as e:
            logger.error(f"停止容器失败: {container_id}, {e}")
            return False

    async def remove_container(self, container_id: str, force: bool = True) -> bool:
        """
        移除容器

        Args:
            container_id: 容器 ID
            force: 是否强制移除

        Returns:
            bool: 是否成功
        """
        if container_id not in self._containers:
            raise Exception(f"容器未找到: {container_id}")

        try:
            # 如果容器正在运行，先停止
            status = await self.get_container_status(container_id)
            if status["status"] == "running":
                await self.stop_container(container_id)

            cmd = ["rm"]
            if force:
                cmd.append("-f")
            cmd.append(container_id)

            await self._run_docker_command(cmd)

            del self._containers[container_id]
            logger.info(f"容器已移除: {container_id}")
            return True

        except Exception as e:
            logger.error(f"移除容器失败: {container_id}, {e}")
            return False

    async def cleanup_container(self, container_id: str) -> None:
        """
        清理容器资源

        Args:
            container_id: 容器 ID
        """
        if container_id not in self._containers:
            return

        try:
            await self.remove_container(container_id)
        except Exception as e:
            logger.error(f"容器清理失败: {container_id}, {e}")

    async def get_all_containers(self) -> List[Dict[str, Any]]:
        """
        获取所有容器信息

        Returns:
            List[Dict[str, Any]]: 容器信息列表
        """
        containers = []

        for container_id, info in self._containers.items():
            try:
                status = await self.get_container_status(container_id)
                containers.append(status)
            except Exception as e:
                logger.error(f"获取容器 {container_id} 状态失败: {e}")

        return containers

    async def cleanup_all(self) -> None:
        """清理所有容器资源"""
        logger.info("正在清理所有容器资源...")

        for container_id in list(self._containers.keys()):
            await self.cleanup_container(container_id)

        logger.info("所有容器资源清理完成")


class DockerRuntimeFactory:
    """Docker 运行时工厂类"""

    _instance: Optional["DockerRuntime"] = None

    @staticmethod
    async def get_instance(config: Optional[SandboxConfig] = None) -> "DockerRuntime":
        """
        获取 Docker 运行时实例

        Args:
            config: 配置

        Returns:
            DockerRuntime: 运行时实例
        """
        if DockerRuntimeFactory._instance is None:
            DockerRuntimeFactory._instance = DockerRuntime(config)
            await DockerRuntimeFactory._instance.initialize()
        return DockerRuntimeFactory._instance

    @staticmethod
    async def create_new_instance(config: Optional[SandboxConfig] = None) -> "DockerRuntime":
        """
        创建新的 Docker 运行时实例

        Args:
            config: 配置

        Returns:
            DockerRuntime: 运行时实例
        """
        runtime = DockerRuntime(config)
        await runtime.initialize()
        return runtime
