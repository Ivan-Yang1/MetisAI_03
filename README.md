# MetisAI - AI 驱动开发平台

一个基于 OpenHands 架构的 Python 前后端 AI 驱动开发平台，支持智能体管理、会话管理、消息处理和 LLM 集成。

## 项目架构

- **前端**: React 19 + TypeScript + Redux Toolkit + React Router + Tailwind CSS
- **后端**: FastAPI + Python 3.12+ + SQLAlchemy + SQLite + LiteLLM
- **数据库**: SQLite (开发环境), PostgreSQL (生产环境)
- **LLM 集成**: LiteLLM (支持 OpenAI, Anthropic, Google, Azure 等)

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- npm 或 yarn
- Docker (可选，用于沙箱执行)

### 1. 克隆项目

```bash
git clone <repository-url>
cd MetisAI_03
```

### 2. 初始化环境

#### Windows (PowerShell)

```powershell
.\init.ps1
```

#### Linux/macOS

```bash
./init.sh
```

### 3. 配置 LLM

#### 3.1 环境变量配置

创建 `.env` 文件（复制 `.env.local` 模板）：

```bash
cp .env.local .env
```

编辑 `.env` 文件，添加您的 LLM API 密钥：

```env
# LLM 配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
AZURE_API_KEY=your_azure_api_key
AZURE_API_BASE=your_azure_api_base
AZURE_API_VERSION=your_azure_api_version

# 数据库配置
DATABASE_URL=sqlite:///./metisai.db

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

#### 3.2 支持的 LLM 提供商

MetisAI 使用 LiteLLM 库支持多种 LLM 提供商：

- **OpenAI**: GPT-3.5, GPT-4, GPT-4o
- **Anthropic**: Claude 3 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Google**: PaLM 2, Gemini Pro
- **Azure**: Azure OpenAI Service
- **其他**: 支持大多数符合 OpenAI 兼容 API 的提供商

### 4. 启动开发服务器

#### 4.1 后端启动

```bash
cd backend
poetry install
poetry run dev
```

后端服务器将在 `http://localhost:8000` 上运行。

#### 4.2 前端启动

在另一个终端窗口中：

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器将在 `http://localhost:5173` 上运行。

### 5. 测试应用

#### 5.1 访问应用

打开浏览器访问 `http://localhost:5173`。

#### 5.2 创建第一个智能体

1. 点击「智能体管理」页面
2. 点击「创建智能体」按钮
3. 填写智能体信息：
   - 名称：My First Agent
   - 类型：CodeActAgent
   - 描述：我的第一个代码执行智能体
   - 配置：可以留空使用默认配置
4. 点击「创建」

#### 5.3 测试智能体

1. 选中刚刚创建的智能体
2. 点击「运行智能体」按钮
3. 在输入框中输入指令，例如：
   ```
   请写一个 Python 函数来计算斐波那契数列的第 n 项
   ```
4. 观察智能体的响应

### 6. 项目结构

```
MetisAI_03/
├── backend/                # 后端代码
│   ├── api/               # API 路由
│   ├── agents/            # 智能体实现
│   ├── controllers/       # 业务逻辑控制器
│   ├── database/          # 数据库连接和管理
│   ├── models/            # 数据模型
│   ├── services/          # 服务层
│   ├── states/            # 状态管理
│   ├── tests/             # 测试代码
│   ├── main.py            # 后端入口文件
│   └── pyproject.toml     # Python 依赖配置
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API 调用封装
│   │   ├── components/    # UI 组件
│   │   ├── hooks/         # 自定义 hooks
│   │   ├── pages/         # 页面组件
│   │   ├── store/         # Redux 状态管理
│   │   └── App.tsx        # 应用入口
│   ├── package.json       # 前端依赖配置
│   └── vite.config.ts     # Vite 配置
├── .env.local             # 环境变量模板
├── CLAUDE.md             # 项目说明文档
├── 需求文档.md            # 详细项目需求
├── OpenHands架构文档.md   # 架构分析报告
├── task.json             # 任务分解
├── progress.txt          # 项目进度记录
├── init.ps1              # Windows 初始化脚本
└── init.sh               # Linux/macOS 初始化脚本
```

### 7. 核心功能

#### 7.1 智能体管理

- 创建、配置、运行和停止 AI 智能体
- 支持多种智能体类型（CodeActAgent, ChatAgent 等）
- 智能体状态监控和管理
- 智能体配置验证

#### 7.2 会话管理

- 创建和管理会话
- 会话状态跟踪
- 会话超时和资源清理
- 会话与智能体关联

#### 7.3 消息处理

- 发送和接收消息
- 消息历史记录
- 消息状态管理
- 消息元数据存储

#### 7.4 LLM 集成

- 支持多种 LLM 提供商
- 统一的 API 接口
- 代码生成功能
- 提示模板管理

### 8. 开发指南

#### 8.1 数据库操作

```bash
cd backend
# 初始化数据库
poetry run python init_db.py
# 运行数据库操作示例
poetry run python example.py
# 运行数据库操作测试
poetry run python test_db.py
```

#### 8.2 运行测试

```bash
cd backend
# 运行智能体系统测试
poetry run python -m unittest tests.test_agents
# 运行会话管理测试
poetry run python -m unittest tests.test_conversations
# 运行消息处理测试
poetry run python -m unittest tests.test_messages
```

#### 8.3 前端测试

```bash
cd frontend
# 运行 TypeScript 检查
npm run build
# 运行 ESLint 检查
npm run lint
```

### 9. 部署

#### 9.1 生产环境部署

#### 9.1.1 Docker 部署

```bash
# 构建后端镜像
cd backend
docker build -t metisai-backend .

# 构建前端镜像
cd frontend
docker build -t metisai-frontend .

# 启动服务
cd ..
docker-compose up -d
```

#### 9.1.2 直接部署

```bash
# 构建前端
cd frontend
npm run build

# 启动后端
cd backend
poetry install --no-dev
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 9.2 环境变量配置

生产环境需要额外配置以下环境变量：

```env
# 生产环境数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/metisai

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=False

# 安全配置
SECRET_KEY=your_secret_key
```

### 10. 故障排除

#### 10.1 常见问题

**Q: 前端无法连接到后端**

A: 确保后端服务器正在运行，并且端口号正确。检查 CORS 配置。

**Q: LLM 响应超时**

A: 检查网络连接，或尝试调整超时设置。

**Q: 智能体无法运行**

A: 检查智能体配置是否正确，或查看服务器日志以获取详细错误信息。

#### 10.2 日志查看

```bash
# 后端日志
cd backend
poetry run python main.py

# 前端日志
cd frontend
npm run dev
```

### 11. 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送分支
5. 创建 Pull Request

### 12. 许可证

MIT License

### 13. 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件

---

**注意**: 本项目处于开发阶段，功能可能会有所变更。请定期查看项目更新。
