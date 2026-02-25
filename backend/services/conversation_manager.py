"""
会话管理系统模块
实现会话创建、管理和资源清理
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from models.conversation import Conversation, ConversationStatus
from models.message import Message, MessageRole
from services.db_service import DatabaseService

logger = logging.getLogger(__name__)


class Session:
    """
    会话类
    表示用户与智能体之间的一次对话会话
    """

    def __init__(
        self,
        session_id: int,
        user_id: str,
        agent_id: Optional[int] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化会话

        Args:
            session_id: 会话 ID
            user_id: 用户 ID
            agent_id: 智能体 ID
            title: 会话标题
            metadata: 会话元数据
        """
        self.session_id = session_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.title = title
        self.metadata = metadata or {}
        self.status = ConversationStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self._messages: List[Message] = []
        self._timeout_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    @property
    def is_active(self) -> bool:
        """判断会话是否处于活动状态"""
        return self.status == ConversationStatus.ACTIVE

    @property
    def message_count(self) -> int:
        """获取消息数量"""
        return len(self._messages)

    @property
    def session_dict(self) -> Dict[str, Any]:
        """返回会话的字典表示"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "title": self.title,
            "status": self.status.value,
            "metadata": self.metadata,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    async def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        添加消息到会话

        Args:
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据

        Returns:
            Message: 消息实例
        """
        async with self._lock:
            message = Message(
                conversation_id=self.session_id,
                role=role,
                content=content,
                metadata_=metadata,
            )

            # 保存到数据库
            await DatabaseService.create_message(message)
            self._messages.append(message)
            self.updated_at = datetime.utcnow()

            logger.debug(f"消息已添加到会话: {self.session_id}, 角色: {role}")
            return message

    async def get_messages(self) -> List[Message]:
        """获取会话的所有消息"""
        async with self._lock:
            if not self._messages:
                # 从数据库加载消息
                self._messages = await DatabaseService.get_messages_by_conversation(self.session_id)
            return list(self._messages)

    async def complete(self) -> None:
        """完成会话"""
        async with self._lock:
            self.status = ConversationStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

            # 更新数据库中的会话状态
            await DatabaseService.update_conversation(
                self.session_id,
                status=ConversationStatus.COMPLETED,
                completed_at=self.completed_at,
            )

            # 取消超时任务
            if self._timeout_task:
                self._timeout_task.cancel()

            logger.info(f"会话已完成: {self.session_id}")

    async def cancel(self) -> None:
        """取消会话"""
        async with self._lock:
            self.status = ConversationStatus.CANCELED
            self.completed_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

            # 更新数据库中的会话状态
            await DatabaseService.update_conversation(
                self.session_id,
                status=ConversationStatus.CANCELED,
                completed_at=self.completed_at,
            )

            # 取消超时任务
            if self._timeout_task:
                self._timeout_task.cancel()

            logger.info(f"会话已取消: {self.session_id}")

    async def set_timeout(self, timeout: float = 3600.0) -> None:
        """
        设置会话超时时间

        Args:
            timeout: 超时时间（秒），默认 1 小时
        """
        # 取消之前的超时任务
        if self._timeout_task:
            self._timeout_task.cancel()

        async def timeout_handler():
            await asyncio.sleep(timeout)
            if self.is_active:
                logger.warning(f"会话超时，自动完成: {self.session_id}")
                await self.complete()

        self._timeout_task = asyncio.create_task(timeout_handler())
        logger.debug(f"会话超时已设置: {self.session_id}, 超时时间: {timeout} 秒")

    async def cleanup(self) -> None:
        """清理会话资源"""
        if self._timeout_task:
            self._timeout_task.cancel()
        self._messages.clear()
        logger.debug(f"会话资源已清理: {self.session_id}")


