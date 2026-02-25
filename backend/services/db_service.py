"""
数据库操作服务模块
提供便捷的数据库操作方法
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from models.agent import Agent, AgentType, AgentStatus
from models.conversation import Conversation, ConversationStatus
from models.message import Message, MessageRole


class DatabaseService:
    """数据库操作服务类"""

    @classmethod
    async def create_agent(
        cls,
        name: str,
        type: AgentType = AgentType.CODEACT,
        description: str = None,
        config: dict = None,
        status: AgentStatus = AgentStatus.ACTIVE,
    ) -> Agent:
        """创建智能体"""
        async for session in get_db_session():
            try:
                agent = Agent(
                    name=name,
                    type=type,
                    description=description,
                    config=config,
                    status=status,
                )
                session.add(agent)
                await session.commit()
                await session.refresh(agent)
                return agent
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def get_agent(cls, agent_id: int) -> Optional[Agent]:
        """根据 ID 获取智能体"""
        async for session in get_db_session():
            result = await session.execute(select(Agent).where(Agent.id == agent_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all_agents(cls) -> List[Agent]:
        """获取所有智能体"""
        async for session in get_db_session():
            result = await session.execute(select(Agent))
            return list(result.scalars().all())

    @classmethod
    async def update_agent(cls, agent_id: int, **kwargs) -> Optional[Agent]:
        """更新智能体"""
        async for session in get_db_session():
            try:
                agent = await session.get(Agent, agent_id)
                if agent:
                    for key, value in kwargs.items():
                        if hasattr(agent, key):
                            setattr(agent, key, value)
                    await session.commit()
                    await session.refresh(agent)
                return agent
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def delete_agent(cls, agent_id: int) -> bool:
        """删除智能体"""
        async for session in get_db_session():
            try:
                agent = await session.get(Agent, agent_id)
                if agent:
                    await session.delete(agent)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def create_conversation(
        cls,
        conversation: Conversation = None,
        user_id: str = None,
        agent_id: int = None,
        title: str = None,
        status: ConversationStatus = ConversationStatus.ACTIVE,
        metadata: dict = None,
    ) -> Conversation:
        """创建会话"""
        async for session in get_db_session():
            try:
                if conversation is None:
                    conversation = Conversation(
                        user_id=user_id,
                        agent_id=agent_id,
                        title=title,
                        status=status,
                        metadata_=metadata,
                    )
                session.add(conversation)
                await session.commit()
                await session.refresh(conversation)
                return conversation
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def get_active_conversations(cls) -> List[Conversation]:
        """获取所有活动状态的会话"""
        async for session in get_db_session():
            result = await session.execute(
                select(Conversation).where(Conversation.status == ConversationStatus.ACTIVE)
            )
            return list(result.scalars().all())

    @classmethod
    async def get_conversation(cls, conversation_id: int) -> Optional[Conversation]:
        """根据 ID 获取会话"""
        async for session in get_db_session():
            result = await session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            return result.scalar_one_or_none()

    @classmethod
    async def get_conversations_by_user(cls, user_id: str) -> List[Conversation]:
        """根据用户 ID 获取会话列表"""
        async for session in get_db_session():
            result = await session.execute(
                select(Conversation).where(Conversation.user_id == user_id)
            )
            return list(result.scalars().all())

    @classmethod
    async def update_conversation(
        cls, conversation_id: int, **kwargs
    ) -> Optional[Conversation]:
        """更新会话"""
        async for session in get_db_session():
            try:
                conversation = await session.get(Conversation, conversation_id)
                if conversation:
                    for key, value in kwargs.items():
                        if hasattr(conversation, key):
                            setattr(conversation, key, value)
                    await session.commit()
                    await session.refresh(conversation)
                return conversation
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def delete_conversation(cls, conversation_id: int) -> bool:
        """删除会话"""
        async for session in get_db_session():
            try:
                conversation = await session.get(Conversation, conversation_id)
                if conversation:
                    await session.delete(conversation)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def create_message(
        cls,
        message: Message = None,
        conversation_id: int = None,
        role: MessageRole = None,
        content: str = None,
        metadata: dict = None,
    ) -> Message:
        """创建消息"""
        async for session in get_db_session():
            try:
                if message is None:
                    message = Message(
                        conversation_id=conversation_id,
                        role=role,
                        content=content,
                        metadata_=metadata,
                    )
                session.add(message)
                await session.commit()
                await session.refresh(message)
                return message
            except Exception as e:
                await session.rollback()
                raise e

    @classmethod
    async def get_message(cls, message_id: int) -> Optional[Message]:
        """根据 ID 获取消息"""
        async for session in get_db_session():
            result = await session.execute(select(Message).where(Message.id == message_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_messages_by_conversation(
        cls, conversation_id: int
    ) -> List[Message]:
        """根据会话 ID 获取消息列表"""
        async for session in get_db_session():
            result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            return list(result.scalars().all())

    @classmethod
    async def delete_message(cls, message_id: int) -> bool:
        """删除消息"""
        async for session in get_db_session():
            try:
                message = await session.get(Message, message_id)
                if message:
                    await session.delete(message)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                await session.rollback()
                raise e
