"""
会话管理系统测试模块
用于测试会话的创建、管理和资源清理
"""

import asyncio
import logging
import sys
import unittest
from typing import Any, Dict, List

sys.path.append("E:/Project/MetisAI/MetisAI_03")

from backend.models.conversation import ConversationStatus
from backend.models.message import MessageRole
from backend.services.conversation_manager import (
    ConversationManager,
    Session,
    get_conversation_manager,
)
from backend.services.db_service import DatabaseService

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class TestSession(unittest.IsolatedAsyncioTestCase):
    """测试会话类"""

    async def test_session_creation(self):
        """测试会话创建"""
        logger.info("开始测试会话创建")

        session = Session(session_id=1, user_id="test_user", agent_id=1, title="测试会话")

        self.assertEqual(session.session_id, 1)
        self.assertEqual(session.user_id, "test_user")
        self.assertEqual(session.agent_id, 1)
        self.assertEqual(session.title, "测试会话")
        self.assertEqual(session.status, ConversationStatus.ACTIVE)
        self.assertTrue(session.is_active)

        logger.debug(f"会话状态: {session.session_dict}")

        logger.info("测试会话创建完成")

    async def test_session_message_management(self):
        """测试会话消息管理"""
        logger.info("开始测试会话消息管理")

        session = Session(session_id=2, user_id="test_user", title="消息管理测试")

        # 添加用户消息
        user_message = await session.add_message(MessageRole.USER, "你好，这是测试消息")
        self.assertIsNotNone(user_message)
        self.assertEqual(user_message.role, MessageRole.USER)
        self.assertIn("测试消息", user_message.content)
        self.assertEqual(session.message_count, 1)

        logger.debug(f"添加用户消息后消息数量: {session.message_count}")

        # 添加智能体消息
        agent_message = await session.add_message(
            MessageRole.AGENT,
            "这是智能体的回复",
            metadata={"model": "claude-3-opus"},
        )
        self.assertIsNotNone(agent_message)
        self.assertEqual(agent_message.role, MessageRole.AGENT)
        self.assertIn("智能体的回复", agent_message.content)
        self.assertEqual(session.message_count, 2)

        logger.debug(f"添加智能体消息后消息数量: {session.message_count}")

        # 获取所有消息
        messages = await session.get_messages()
        self.assertEqual(len(messages), 2)

        logger.debug(f"消息列表: {[msg.content for msg in messages]}")

        logger.info("测试会话消息管理完成")

    async def test_session_completion(self):
        """测试会话完成"""
        logger.info("开始测试会话完成")

        session = Session(session_id=3, user_id="test_user", title="完成测试会话")

        await session.complete()
        self.assertEqual(session.status, ConversationStatus.COMPLETED)
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.completed_at)

        logger.debug(f"会话完成时间: {session.completed_at}")

        logger.info("测试会话完成完成")

    async def test_session_cancellation(self):
        """测试会话取消"""
        logger.info("开始测试会话取消")

        session = Session(session_id=4, user_id="test_user", title="取消测试会话")

        await session.cancel()
        self.assertEqual(session.status, ConversationStatus.CANCELED)
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.completed_at)

        logger.debug(f"会话取消时间: {session.completed_at}")

        logger.info("测试会话取消完成")


