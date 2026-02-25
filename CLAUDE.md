# MetisAI - 项目说明文档

## 项目概述

一个基于 OpenHands 架构的 Python 前后端 AI 驱动开发平台。

> 注意：详细的项目需求在 `需求文档.md` 中，任务定义在 `task.json` 中。

---

## 强制要求：智能体工作流程

每个新的智能体会话必须遵循以下工作流程：

### 步骤 1：初始化环境

```bash
# Linux/macOS
./init.sh

# Windows (PowerShell)
.\init.ps1
```

这将：
- 检查是否安装了所需的工具
- 设置开发环境
- 创Python虚拟环境（如需要）
- 安装项目依赖
- 启动后端和前端开发服务器

**请勿跳过此步骤。** 在继续之前确保服务器正在运行。

### 步骤 2：选择下一个任务

读取 `task.json` 并选择一个任务来处理。

选择标准（按优先级排序）：
1. 选择 `passes: false` 的任务
2. 考虑依赖关系 - 基本功能应该先完成
3. 选择最高优先级的未完成任务

### 步骤 3：实现任务

- 仔细阅读任务描述和步骤
- 参考OpenHands-main-example中相同功能的实现
- 实现功能以满足所有步骤
- 遵循现有的代码模式和约定

### 步骤 4：彻底测试

实现后：
- 测试所有功能以确保其正常工作
- 运行所有相关测试（如果可用），尽量使用端到端测试，可以使用playwrightMCP进行模拟测试
- 验证更改是否修复了问题或满足了要求

### 步骤 5：记录进度

更新 `progress.txt` 包含：
- 任务完成状态
- 修改的文件
- 关键技术决策
- 测试结果

### 步骤 6：提交git

**IMPORTANT: 所有相关的更改应该在同一个 commit 中提交！**

```bash
git add .
git commit -m "[任务描述] - completed"
git push origin master
```

---

## ⚠️ 阻塞处理（Blocking Issues）

**如果任务无法完成测试或需要人工介入，必须遵循以下规则：**

### 需要停止任务并请求人工帮助的情况：

1. **缺少环境配置**：
   - .env 文件需要填写真实的 API 密钥
   - 数据库需要创建和配置
   - 外部服务需要开通账号

2. **外部依赖不可用**：
   - 第三方 API 服务宕机
   - 需要人工授权的 OAuth 流程
   - 需要付费升级的服务

3. **测试无法进行**：
   - 功能依赖外部系统尚未部署
   - 需要特定硬件环境

### 阻塞时的正确操作：

**DO NOT（禁止）：**
- ❌ 提交 git commit
- ❌ 将任务标记为完成
- ❌ 假装任务已完成

**DO（必须）：**
- ✅ 在 progress.txt 中记录当前进度和阻塞原因
- ✅ 输出清晰的阻塞信息，说明需要人工做什么
- ✅ 停止任务，等待人工介入

### 阻塞信息格式：

```
🚫 任务阻塞 - 需要人工介入

**当前任务**: [任务名称]

**已完成的工作**:
- [已完成的代码/配置]

**阻塞原因**:
- [具体说明为什么无法继续]

**需要人工帮助**:
1. [具体的步骤 1]
2. [具体的步骤 2]
...

**解除阻塞后**:
- [继续任务的步骤]
```

---


## 项目结构

```
/
├── CLAUDE.md          # 此文件 - 工作流程说明
├── task.json          # 任务定义（权威来源）
├── progress.txt       # 每个会话的进度日志
├── init.sh            # Linux/macOS 初始化脚本
├── init.ps1           # Windows 初始化脚本（PowerShell）
├── 需求文档.md         # 项目需求文档
├── OpenHands架构文档.md  # 架构分析报告
├── backend/           # Python 后端（FastAPI）
└── frontend/          # React 前端（Vite）
```

## 命令

```bash
# 前端命令（在 frontend/ 目录）
npm run dev      # 在端口 5173 启动 React 开发服务器
npm run build    # 生产构建
npm run lint     # 运行 linter

# 后端命令（在 backend/ 目录）
poetry install   # 安装 Python 依赖
poetry shell     # 激活虚拟环境
poetry run dev   # 在端口 8000 启动 FastAPI 服务器
```

## 代码规范

### 前端
- React 19 与 TypeScript 严格模式
- Redux Toolkit 用于状态管理
- React Router 用于路由
- Tailwind CSS 用于样式
- 使用 Hooks 的函数式组件

### 后端
- Python 3.12-3.13
- FastAPI 与异步端点
- SQLAlchemy ORM
- Pydantic 用于数据验证
- 使用类型提示的参数

---

## 关键规则

1. **每个会话一个任务** - 专注于做好一个任务
2. **标记完成前测试** - 所有步骤必须通过
3. **记录所有变更** - 每个会话都要更新 progress.txt
4. **遵循现有模式** - 保持与现有代码库的一致性
5. **频繁提交** - 使用有意义的提交消息

---

## 依赖项

### 所需工具
- Docker 和 Docker Compose（用于容器化）
- Python 3.12+（用于后端）
- Node.js 18+（用于前端）
- Git（用于版本控制）

### Python 包
- FastAPI
- SQLAlchemy
- JWT
- python-socketio
- litellm
- Pydantic

### 前端包
- React 19
- TypeScript
- Redux Toolkit
- React Router
- Socket.IO
- Axios