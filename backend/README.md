# MetisAI - 后端服务

基于 FastAPI 的 AI 驱动开发平台后端服务。

## 功能

- 智能体管理
- 会话管理
- 消息处理
- WebSocket 通信
- LLM 集成
- 沙箱执行环境

## 技术栈

- Python 3.12+
- FastAPI
- SQLAlchemy ORM
- JWT 认证
- Socket.IO
- LiteLLM

## 安装依赖

```bash
# 使用 Poetry 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 启动开发服务器
poetry run dev
```

## 开发

```bash
# 启动开发服务器
poetry run dev

# 运行测试
poetry run pytest

# 格式化代码
poetry run ruff format

# 检查代码
poetry run ruff check
```
