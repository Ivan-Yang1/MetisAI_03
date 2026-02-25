"""
智能体配置验证模块
实现智能体配置的验证和处理
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import ValidationError

from backend.agents.base import AgentConfig, AgentState, BaseAgent
from backend.agents.codeact import CodeActAgent, CodeActAgentConfig
from backend.controllers.agent_controller import get_agent_controller
from backend.models.agent import AgentType
from backend.services.db_service import DatabaseService

logger = logging.getLogger(__name__)


class AgentConfigValidator:
    """
    智能体配置验证器
    负责验证和处理智能体配置
    """

    @staticmethod
    def validate_config(
        config: Union[Dict[str, Any], AgentConfig],
        agent_type: AgentType = AgentType.CHAT,
    ) -> Tuple[bool, Optional[Union[Dict[str, Any], AgentConfig]], List[str]]:
        """
        验证智能体配置

        Args:
            config: 配置字典或 AgentConfig 实例
            agent_type: 智能体类型

        Returns:
            Tuple[bool, Optional[Dict], List[str]]:
                (是否有效, 验证后的配置, 错误信息)
        """
        errors = []

        try:
            if isinstance(config, dict):
                if agent_type == AgentType.CODEACT:
                    validated_config = CodeActAgentConfig(**config)
                else:
                    validated_config = AgentConfig(**config)
            elif isinstance(config, AgentConfig):
                validated_config = config
            else:
                errors.append("配置类型无效")
                return False, None, errors

            return True, validated_config, errors

        except ValidationError as e:
            errors.extend([str(err) for err in e.errors()])
            return False, None, errors

    @staticmethod
    def validate_config_dict(
        config_dict: Dict[str, Any],
        agent_type: AgentType = AgentType.CHAT,
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        验证配置字典并返回字典格式

        Args:
            config_dict: 配置字典
            agent_type: 智能体类型

        Returns:
            Tuple[bool, Optional[Dict], List[str]]:
                (是否有效, 验证后的配置, 错误信息)
        """
        valid, config, errors = AgentConfigValidator.validate_config(
            config_dict, agent_type
        )

        if valid and config:
            return True, config.dict(), errors
        else:
            return False, None, errors

    @staticmethod
    def validate_required_fields(
        config: Dict[str, Any], required_fields: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        验证配置是否包含所有必填字段

        Args:
            config: 配置字典
            required_fields: 必填字段列表

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息)
        """
        errors = []

        for field in required_fields:
            if field not in config:
                errors.append(f"配置缺少必填字段 '{field}'")
            elif config.get(field) is None or config.get(field) == "":
                errors.append(f"字段 '{field}' 不能为空")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_config(
        config: Dict[str, Any], agent_type: AgentType = AgentType.CHAT
    ) -> Dict[str, Any]:
        """
        清洗配置，移除不允许的字段

        Args:
            config: 配置字典
            agent_type: 智能体类型

        Returns:
            Dict[str, Any]: 清洗后的配置
        """
        allowed_fields = set()

        if agent_type == AgentType.CODEACT:
            allowed_fields = {
                "model",
                "temperature",
                "max_tokens",
                "timeout",
                "enable_code_execution",
                "code_language",
                "max_code_lines",
                "sandbox_timeout",
                "enable_auto_retry",
            }
        else:
            allowed_fields = {
                "model",
                "temperature",
                "max_tokens",
                "timeout",
            }

        sanitized_config = {}

        for key, value in config.items():
            if key in allowed_fields:
                sanitized_config[key] = value

        return sanitized_config

    @staticmethod
    def merge_configs(
        base_config: Dict[str, Any],
        user_config: Dict[str, Any],
        agent_type: AgentType = AgentType.CHAT,
    ) -> Dict[str, Any]:
        """
        合并基础配置和用户配置

        Args:
            base_config: 基础配置
            user_config: 用户配置
            agent_type: 智能体类型

        Returns:
            Dict[str, Any]: 合并后的配置
        """
        # 先清洗用户配置，移除不允许的字段
        sanitized_user_config = AgentConfigValidator.sanitize_config(
            user_config, agent_type
        )

        # 合并配置
        merged_config = {**base_config, **sanitized_user_config}

        return merged_config


class AgentValidationService:
    """
    智能体验证服务
    负责智能体实例和配置的验证
    """

    @staticmethod
    async def validate_agent_instance(agent: BaseAgent) -> Tuple[bool, List[str]]:
        """
        验证智能体实例

        Args:
            agent: 智能体实例

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息)
        """
        errors = []

        if not hasattr(agent, "agent_id") or agent.agent_id <= 0:
            errors.append("智能体 ID 无效")

        if not hasattr(agent, "name") or len(agent.name.strip()) == 0:
            errors.append("智能体名称无效")

        if not hasattr(agent, "state") or not isinstance(agent.state, AgentState):
            errors.append("智能体状态无效")

        if hasattr(agent, "config"):
            config_valid, _, config_errors = AgentConfigValidator.validate_config(
                agent.config, agent.type
            )

            if not config_valid:
                errors.extend(config_errors)

        return len(errors) == 0, errors

    @staticmethod
    async def validate_agent_from_db(agent: Agent) -> Tuple[bool, List[str]]:
        """
        验证数据库中的智能体记录

        Args:
            agent: 数据库中的智能体记录

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息)
        """
        errors = []

        if not hasattr(agent, "id") or agent.id <= 0:
            errors.append("智能体 ID 无效")

        if not hasattr(agent, "name") or len(agent.name.strip()) == 0:
            errors.append("智能体名称无效")

        if agent.config:
            valid, _, config_errors = AgentConfigValidator.validate_config(
                agent.config, agent.type
            )

            if not valid:
                errors.extend(config_errors)

        return len(errors) == 0, errors

    @staticmethod
    async def validate_all_agents() -> Dict[int, Tuple[bool, List[str]]]:
        """
        验证所有智能体

        Returns:
            Dict[int, Tuple[bool, List[str]]]: 智能体验证结果
        """
        agents = await DatabaseService.get_all_agents()
        results = {}

        for agent in agents:
            valid, errors = await AgentValidationService.validate_agent_from_db(
                agent
            )
            results[agent.id] = (valid, errors)

        return results

    @staticmethod
    async def validate_agent_controller() -> Tuple[bool, List[str]]:
        """
        验证智能体控制器状态

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息)
        """
        errors = []

        try:
            controller = await get_agent_controller()
            agents = await controller.get_all_agents()

            for agent in agents:
                valid, agent_errors = await AgentValidationService.validate_agent_instance(
                    agent
                )
                if not valid:
                    errors.extend(
                        [f"智能体 {agent.agent_id} 验证失败: {err}" for err in agent_errors]
                    )

            if len(agents) == 0:
                errors.append("控制器中没有智能体")

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(str(e))
            return False, errors


class ConfigurationManager:
    """
    配置管理类
    负责配置的加载、保存和更新
    """

    @staticmethod
    async def load_default_config(agent_type: AgentType = AgentType.CHAT) -> Dict[str, Any]:
        """
        加载默认配置

        Args:
            agent_type: 智能体类型

        Returns:
            Dict[str, Any]: 默认配置
        """
        if agent_type == AgentType.CODEACT:
            return CodeActAgentConfig().dict()
        else:
            return AgentConfig().dict()

    @staticmethod
    async def save_config(agent_id: int, config: Dict[str, Any]) -> bool:
        """
        保存智能体配置

        Args:
            agent_id: 智能体 ID
            config: 配置字典

        Returns:
            bool: 是否成功
        """
        controller = await get_agent_controller()
        agent = await controller.get_agent(agent_id)

        if not agent:
            return False

        valid, validated_config, errors = AgentConfigValidator.validate_config(
            config, agent.type
        )

        if not valid:
            return False

        await DatabaseService.update_agent(agent_id, config=validated_config.dict())

        return True

    @staticmethod
    async def update_config(
        agent_id: int,
        config_update: Dict[str, Any],
        merge: bool = True,
    ) -> bool:
        """
        更新智能体配置

        Args:
            agent_id: 智能体 ID
            config_update: 更新的配置
            merge: 是否合并配置

        Returns:
            bool: 是否成功
        """
        controller = await get_agent_controller()
        agent = await controller.get_agent(agent_id)

        if not agent:
            return False

        if merge:
            existing_config = await ConfigurationManager.load_config(agent_id)
            updated_config = {**existing_config, **config_update}
        else:
            updated_config = config_update

        valid, validated_config, errors = AgentConfigValidator.validate_config(
            updated_config, agent.type
        )

        if not valid:
            return False

        await DatabaseService.update_agent(agent_id, config=validated_config.dict())
        return True

    @staticmethod
    async def load_config(agent_id: int) -> Optional[Dict[str, Any]]:
        """
        加载智能体配置

        Args:
            agent_id: 智能体 ID

        Returns:
            Optional[Dict[str, Any]]: 配置字典
        """
        agent = await DatabaseService.get_agent(agent_id)

        if not agent:
            return None

        return agent.config

    @staticmethod
    async def validate_and_load_config(
        agent_id: int,
    ) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        验证并加载智能体配置

        Args:
            agent_id: 智能体 ID

        Returns:
            Tuple[bool, Optional[Dict], List[str]]:
                (是否有效, 配置, 错误信息)
        """
        config = await ConfigurationManager.load_config(agent_id)

        if not config:
            return False, None, ["配置未找到"]

        agent = await DatabaseService.get_agent(agent_id)
        valid, _, errors = AgentConfigValidator.validate_config(config, agent.type)

        return valid, config, errors


def get_agent_config_validator() -> AgentConfigValidator:
    """
    获取配置验证器实例

    Returns:
        AgentConfigValidator: 验证器实例
    """
    return AgentConfigValidator()
