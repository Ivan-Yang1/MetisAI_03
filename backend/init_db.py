"""
数据库初始化模块
用于创建表结构和初始化数据
"""

import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.database import DEFAULT_PERSISTENCE_DIR, get_database_url
from backend.models.base import Base


async def init_database():
    """初始化数据库"""
    print("初始化数据库...")

    # 确保数据目录存在
    DEFAULT_PERSISTENCE_DIR.mkdir(parents=True, exist_ok=True)

    # 创建异步引擎
    engine = create_async_engine(get_database_url(), echo=True)

    # 创建所有表
    async with engine.begin() as conn:
        # 为了简化示例，我们先删除所有表（生产环境中不应这样做）
        await conn.run_sync(Base.metadata.drop_all)
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    print("数据库初始化完成！")


async def main():
    """主函数"""
    try:
        await init_database()
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        raise e


if __name__ == "__main__":
    asyncio.run(main())
