"""
数据库操作测试代码
用于验证数据库模型和操作是否正常工作
"""

import asyncio

from backend.database import get_db_session
from backend.models.agent import Agent, AgentType, AgentStatus
from backend.models.conversation import Conversation, ConversationStatus
from backend.models.message import Message, MessageRole


async def test_create_agent():
    """测试创建智能体"""
    print("测试创建智能体...")
    async for session in get_db_session():
        try:
            agent = Agent(
                name="CodeAct Agent",
                type=AgentType.CODEACT,
                description="一个可以执行代码的智能体",
                config={"model": "claude-3-opus"},
                status=AgentStatus.ACTIVE,
            )
            session.add(agent)
            await session.commit()
            print(f"智能体创建成功: {agent}")
            return agent
        except Exception as e:
            print(f"创建智能体失败: {e}")
            await session.rollback()
            raise


async def test_create_conversation(agent):
    """测试创建会话"""
    print("测试创建会话...")
    async for session in get_db_session():
        try:
            conversation = Conversation(
                user_id="test-user-1",
                agent_id=agent.id,
                title="第一个会话",
                status=ConversationStatus.ACTIVE,
                metadata_={"topic": "代码生成"},
            )
            session.add(conversation)
            await session.commit()
            print(f"会话创建成功: {conversation}")
            return conversation
        except Exception as e:
            print(f"创建会话失败: {e}")
            await session.rollback()
            raise


async def test_create_message(conversation):
    """测试创建消息"""
    print("测试创建消息...")
    async for session in get_db_session():
        try:
            # 创建用户消息
            user_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content="请帮我写一个简单的 Python 函数",
                metadata_={"source": "web"},
            )
            session.add(user_message)

            # 创建智能体回复
            agent_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.AGENT,
                content="当然！这里有一个简单的 Python 函数：\n\n```python\ndef hello_world(name):\n    return f'Hello, {name}!'\n```",
                metadata_={"model": "claude-3-opus"},
            )
            session.add(agent_message)

            await session.commit()
            print(f"消息创建成功: 用户消息 - {user_message}, 智能体消息 - {agent_message}")
            return user_message, agent_message
        except Exception as e:
            print(f"创建消息失败: {e}")
            await session.rollback()
            raise


async def test_query_data():
    """测试查询数据"""
    print("测试查询数据...")
    async for session in get_db_session():
        try:
            # 查询所有智能体
            agents = await session.execute(Agent.__table__.select())
            print(f"智能体数量: {len(agents.fetchall())}")

            # 查询所有会话
            conversations = await session.execute(Conversation.__table__.select())
            print(f"会话数量: {len(conversations.fetchall())}")

            # 查询所有消息
            messages = await session.execute(Message.__table__.select())
            print(f"消息数量: {len(messages.fetchall())}")
        except Exception as e:
            print(f"查询数据失败: {e}")
            raise


async def main():
    """主测试函数"""
    try:
        print("开始测试数据库操作...")
        agent = await test_create_agent()
        conversation = await test_create_conversation(agent)
        await test_create_message(conversation)
        await test_query_data()
        print("所有测试成功完成！")
    except Exception as e:
        print(f"测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
