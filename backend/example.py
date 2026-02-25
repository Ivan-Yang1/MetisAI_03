"""
数据库操作示例
演示如何使用 DatabaseService 进行 CRUD 操作
"""

import asyncio
from typing import List, Optional

from backend.models.agent import AgentType, AgentStatus
from backend.models.conversation import ConversationStatus
from backend.models.message import MessageRole
from backend.services.db_service import DatabaseService


async def main():
    """主函数"""
    print("=== 数据库操作示例 ===")

    # 1. 创建智能体
    print("\n1. 创建智能体:")
    agent = await DatabaseService.create_agent(
        name="Chat Agent",
        type=AgentType.CHAT,
        description="一个可以聊天的智能体",
        config={"model": "gpt-4"},
        status=AgentStatus.ACTIVE,
    )
    print(f"成功创建智能体: {agent}")

    # 2. 创建会话
    print("\n2. 创建会话:")
    conversation = await DatabaseService.create_conversation(
        user_id="test-user-2",
        agent_id=agent.id,
        title="聊天会话",
        status=ConversationStatus.ACTIVE,
        metadata={"topic": "日常聊天"},
    )
    print(f"成功创建会话: {conversation}")

    # 3. 创建消息
    print("\n3. 创建消息:")
    user_message = await DatabaseService.create_message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="你好，今天天气怎么样？",
        metadata={"source": "web"},
    )
    print(f"成功创建用户消息: {user_message}")

    agent_message = await DatabaseService.create_message(
        conversation_id=conversation.id,
        role=MessageRole.AGENT,
        content="我无法直接获取天气信息，但我可以帮你查询。你所在的城市是？",
        metadata={"model": "gpt-4"},
    )
    print(f"成功创建智能体消息: {agent_message}")

    # 4. 查询数据
    print("\n4. 查询数据:")
    all_agents = await DatabaseService.get_all_agents()
    print(f"所有智能体 ({len(all_agents)} 个):")
    for a in all_agents:
        print(f"  - {a}")

    user_conversations = await DatabaseService.get_conversations_by_user(
        "test-user-2"
    )
    print(f"\n用户 'test-user-2' 的会话 ({len(user_conversations)} 个):")
    for c in user_conversations:
        print(f"  - {c}")

    conversation_messages = await DatabaseService.get_messages_by_conversation(
        conversation.id
    )
    print(f"\n会话 {conversation.id} 的消息 ({len(conversation_messages)} 个):")
    for m in conversation_messages:
        print(f"  - {m.role}: {m.content}")

    # 5. 更新数据
    print("\n5. 更新数据:")
    updated_agent = await DatabaseService.update_agent(
        agent.id, description="一个可以聊天和回答问题的智能体"
    )
    print(f"成功更新智能体: {updated_agent}")

    updated_conversation = await DatabaseService.update_conversation(
        conversation.id, title="天气查询会话"
    )
    print(f"成功更新会话: {updated_conversation}")

    # 6. 删除数据
    print("\n6. 删除数据:")
    message_count_before = len(
        await DatabaseService.get_messages_by_conversation(conversation.id)
    )
    await DatabaseService.delete_message(user_message.id)
    message_count_after = len(
        await DatabaseService.get_messages_by_conversation(conversation.id)
    )
    print(
        f"成功删除用户消息，消息数量从 {message_count_before} 减少到 {message_count_after}"
    )

    conversation_count_before = len(
        await DatabaseService.get_conversations_by_user("test-user-2")
    )
    await DatabaseService.delete_conversation(conversation.id)
    conversation_count_after = len(
        await DatabaseService.get_conversations_by_user("test-user-2")
    )
    print(
        f"成功删除会话，会话数量从 {conversation_count_before} 减少到 {conversation_count_after}"
    )

    agent_count_before = len(await DatabaseService.get_all_agents())
    await DatabaseService.delete_agent(agent.id)
    agent_count_after = len(await DatabaseService.get_all_agents())
    print(
        f"成功删除智能体，智能体数量从 {agent_count_before} 减少到 {agent_count_after}"
    )

    print("\n=== 示例操作完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
