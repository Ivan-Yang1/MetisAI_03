"""
数据库连接管理模块
"""

import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 默认数据库路径
DEFAULT_PERSISTENCE_DIR = Path.home() / ".metisai"


def get_database_url() -> str:
    """获取数据库连接 URL"""
    # 优先从环境变量获取
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # 默认使用 SQLite
    persistence_dir = DEFAULT_PERSISTENCE_DIR
    persistence_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{str(persistence_dir)}/metisai.db"


# 创建异步引擎
engine = create_async_engine(
    get_database_url(),
    echo=True,
    pool_pre_ping=True,
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖注入函数
    为每个请求创建一个新的数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
