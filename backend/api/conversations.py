"""
会话管理 API
负责会话的创建、获取、更新和删除
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from services.conversation_manager import get_conversation_manager
from models.conversation import Conversation, ConversationStatus
from models.message import Message, MessageRole

router = APIRouter(prefix="/api/conversations", tags=["会话管理"])


class ConversationCreate(BaseModel):
    """创建会话请求模型"""

    user_id: str
    agent_id: Optional[int] = None
    title: Optional[str] = None
    metadata: Optional[dict] = None


class ConversationUpdate(BaseModel):
    """更新会话请求模型"""

    title: Optional[str] = None
    metadata: Optional[dict] = None
    status: Optional[ConversationStatus] = None


class ConversationResponse(BaseModel):
    """会话响应模型"""

    id: int
    user_id: str
    agent_id: Optional[int] = None
    title: Optional[str] = None
    status: ConversationStatus
    metadata: Optional[dict] = None

    class Config:
        """Pydantic 配置"""

        from_attributes = True


class MessageCreate(BaseModel):
    """创建消息请求模型"""

    role: MessageRole
    content: str
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    """消息响应模型"""

    id: int
    conversation_id: int
    role: MessageRole
    content: str
    metadata: Optional[dict] = None

    class Config:
        """Pydantic 配置"""

        from_attributes = True


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    manager=Depends(get_conversation_manager),
):
    """获取所有会话列表"""
    try:
        conversations = await manager.get_all_conversations()
        return [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                agent_id=conv.agent_id,
                title=conv.title,
                status=conv.status,
                metadata=conv.metadata,
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    manager=Depends(get_conversation_manager),
):
    """获取会话详情"""
    try:
        conversation = await manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            title=conversation.title,
            status=conversation.status,
            metadata=conversation.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话详情失败: {str(e)}"
        )


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    manager=Depends(get_conversation_manager),
):
    """创建新会话"""
    try:
        conversation = await manager.create_conversation(
            user_id=conversation_data.user_id,
            agent_id=conversation_data.agent_id,
            title=conversation_data.title,
            metadata=conversation_data.metadata,
        )
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            agent_id=conversation.agent_id,
            title=conversation.title,
            status=conversation.status,
            metadata=conversation.metadata,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    manager=Depends(get_conversation_manager),
):
    """更新会话信息"""
    try:
        # 获取现有会话
        existing_conv = await manager.get_conversation(conversation_id)
        if not existing_conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        # 更新会话
        update_data = conversation_data.dict(exclude_unset=True)
        await manager.update_conversation(conversation_id, **update_data)

        # 重新获取更新后的会话
        updated_conv = await manager.get_conversation(conversation_id)
        return ConversationResponse(
            id=updated_conv.id,
            user_id=updated_conv.user_id,
            agent_id=updated_conv.agent_id,
            title=updated_conv.title,
            status=updated_conv.status,
            metadata=updated_conv.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新会话失败: {str(e)}"
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    manager=Depends(get_conversation_manager),
):
    """删除会话"""
    try:
        success = await manager.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话失败: {str(e)}"
        )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    manager=Depends(get_conversation_manager),
):
    """获取会话消息"""
    try:
        conversation = await manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        messages = await manager.get_conversation_messages(conversation_id)
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                metadata=msg.metadata,
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话消息失败: {str(e)}"
        )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_conversation_message(
    conversation_id: int,
    message_data: MessageCreate,
    manager=Depends(get_conversation_manager),
):
    """创建会话消息"""
    try:
        conversation = await manager.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        message = await manager.add_message(
            conversation_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata,
        )

        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            metadata=message.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话消息失败: {str(e)}"
        )