class ConversationManager:
    """
    会话管理器
    负责会话的创建、管理和资源清理
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化会话管理器"""
        if ConversationManager._initialized:
            return
        ConversationManager._initialized = True

        self._sessions: Dict[int, Session] = {}
        self._session_lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._timeout_duration: float = 3600.0  # 默认超时时间（秒）

    async def initialize(self, timeout_duration: float = 3600.0) -> None:
        """
        初始化会话管理器

        Args:
            timeout_duration: 会话超时时间（秒）
        """
        logger.info("正在初始化会话管理器...")

        self._timeout_duration = timeout_duration

        # 从数据库加载已有的会话
        conversations = await DatabaseService.get_active_conversations()

        for conversation in conversations:
            session = Session(
                session_id=conversation.id,
                user_id=conversation.user_id,
                agent_id=conversation.agent_id,
                title=conversation.title,
                metadata=conversation.metadata_,
            )
            session.status = conversation.status
            session.created_at = conversation.created_at
            session.updated_at = conversation.updated_at
            session.completed_at = conversation.completed_at

            self._sessions[conversation.id] = session

            # 为活动会话设置超时
            if session.is_active:
                await session.set_timeout(self._timeout_duration)

        logger.info(f"会话管理器已初始化，加载了 {len(self._sessions)} 个会话")

        # 启动定期清理任务
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def _periodic_cleanup(self) -> None:
        """定期清理超时的会话"""
        while True:
            try:
                await asyncio.sleep(300)  # 每 5 分钟检查一次

                current_time = datetime.utcnow()
                expired_sessions: List[int] = []

                async with self._session_lock:
                    for session_id, session in self._sessions.items():
                        if session.is_active:
                            # 检查会话是否超时
                            time_since_update = (current_time - session.updated_at).total_seconds()
                            if time_since_update > self._timeout_duration:
                                expired_sessions.append(session_id)

                # 清理超时的会话
                for session_id in expired_sessions:
                    await self.complete_session(session_id)
                    logger.info(f"会话已超时并自动完成: {session_id}")

            except Exception as e:
                logger.error(f"定期清理任务出错: {e}")
                continue

    async def create_session(
        self,
        user_id: str,
        agent_id: Optional[int] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        创建新会话

        Args:
            user_id: 用户 ID
            agent_id: 智能体 ID（可选）
            title: 会话标题（可选）
            metadata: 会话元数据（可选）

        Returns:
            Session: 会话实例
        """
        async with self._session_lock:
            # 在数据库中创建会话
            conversation = Conversation(
                user_id=user_id,
                agent_id=agent_id,
                title=title,
                metadata_=metadata,
            )
            conversation = await DatabaseService.create_conversation(conversation)

            # 创建会话实例
            session = Session(
                session_id=conversation.id,
                user_id=user_id,
                agent_id=agent_id,
                title=title,
                metadata=metadata,
            )

            self._sessions[conversation.id] = session

            # 设置超时
            await session.set_timeout(self._timeout_duration)

            logger.info(f"会话已创建: {session.session_id}, 用户: {user_id}")
            return session

    async def get_session(self, session_id: int) -> Optional[Session]:
        """
        获取会话实例

        Args:
            session_id: 会话 ID

        Returns:
            Optional[Session]: 会话实例
        """
        async with self._session_lock:
            return self._sessions.get(session_id)

    async def get_sessions_by_user(self, user_id: str) -> List[Session]:
        """
        获取用户的所有会话

        Args:
            user_id: 用户 ID

        Returns:
            List[Session]: 会话列表
        """
        async with self._session_lock:
            return [
                session for session in self._sessions.values()
                if session.user_id == user_id
            ]

    async def get_active_sessions(self) -> List[Session]:
        """获取所有活动的会话"""
        async with self._session_lock:
            return [
                session for session in self._sessions.values()
                if session.is_active
            ]

    async def complete_session(self, session_id: int) -> bool:
        """
        完成会话

        Args:
            session_id: 会话 ID

        Returns:
            bool: 是否成功完成
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_active:
                return False

            await session.complete()
            logger.debug(f"会话已完成: {session_id}")
            return True

    async def cancel_session(self, session_id: int) -> bool:
        """
        取消会话

        Args:
            session_id: 会话 ID

        Returns:
            bool: 是否成功取消
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_active:
                return False

            await session.cancel()
            logger.debug(f"会话已取消: {session_id}")
            return True

    async def delete_session(self, session_id: int) -> bool:
        """
        删除会话

        Args:
            session_id: 会话 ID

        Returns:
            bool: 是否成功删除
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # 清理资源
            await session.cleanup()

            # 删除从内存和数据库
            del self._sessions[session_id]
            await DatabaseService.delete_conversation(session_id)

            logger.info(f"会话已删除: {session_id}")
            return True

    async def add_message_to_session(
        self,
        session_id: int,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Message]:
        """
        向会话添加消息

        Args:
            session_id: 会话 ID
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据

        Returns:
            Optional[Message]: 消息实例
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_active:
                logger.error(f"会话不可用: {session_id}")
                return None

            message = await session.add_message(role, content, metadata)

            # 重置超时
            await session.set_timeout(self._timeout_duration)

            return message

    async def get_session_messages(self, session_id: int) -> List[Message]:
        """
        获取会话的所有消息

        Args:
            session_id: 会话 ID

        Returns:
            List[Message]: 消息列表
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                return []

            return await session.get_messages()

    async def update_session_title(self, session_id: int, title: str) -> bool:
        """
        更新会话标题

        Args:
            session_id: 会话 ID
            title: 新标题

        Returns:
            bool: 是否成功更新
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.title = title
            session.updated_at = datetime.utcnow()

            await DatabaseService.update_conversation(session_id, title=title)
            logger.debug(f"会话标题已更新: {session_id}, 新标题: {title}")
            return True

    async def update_session_metadata(self, session_id: int, metadata: Dict[str, Any]) -> bool:
        """
        更新会话元数据

        Args:
            session_id: 会话 ID
            metadata: 新元数据

        Returns:
            bool: 是否成功更新
        """
        async with self._session_lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.metadata.update(metadata)
            session.updated_at = datetime.utcnow()

            await DatabaseService.update_conversation(session_id, metadata=metadata)
            logger.debug(f"会话元数据已更新: {session_id}")
            return True

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        async with self._session_lock:
            total_sessions = len(self._sessions)
            active_sessions = len([s for s in self._sessions.values() if s.is_active])
            total_messages = sum(s.message_count for s in self._sessions.values())

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "status": "healthy" if active_sessions >= 0 else "warning",
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def shutdown(self) -> None:
        """关闭会话管理器"""
        logger.info("正在关闭会话管理器...")

        if self._cleanup_task:
            self._cleanup_task.cancel()

        # 清理所有会话资源
        async with self._session_lock:
            for session in self._sessions.values():
                await session.cleanup()

        self._sessions.clear()
        logger.info("会话管理器已关闭")


# 创建全局会话管理器实例
_conversation_manager = None


async def get_conversation_manager() -> ConversationManager:
    """
    获取全局会话管理器实例

    Returns:
        ConversationManager: 会话管理器实例
    """
    global _conversation_manager

    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
        await _conversation_manager.initialize()

    return _conversation_manager