class TestConversationManager(unittest.IsolatedAsyncioTestCase):
    """测试会话管理器"""

    async def test_manager_initialization(self):
        """测试会话管理器初始化"""
        logger.info("开始测试会话管理器初始化")

        manager = await get_conversation_manager()
        self.assertIsNotNone(manager)

        logger.debug("会话管理器实例化成功")

        logger.info("测试会话管理器初始化完成")

    async def test_create_session(self):
        """测试创建会话"""
        logger.info("开始测试创建会话")

        manager = await get_conversation_manager()

        # 创建会话
        session = await manager.create_session(
            user_id="test_user_1",
            agent_id=1,
            title="测试会话 1",
            metadata={"source": "test"},
        )

        self.assertIsNotNone(session)
        self.assertEqual(session.user_id, "test_user_1")
        self.assertEqual(session.agent_id, 1)
        self.assertEqual(session.title, "测试会话 1")
        self.assertTrue(session.is_active)

        logger.debug(f"创建的会话: {session.session_dict}")

        # 验证会话是否在管理器中
        retrieved_session = await manager.get_session(session.session_id)
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session.session_id)

        logger.debug("会话已成功检索")

        # 测试会话删除
        await manager.delete_session(session.session_id)
        deleted_session = await manager.get_session(session.session_id)
        self.assertIsNone(deleted_session)

        logger.info("测试创建会话完成")

    async def test_session_lifecycle(self):
        """测试会话生命周期"""
        logger.info("开始测试会话生命周期")

        manager = await get_conversation_manager()

        # 创建会话
        session = await manager.create_session(
            user_id="test_user_2",
            agent_id=1,
            title="生命周期测试会话",
        )

        # 向会话添加消息
        await manager.add_message_to_session(
            session.session_id,
            MessageRole.USER,
            "这是第一个消息",
        )

        # 获取会话消息
        messages = await manager.get_session_messages(session.session_id)
        self.assertEqual(len(messages), 1)

        logger.debug(f"会话消息数量: {len(messages)}")

        # 测试会话更新
        new_title = "更新后的会话标题"
        await manager.update_session_title(session.session_id, new_title)

        updated_session = await manager.get_session(session.session_id)
        self.assertEqual(updated_session.title, new_title)

        logger.debug(f"会话标题已更新为: {new_title}")

        # 测试会话完成
        await manager.complete_session(session.session_id)

        completed_session = await manager.get_session(session.session_id)
        self.assertEqual(completed_session.status, ConversationStatus.COMPLETED)
        self.assertFalse(completed_session.is_active)

        logger.debug(f"会话状态已变为: {completed_session.status.value}")

        await manager.delete_session(session.session_id)

        logger.info("测试会话生命周期完成")

    async def test_session_health_check(self):
        """测试会话健康检查"""
        logger.info("开始测试会话健康检查")

        manager = await get_conversation_manager()
        health_info = await manager.health_check()

        self.assertIsNotNone(health_info)
        self.assertIn("total_sessions", health_info)
        self.assertIn("active_sessions", health_info)
        self.assertIn("total_messages", health_info)
        self.assertIn("status", health_info)

        logger.debug(f"健康检查信息: {health_info}")

        logger.info("测试会话健康检查完成")

    async def test_bulk_session_operations(self):
        """测试批量会话操作"""
        logger.info("开始测试批量会话操作")

        manager = await get_conversation_manager()

        # 批量创建会话
        session_ids: List[int] = []
        for i in range(3):
            session = await manager.create_session(
                user_id=f"test_user_{i}",
                agent_id=1,
                title=f"批量创建会话 {i}",
            )
            session_ids.append(session.session_id)

        logger.debug(f"批量创建的会话: {session_ids}")

        # 获取用户的所有会话
        user_sessions = await manager.get_sessions_by_user("test_user_0")
        self.assertEqual(len(user_sessions), 1)
        self.assertEqual(user_sessions[0].user_id, "test_user_0")

        logger.debug(f"用户 test_user_0 的会话数量: {len(user_sessions)}")

        # 获取所有活动会话
        active_sessions = await manager.get_active_sessions()
        active_ids = [session.session_id for session in active_sessions]
        self.assertTrue(all(sid in active_ids for sid in session_ids))

        logger.debug(f"活动会话数量: {len(active_sessions)}")

        # 删除所有创建的会话
        for session_id in session_ids:
            await manager.delete_session(session_id)

        logger.info("测试批量会话操作完成")

    async def test_session_timeout(self):
        """测试会话超时"""
        logger.info("开始测试会话超时")

        manager = await get_conversation_manager()

        # 创建会话
        session = await manager.create_session(
            user_id="test_user_timeout",
            title="超时测试会话",
        )

        # 设置一个非常短的超时时间进行测试
        await session.set_timeout(1.0)  # 1 秒超时

        logger.debug("会话超时已设置为 1 秒")

        # 等待超时
        await asyncio.sleep(1.5)

        # 获取会话状态
        retrieved_session = await manager.get_session(session.session_id)
        self.assertIsNotNone(retrieved_session)

        logger.debug(f"会话状态: {retrieved_session.status.value}")

        await manager.delete_session(session.session_id)

        logger.info("测试会话超时完成")


class TestConversationManagerIntegration(unittest.IsolatedAsyncioTestCase):
    """测试会话管理器与数据库集成"""

    async def test_manager_db_integration(self):
        """测试会话管理器与数据库集成"""
        logger.info("开始测试会话管理器与数据库集成")

        manager = await get_conversation_manager()

        # 创建会话
        session = await manager.create_session(
            user_id="db_test_user",
            agent_id=1,
            title="数据库集成测试会话",
        )

        # 从数据库直接获取会话
        db_conversation = await DatabaseService.get_conversation(session.session_id)
        self.assertIsNotNone(db_conversation)
        self.assertEqual(db_conversation.user_id, session.user_id)
        self.assertEqual(db_conversation.agent_id, session.agent_id)
        self.assertEqual(db_conversation.title, session.title)

        logger.debug("会话已成功保存到数据库")

        await manager.delete_session(session.session_id)

        logger.info("测试会话管理器与数据库集成完成")

    async def test_session_message_db_sync(self):
        """测试会话消息数据库同步"""
        logger.info("开始测试会话消息数据库同步")

        manager = await get_conversation_manager()

        # 创建会话
        session = await manager.create_session(
            user_id="db_message_test",
            title="消息同步测试会话",
        )

        # 添加消息
        await manager.add_message_to_session(
            session.session_id,
            MessageRole.USER,
            "数据库同步测试消息",
        )

        # 从数据库直接获取消息
        db_messages = await DatabaseService.get_messages_by_conversation(session.session_id)
        self.assertEqual(len(db_messages), 1)
        self.assertEqual(db_messages[0].content, "数据库同步测试消息")

        logger.debug("消息已成功同步到数据库")

        await manager.delete_session(session.session_id)

        logger.info("测试会话消息数据库同步完成")


if __name__ == "__main__":
    unittest.main()
