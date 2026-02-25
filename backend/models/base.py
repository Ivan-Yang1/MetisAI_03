"""
共享的 SQLAlchemy 基类
所有模型都应该从这个基类继承
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
