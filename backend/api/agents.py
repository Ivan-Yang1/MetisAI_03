"""
智能体管理 API
负责智能体的创建、获取、更新、删除和状态管理
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from typing import List, Optional
import traceback

from controllers.agent_controller import get_agent_controller
from models.agent import Agent, AgentStatus, AgentType

router = APIRouter(prefix="/api/agents", tags=["智能体管理"])


class AgentCreate(BaseModel):
    """创建智能体请求模型"""

    name: str
    type: AgentType
    description: Optional[str] = None
    config: Optional[dict] = None


class AgentUpdate(BaseModel):
    """更新智能体请求模型"""

    name: Optional[str] = None
    type: Optional[AgentType] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    status: Optional[AgentStatus] = None


class AgentResponse(BaseModel):
    """智能体响应模型"""

    id: int
    name: str
    type: AgentType
    status: str
    description: Optional[str] = None
    config: Optional[dict] = None

    @validator("config", pre=True)
    def extract_config(cls, v, **kwargs):
        """从配置对象中提取字典"""
        if hasattr(v, "dict"):
            return v.dict()
        elif hasattr(v, "model_dump"):
            return v.model_dump()
        return v

    class Config:
        """Pydantic 配置"""

        from_attributes = True

    @validator("id", pre=True)
    def extract_agent_id(cls, v, values, **kwargs):
        """从智能体实例中提取 id 属性"""
        if isinstance(v, dict):
            return v.get("agent_id", v.get("id"))
        elif hasattr(v, "agent_id"):
            return v.agent_id
        elif hasattr(v, "id"):
            return v.id
        return v


class AgentStatusResponse(BaseModel):
    """智能体状态响应模型"""

    id: int
    status: AgentStatus


@router.get("/")
async def list_agents(
    controller=Depends(get_agent_controller),
):
    """获取所有智能体列表"""
    try:
        agents = await controller.get_all_agents()
        result = []
        for agent in agents:
            # 使用 state_dict 获取智能体信息
            state_dict = agent.state_dict
            result.append({
                "id": state_dict["agent_id"],
                "name": state_dict["name"],
                "type": state_dict["type"],
                "status": state_dict["state"],
                "description": agent.description or "Description not available",
                "config": state_dict["config"],
            })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取智能体列表失败: {str(e)}\nStack trace: {str(traceback.format_exc())}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    controller=Depends(get_agent_controller),
):
    """根据 ID 获取智能体详情"""
    try:
        agent = await controller.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            status=agent.status,
            description=agent.description,
            config=agent.config,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取智能体详情失败: {str(e)}"
        )


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    controller=Depends(get_agent_controller),
):
    """创建新智能体"""
    try:
        agent = await controller.create_agent(
            name=agent_data.name,
            type=agent_data.type,
            description=agent_data.description,
            config=agent_data.config,
        )
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            status=agent.status,
            description=agent.description,
            config=agent.config,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建智能体失败: {str(e)}"
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    controller=Depends(get_agent_controller),
):
    """更新智能体信息"""
    try:
        # 获取现有智能体
        existing_agent = await controller.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )

        # 更新智能体
        update_data = agent_data.dict(exclude_unset=True)
        await controller.update_agent(agent_id, **update_data)

        # 重新获取更新后的智能体
        updated_agent = await controller.get_agent(agent_id)
        return AgentResponse(
            id=updated_agent.id,
            name=updated_agent.name,
            type=updated_agent.type,
            status=updated_agent.status,
            description=updated_agent.description,
            config=updated_agent.config,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新智能体失败: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    controller=Depends(get_agent_controller),
):
    """删除智能体"""
    try:
        success = await controller.destroy_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除智能体失败: {str(e)}"
        )


@router.post("/{agent_id}/start", response_model=AgentStatusResponse)
async def start_agent(
    agent_id: int,
    controller=Depends(get_agent_controller),
):
    """启动智能体"""
    try:
        agent = await controller.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )

        await controller.run_agent(agent_id, "启动智能体")
        return AgentStatusResponse(id=agent_id, status=agent.status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动智能体失败: {str(e)}"
        )


@router.post("/{agent_id}/stop", response_model=AgentStatusResponse)
async def stop_agent(
    agent_id: int,
    controller=Depends(get_agent_controller),
):
    """停止智能体"""
    try:
        agent = await controller.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )

        await controller.stop_agent(agent_id)
        return AgentStatusResponse(id=agent_id, status=agent.status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止智能体失败: {str(e)}"
        )


@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_id: int,
    controller=Depends(get_agent_controller),
):
    """获取智能体状态"""
    try:
        agent = await controller.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )

        return AgentStatusResponse(id=agent_id, status=agent.status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取智能体状态失败: {str(e)}"
        )
