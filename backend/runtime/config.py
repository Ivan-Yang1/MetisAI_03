"""
沙箱配置系统模块
负责配置和管理沙箱执行环境的参数
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class SandboxType(str, Enum):
    """沙箱类型枚举"""

    DOCKER = "docker"
    LOCAL = "local"
    KUBERNETES = "kubernetes"
    REMOTE = "remote"


class ResourceLimits(BaseModel):
    """资源限制配置"""

    cpu: str = Field(default="1", description="CPU 限制（例如 '1' 表示 1 核）")
    memory: str = Field(default="1G", description="内存限制（例如 '1G' 表示 1 GB）")
    disk: str = Field(default="10G", description="磁盘限制（例如 '10G' 表示 10 GB）")
    timeout: int = Field(default=300, description="执行超时时间（秒）")
    max_processes: int = Field(default=10, description="最大进程数")

    @validator("cpu")
    def validate_cpu(cls, v: str) -> str:
        """验证 CPU 限制格式"""
        if not (v.isdigit() or (v.replace(".", "", 1).isdigit() and v.count(".") < 2)):
            raise ValueError("CPU 限制必须是数字格式（例如 '1' 或 '0.5'）")
        return v

    @validator("memory")
    def validate_memory(cls, v: str) -> str:
        """验证内存限制格式"""
        valid_suffixes = ["K", "M", "G", "T"]
        if len(v) < 2:
            raise ValueError("内存限制格式无效（需要包含单位，如 '1G'）")
        if v[-1] not in valid_suffixes and not v.isdigit():
            raise ValueError(f"内存限制必须以 {', '.join(valid_suffixes)} 结尾或纯数字（字节）")
        return v

    @validator("disk")
    def validate_disk(cls, v: str) -> str:
        """验证磁盘限制格式"""
        valid_suffixes = ["K", "M", "G", "T"]
        if len(v) < 2:
            raise ValueError("磁盘限制格式无效（需要包含单位，如 '10G'）")
        if v[-1] not in valid_suffixes and not v.isdigit():
            raise ValueError(f"磁盘限制必须以 {', '.join(valid_suffixes)} 结尾或纯数字（字节）")
        return v


class DockerConfig(BaseModel):
    """Docker 配置"""

    image: str = Field(default="python:3.12-slim", description="Docker 镜像")
    network_mode: str = Field(default="bridge", description="网络模式")
    privileged: bool = Field(default=False, description="是否以特权模式运行")
    volumes: Dict[str, str] = Field(default_factory=dict, description="挂载卷配置")
    environment: Dict[str, str] = Field(default_factory=dict, description="环境变量")
    entrypoint: Optional[str] = Field(default=None, description="入口点")
    command: Optional[str] = Field(default=None, description="命令")


class KubernetesConfig(BaseModel):
    """Kubernetes 配置"""

    namespace: str = Field(default="openhands", description="Kubernetes 命名空间")
    service_account: str = Field(default="openhands", description="服务账户")
    node_selector: Dict[str, str] = Field(default_factory=dict, description="节点选择器")
    tolerations: List[Dict[str, Any]] = Field(default_factory=list, description="容忍度")


class SandboxConfig(BaseModel):
    """沙箱配置"""

    sandbox_type: SandboxType = Field(default=SandboxType.DOCKER, description="沙箱类型")
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits, description="资源限制")
    docker_config: DockerConfig = Field(default_factory=DockerConfig, description="Docker 配置")
    kubernetes_config: KubernetesConfig = Field(default_factory=KubernetesConfig, description="Kubernetes 配置")
    working_dir: str = Field(default="/workspace", description="工作目录")
    cleanup: bool = Field(default=True, description="是否在完成后清理资源")
    enable_monitoring: bool = Field(default=True, description="是否启用监控")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    @validator("sandbox_type")
    def validate_sandbox_type(cls, v: SandboxType) -> SandboxType:
        """验证沙箱类型"""
        if v not in SandboxType:
            raise ValueError(f"不支持的沙箱类型: {v}")
        return v


@dataclass
class SandboxRuntimeOptions:
    """沙箱运行时选项"""

    sandbox_type: SandboxType = SandboxType.DOCKER
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    docker_config: DockerConfig = field(default_factory=DockerConfig)
    kubernetes_config: KubernetesConfig = field(default_factory=KubernetesConfig)
    working_dir: str = "/workspace"
    cleanup: bool = True
    enable_monitoring: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "sandbox_type": self.sandbox_type.value,
            "resource_limits": self.resource_limits.dict(),
            "docker_config": self.docker_config.dict(),
            "kubernetes_config": self.kubernetes_config.dict(),
            "working_dir": self.working_dir,
            "cleanup": self.cleanup,
            "enable_monitoring": self.enable_monitoring,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SandboxRuntimeOptions":
        """从字典创建实例"""
        return cls(
            sandbox_type=SandboxType(data.get("sandbox_type", "docker")),
            resource_limits=ResourceLimits(**data.get("resource_limits", {})),
            docker_config=DockerConfig(**data.get("docker_config", {})),
            kubernetes_config=KubernetesConfig(**data.get("kubernetes_config", {})),
            working_dir=data.get("working_dir", "/workspace"),
            cleanup=data.get("cleanup", True),
            enable_monitoring=data.get("enable_monitoring", True),
            metadata=data.get("metadata", {}),
        )


class SandboxConfigValidator:
    """沙箱配置验证器"""

    @staticmethod
    def validate_config(config: Union[Dict[str, Any], SandboxConfig]) -> SandboxConfig:
        """验证和转换配置"""
        if isinstance(config, dict):
            return SandboxConfig(**config)
        elif isinstance(config, SandboxConfig):
            return config
        else:
            raise ValueError(f"不支持的配置类型: {type(config)}")

    @staticmethod
    def validate_options(options: Union[Dict[str, Any], SandboxRuntimeOptions]) -> SandboxRuntimeOptions:
        """验证和转换运行时选项"""
        if isinstance(options, dict):
            return SandboxRuntimeOptions.from_dict(options)
        elif isinstance(options, SandboxRuntimeOptions):
            return options
        else:
            raise ValueError(f"不支持的选项类型: {type(options)}")

    @staticmethod
    def merge_configs(base: SandboxConfig, override: Dict[str, Any]) -> SandboxConfig:
        """合并配置"""
        config_dict = base.dict()
        config_dict.update(override)
        return SandboxConfig(**config_dict)


class SandboxConfigManager:
    """沙箱配置管理器"""

    _default_config: Optional[SandboxConfig] = None

    @classmethod
    def get_default_config(cls) -> SandboxConfig:
        """获取默认配置"""
        if cls._default_config is None:
            cls._default_config = SandboxConfig()
        return cls._default_config

    @classmethod
    def set_default_config(cls, config: Union[Dict[str, Any], SandboxConfig]) -> None:
        """设置默认配置"""
        cls._default_config = SandboxConfigValidator.validate_config(config)
        logger.info(f"沙箱默认配置已更新: {cls._default_config.sandbox_type}")

    @classmethod
    def create_config(cls, **kwargs) -> SandboxConfig:
        """创建新配置"""
        config = SandboxConfig(**kwargs)
        logger.debug(f"创建新的沙箱配置: {config.sandbox_type}")
        return config

    @classmethod
    def validate_and_create(cls, config_data: Dict[str, Any]) -> SandboxConfig:
        """验证并创建配置"""
        try:
            config = SandboxConfig(**config_data)
            logger.debug(f"配置验证成功: {config.sandbox_type}")
            return config
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            raise


# 默认配置
DEFAULT_CONFIG = SandboxConfigManager.get_default_config()

# 常用配置模板
DOCKER_CONFIG = SandboxConfig(
    sandbox_type=SandboxType.DOCKER,
    resource_limits=ResourceLimits(cpu="2", memory="2G", disk="20G", timeout=600),
    docker_config=DockerConfig(image="python:3.12-slim"),
)

LOCAL_CONFIG = SandboxConfig(
    sandbox_type=SandboxType.LOCAL,
    resource_limits=ResourceLimits(cpu="1", memory="512M", disk="5G", timeout=120),
)

KUBERNETES_CONFIG = SandboxConfig(
    sandbox_type=SandboxType.KUBERNETES,
    resource_limits=ResourceLimits(cpu="4", memory="4G", disk="50G", timeout=1800),
    kubernetes_config=KubernetesConfig(namespace="openhands", service_account="openhands"),
)
