# OpenHands 项目架构文档

## 项目概述

OpenHands 是一个 AI 驱动的开发平台，使软件智能体能够自主执行编码任务。系统提供多种接口，包括 SDK、CLI、本地 GUI、云部署和企业解决方案。

**项目地址**：https://github.com/OpenHands/OpenHands

**架构版本**：V1（当前）| V0（已废弃，计划于 2026 年 4 月 1 日移除）

## 1. 整体架构设计

### 1.1 系统层次结构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     前端应用层 (Frontend)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │  React 19.2  │ │  UI组件库    │ │ 状态管理     │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     API 网关层 (API Gateway)                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │  REST API    │ │  WebSocket   │ │ 认证授权     │                │
│  │ (/api/v1/*)  │ │  (V0遗留)    │ │              │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     应用服务层 (Application Services)              │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐    │
│  │ V1 应用服务器            │  │ 会话管理与智能体控制器        │    │
│  │ (openhands/app_server/)  │  │ (AppConversationService)     │    │
│  └──────────────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     核心服务层 (Core Services)                      │
│  ┌─────────────────┐ ┌────────────────────┐ ┌──────────────────┐  │
│  │ LLM 集成        │ │ 运行时管理         │ │ 存储系统         │  │
│  │ (litellm包装)    │ │ (Docker/K8s/Local) │ │ (FileStore实现)  │  │
│  └─────────────────┘ └────────────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     执行环境层 (Execution Environment)             │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐   │
│  │ Docker 容器      │ │ Kubernetes       │ │ 沙箱执行服务器    │   │
│  │ (沙箱化运行)      │ │ (编排与管理)      │ │ (ActionExecution)│   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘   │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐   │
│  │ Bash 会话        │ │ Playwright 浏览器 │ │ Jupyter 内核     │   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈概览

| 层级 | 组件 | 技术栈 |
|------|------|--------|
| **前端** | React 应用 | React 19.2.3, WebSocket, REST API |
| **后端** | API 服务器 | Python 3.12-3.13, FastAPI, SQLAlchemy |
| **LLM 集成** | LLM 抽象层 | litellm (≥1.74.3) |
| **数据库** | 存储系统 | PostgreSQL/SQLite, SQLAlchemy ORM |
| **容器化** | 执行环境 | Docker, Kubernetes |
| **依赖管理** | 包管理 | Poetry (≥2.1.2) |

## 2. 前端应用架构

### 2.1 项目结构

```
frontend/
├── package.json                 # 项目依赖
├── package-lock.json            # 依赖锁定文件
├── public/                      # 静态资源
└── src/                        # 源代码
    ├── components/             # UI 组件
    │   ├── common/            # 通用组件
    │   ├── features/          # 功能组件
    │   └── layout/           # 布局组件
    ├── pages/                 # 页面组件
    │   ├── Dashboard/        # 仪表板
    │   ├── AgentManagement/  # 智能体管理
    │   ├── Settings/         # 设置
    │   └── Conversations/    # 会话
    ├── services/             # API 服务
    │   ├── api/             # REST API 客户端
    │   ├── websocket/       # WebSocket 客户端
    │   └── llm/             # LLM 集成
    ├── store/                # 状态管理
    │   ├── slices/          # Redux 切片
    │   ├── hooks/           # 自定义 Hooks
    │   └── index.js         # 存储配置
    ├── utils/               # 工具函数
    │   ├── formatters/      # 格式化工具
    │   ├── validators/      # 验证工具
    │   └── helpers/         # 辅助函数
    ├── App.js               # 根组件
    ├── index.js             # 入口文件
    └── setupTests.js        # 测试配置
```

### 2.2 前端主要功能

#### 2.2.1 智能体管理界面

```javascript
// src/pages/AgentManagement/AgentList.jsx
import React, { useEffect, useState } from 'react';
import { AgentCard } from '../../components/features';
import { getAgents } from '../../services/api';

const AgentList = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await getAgents();
        setAgents(response.data);
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
  }, []);

  return (
    <div className="agent-list">
      <h1>智能体管理</h1>
      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="agent-grid">
          {agents.map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onStart={handleStartAgent}
              onStop={handleStopAgent}
              onDelete={handleDeleteAgent}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentList;
```

#### 2.2.2 会话管理界面

```javascript
// src/pages/Conversations/ConversationPanel.jsx
import React, { useState } from 'react';
import { ChatMessage, ChatInput } from '../../components/features';
import { sendMessage } from '../../services/api';

const ConversationPanel = ({ conversationId }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    try {
      const response = await sendMessage(conversationId, inputText);
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="conversation-panel">
      <div className="messages-container">
        {messages.map(message => (
          <ChatMessage key={message.id} message={message} />
        ))}
      </div>
      <ChatInput
        value={inputText}
        onChange={setInputText}
        onSend={handleSendMessage}
        placeholder="输入消息..."
      />
    </div>
  );
};

export default ConversationPanel;
```

### 2.3 状态管理架构

```javascript
// src/store/slices/agentsSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getAgents, startAgent, stopAgent } from '../../services/api';

export const fetchAgents = createAsyncThunk(
  'agents/fetchAgents',
  async () => {
    const response = await getAgents();
    return response.data;
  }
);

export const startAgentThunk = createAsyncThunk(
  'agents/startAgent',
  async (agentId) => {
    const response = await startAgent(agentId);
    return response.data;
  }
);

export const stopAgentThunk = createAsyncThunk(
  'agents/stopAgent',
  async (agentId) => {
    const response = await stopAgent(agentId);
    return response.data;
  }
);

const agentsSlice = createSlice({
  name: 'agents',
  initialState: {
    list: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(startAgentThunk.fulfilled, (state, action) => {
        state.list = state.list.map(agent =>
          agent.id === action.payload.id ? action.payload : agent
        );
      })
      .addCase(stopAgentThunk.fulfilled, (state, action) => {
        state.list = state.list.map(agent =>
          agent.id === action.payload.id ? action.payload : agent
        );
      });
  },
});

export default agentsSlice.reducer;
```

### 2.4 API 集成架构

```javascript
// src/services/api/index.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 智能体管理 API
export const getAgents = () => api.get('/agents');
export const getAgentById = (id) => api.get(`/agents/${id}`);
export const createAgent = (data) => api.post('/agents', data);
export const updateAgent = (id, data) => api.put(`/agents/${id}`, data);
export const deleteAgent = (id) => api.delete(`/agents/${id}`);
export const startAgent = (id) => api.post(`/agents/${id}/start`);
export const stopAgent = (id) => api.post(`/agents/${id}/stop`);

// 会话管理 API
export const getConversations = () => api.get('/conversations');
export const getConversationById = (id) => api.get(`/conversations/${id}`);
export const createConversation = (data) => api.post('/conversations', data);
export const deleteConversation = (id) => api.delete(`/conversations/${id}`);
export const sendMessage = (conversationId, content) =>
  api.post(`/conversations/${conversationId}/messages`, { content });

// 设置 API
export const getSettings = () => api.get('/settings');
export const updateSettings = (data) => api.put('/settings', data);
export const getSecrets = () => api.get('/secrets');
export const createSecret = (data) => api.post('/secrets', data);
export const deleteSecret = (id) => api.delete(`/secrets/${id}`);

// Git 集成 API
export const getRepositories = () => api.get('/git/repositories');
export const getRepositoryById = (id) => api.get(`/git/repositories/${id}`);
export const createRepository = (data) => api.post('/git/repositories', data);
export const deleteRepository = (id) => api.delete(`/git/repositories/${id}`);
export const getBranches = (repoId) =>
  api.get(`/git/repositories/${repoId}/branches`);

export default api;
```

## 3. 智能体系统架构

### 3.1 智能体控制器架构

```python
# openhands/app_server/services/app_conversation_service.py
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from openhands.app_server.models.conversation import Conversation
from openhands.app_server.models.message import Message
from openhands.llm.client import LLMClient
from openhands.runtime.manager import RuntimeManager
from openhands.storage.file_store import FileStore


class AppConversationService:
    """应用会话服务 - 管理智能体会话和交互"""

    def __init__(self, llm_client: LLMClient, runtime_manager: RuntimeManager,
                 file_store: FileStore):
        self.llm_client = llm_client
        self.runtime_manager = runtime_manager
        self.file_store = file_store

    async def create_conversation(self, user_id: UUID, agent_config: dict) -> Conversation:
        """创建新的会话"""
        conversation = Conversation(
            user_id=user_id,
            agent_config=agent_config,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await conversation.save()
        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """获取会话"""
        return await Conversation.filter(id=conversation_id).first()

    async def send_message(self, conversation_id: UUID, content: str) -> Message:
        """发送消息到智能体"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError("会话不存在")

        # 保存用户消息
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        await user_message.save()

        # 获取历史消息
        messages = await self._get_conversation_history(conversation_id)

        # 生成智能体响应
        response = await self.llm_client.generate_response(messages, conversation.agent_config)

        # 保存智能体消息
        agent_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            timestamp=datetime.now()
        )
        await agent_message.save()

        # 更新会话时间
        conversation.updated_at = datetime.now()
        await conversation.save()

        return agent_message

    async def _get_conversation_history(self, conversation_id: UUID) -> List[dict]:
        """获取会话历史"""
        messages = await Message.filter(conversation_id=conversation_id).order_by('timestamp')
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
```

### 3.2 LLM 集成架构

```python
# openhands/llm/client.py
from typing import List, Dict, Optional

import litellm
from openhands.core.config import settings
from openhands.core.logging import logger


class LLMClient:
    """LLM 客户端 - 抽象层"""

    def __init__(self):
        self._init_litellm()
        self.model = settings.llm.default_model
        self.api_key = settings.llm.api_key

    def _init_litellm(self):
        """初始化 litellm"""
        litellm.set_verbose(settings.llm.verbose)
        litellm.set_custom_llm_provider("openai", "https://api.openai.com/v1")
        if settings.llm.debug:
            logger.debug("LLM 客户端初始化完成")

    async def generate_response(self, messages: List[Dict], config: Optional[Dict] = None) -> str:
        """生成智能体响应"""
        try:
            response = await litellm.acompletion(
                model=self.model or config.get('model'),
                messages=messages,
                api_key=self.api_key,
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 2000),
                top_p=config.get('top_p', 1.0),
                frequency_penalty=config.get('frequency_penalty', 0.0),
                presence_penalty=config.get('presence_penalty', 0.0)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 生成响应失败: {str(e)}")
            raise
```

### 3.3 运行时管理架构

```python
# openhands/runtime/manager.py
from typing import Optional
from abc import ABC, abstractmethod

from openhands.core.config import settings
from openhands.runtime.impl.docker import DockerRuntime
from openhands.runtime.impl.kubernetes import KubernetesRuntime
from openhands.runtime.impl.local import LocalRuntime
from openhands.runtime.impl.remote import RemoteRuntime


class RuntimeManager:
    """运行时管理器 - 管理不同类型的运行时环境"""

    def __init__(self):
        self._runtimes = {
            'docker': DockerRuntime(),
            'kubernetes': KubernetesRuntime(),
            'local': LocalRuntime(),
            'remote': RemoteRuntime(),
        }

    def get_runtime(self, runtime_type: str = None) -> 'BaseRuntime':
        """获取运行时实例"""
        runtime_type = runtime_type or settings.runtime.default_type
        if runtime_type not in self._runtimes:
            raise ValueError(f"不支持的运行时类型: {runtime_type}")
        return self._runtimes[runtime_type]


class BaseRuntime(ABC):
    """运行时基础接口"""

    @abstractmethod
    async def start_session(self, config: dict) -> str:
        """启动会话"""
        pass

    @abstractmethod
    async def execute_command(self, session_id: str, command: str) -> dict:
        """执行命令"""
        pass

    @abstractmethod
    async def stop_session(self, session_id: str) -> None:
        """停止会话"""
        pass


class DockerRuntime(BaseRuntime):
    """Docker 运行时实现"""

    async def start_session(self, config: dict) -> str:
        # 启动 Docker 容器
        pass

    async def execute_command(self, session_id: str, command: str) -> dict:
        # 在 Docker 容器中执行命令
        pass

    async def stop_session(self, session_id: str) -> None:
        # 停止 Docker 容器
        pass
```

### 3.4 智能体状态管理

```python
# openhands/app_server/models/agent.py
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from openhands.app_server.database import Base


class AgentStatus(str, Enum):
    """智能体状态"""
    STOPPED = 'stopped'
    STARTING = 'starting'
    RUNNING = 'running'
    STOPPING = 'stopping'
    ERROR = 'error'


class Agent(Base):
    """智能体模型"""
    __tablename__ = 'agents'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    config: Mapped[dict] = mapped_column(JSON)
    status: Mapped[AgentStatus] = mapped_column(
        String(50),
        default=AgentStatus.STOPPED
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    def __repr__(self):
        return f"<Agent {self.name}>"

    async def update_status(self, status: AgentStatus):
        """更新智能体状态"""
        self.status = status
        await self.save()

    async def start(self):
        """启动智能体"""
        if self.status != AgentStatus.STOPPED:
            raise ValueError("智能体状态无效")

        await self.update_status(AgentStatus.STARTING)
        try:
            # 启动逻辑...
            await self.update_status(AgentStatus.RUNNING)
        except Exception as e:
            await self.update_status(AgentStatus.ERROR)
            raise

    async def stop(self):
        """停止智能体"""
        if self.status != AgentStatus.RUNNING:
            raise ValueError("智能体状态无效")

        await self.update_status(AgentStatus.STOPPING)
        try:
            # 停止逻辑...
            await self.update_status(AgentStatus.STOPPED)
        except Exception as e:
            await self.update_status(AgentStatus.ERROR)
            raise
```

## 4. 后端架构

### 4.1 API 服务器架构

```python
# openhands/app_server/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from openhands.app_server.database import get_db
from openhands.app_server.models.agent import Agent, AgentStatus
from openhands.app_server.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentStatusResponse
)
from openhands.app_server.services.app_conversation_service import (
    AppConversationService
)
from openhands.app_server.services.agent_service import AgentService
from openhands.core.config import settings


app = FastAPI(title="OpenHands V1 API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

# 安全配置
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证访问令牌"""
    token = credentials.credentials
    # 实际实现应该验证 JWT 令牌
    if token != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    return token


# 依赖注入
def get_agent_service(db: AsyncSession = Depends(get_db)):
    """获取智能体服务"""
    return AgentService(db)


def get_conversation_service(db: AsyncSession = Depends(get_db)):
    """获取会话服务"""
    return AppConversationService(db)


# 智能体管理接口
@app.get("/api/v1/agents", response_model=list[AgentResponse])
async def list_agents(
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """获取智能体列表"""
    return await agent_service.get_all_agents()


@app.get("/api/v1/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """获取智能体详情"""
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    return agent


@app.post("/api/v1/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """创建智能体"""
    return await agent_service.create_agent(agent_data)


@app.put("/api/v1/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """更新智能体"""
    agent = await agent_service.update_agent(agent_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    return agent


@app.delete("/api/v1/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """删除智能体"""
    deleted = await agent_service.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="智能体不存在")


@app.post("/api/v1/agents/{agent_id}/start", response_model=AgentStatusResponse)
async def start_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """启动智能体"""
    await agent_service.start_agent(agent_id)
    return {"status": AgentStatus.RUNNING}


@app.post("/api/v1/agents/{agent_id}/stop", response_model=AgentStatusResponse)
async def stop_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    _: str = Depends(verify_token)
):
    """停止智能体"""
    await agent_service.stop_agent(agent_id)
    return {"status": AgentStatus.STOPPED}


# 会话管理接口
@app.post("/api/v1/conversations", status_code=201)
async def create_conversation(
    conversation_service: AppConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_token)
):
    """创建新会话"""
    return await conversation_service.create_conversation()


@app.get("/api/v1/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    conversation_service: AppConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_token)
):
    """获取会话消息"""
    return await conversation_service.get_messages(conversation_id)


@app.post("/api/v1/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: dict,
    conversation_service: AppConversationService = Depends(get_conversation_service),
    _: str = Depends(verify_token)
):
    """发送消息"""
    return await conversation_service.send_message(
        conversation_id,
        message["content"]
    )
```

### 4.2 数据库架构

```python
# openhands/app_server/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from openhands.core.config import settings


DATABASE_URL = settings.database.url

engine = create_async_engine(DATABASE_URL, echo=settings.database.echo)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
```

## 5. 文件存储架构

### 5.1 FileStore 接口

```python
# openhands/storage/file_store.py
from typing import List, Optional, IO
from abc import ABC, abstractmethod
from pathlib import Path


class FileStore(ABC):
    """文件存储接口"""

    @abstractmethod
    async def read_file(self, path: str) -> bytes:
        """读取文件"""
        pass

    @abstractmethod
    async def write_file(self, path: str, content: bytes) -> None:
        """写入文件"""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> None:
        """删除文件"""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        pass

    @abstractmethod
    async def list_files(self, directory: str) -> List[str]:
        """列出目录内容"""
        pass


class LocalFileStore(FileStore):
    """本地文件存储实现"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = "./data"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True, parents=True)

    async def read_file(self, path: str) -> bytes:
        file_path = self.base_dir / Path(path.lstrip("/"))
        with open(file_path, "rb") as f:
            return f.read()

    async def write_file(self, path: str, content: bytes) -> None:
        file_path = self.base_dir / Path(path.lstrip("/"))
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "wb") as f:
            f.write(content)

    async def delete_file(self, path: str) -> None:
        file_path = self.base_dir / Path(path.lstrip("/"))
        if file_path.exists():
            file_path.unlink()

    async def exists(self, path: str) -> bool:
        file_path = self.base_dir / Path(path.lstrip("/"))
        return file_path.exists()

    async def list_files(self, directory: str) -> List[str]:
        dir_path = self.base_dir / Path(directory.lstrip("/"))
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        return [str(f) for f in dir_path.iterdir()]


class MemoryFileStore(FileStore):
    """内存文件存储实现 (用于测试)"""

    def __init__(self):
        self.files = {}

    async def read_file(self, path: str) -> bytes:
        if path not in self.files:
            raise FileNotFoundError(f"文件未找到: {path}")
        return self.files[path]

    async def write_file(self, path: str, content: bytes) -> None:
        self.files[path] = content

    async def delete_file(self, path: str) -> None:
        if path in self.files:
            del self.files[path]

    async def exists(self, path: str) -> bool:
        return path in self.files

    async def list_files(self, directory: str) -> List[str]:
        prefix = directory.rstrip("/") + "/"
        return [
            f
            for f in self.files.keys()
            if f.startswith(prefix) and "/" not in f[len(prefix):]
        ]
```

## 6. 部署架构

### 6.1 Docker Compose 部署

```yaml
# docker-compose.yml
version: "3.8"

services:
  # 后端 API 服务
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: openhands-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://openhands:password@postgres:5432/openhands
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data

  # PostgreSQL 数据库
  postgres:
    image: postgres:15
    container_name: openhands-postgres
    environment:
      - POSTGRES_USER=openhands
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=openhands
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # 前端应用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: openhands-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

  # Redis 缓存
  redis:
    image: redis:7
    container_name: openhands-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 可选: Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: openhands-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 6.2 Kubernetes 部署

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openhands-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openhands-backend
  template:
    metadata:
      labels:
        app: openhands-backend
    spec:
      containers:
        - name: backend
          image: openhands/backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              value: postgresql://openhands:password@openhands-postgres:5432/openhands
            - name: LLM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: openhands-secrets
                  key: llm-api-key
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"

---

apiVersion: v1
kind: Service
metadata:
  name: openhands-backend
spec:
  selector:
    app: openhands-backend
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: openhands-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openhands-frontend
  template:
    metadata:
      labels:
        app: openhands-frontend
    spec:
      containers:
        - name: frontend
          image: openhands/frontend:latest
          ports:
            - containerPort: 3000
          env:
            - name: REACT_APP_API_BASE_URL
              value: http://openhands-backend:8000/api/v1
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"

---

apiVersion: v1
kind: Service
metadata:
  name: openhands-frontend
spec:
  selector:
    app: openhands-frontend
  ports:
    - port: 3000
      targetPort: 3000
  type: ClusterIP

---

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openhands-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
    - host: app.all-hands.dev
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: openhands-frontend
                port:
                  number: 3000
          - path: /api/v1
            pathType: Prefix
            backend:
              service:
                name: openhands-backend
                port:
                  number: 8000
```

## 7. 架构特点总结

### 7.1 核心优势

1. **模块化架构**：清晰的层次结构，易于扩展和维护
2. **云原生设计**：支持 Kubernetes 部署和容器化执行
3. **沙箱安全**：完整的安全隔离机制，确保代码执行安全
4. **多运行时支持**：支持 Docker、Kubernetes、本地运行时
5. **高性能**：异步设计，支持高并发处理
6. **可扩展性**：模块化设计，易于添加新功能

### 7.2 架构改进建议

1. **API 版本控制**：增强 API 版本控制机制
2. **监控与日志**：添加详细的应用监控和日志记录
3. **缓存优化**：实现响应缓存，提高性能
4. **异步处理**：增强异步任务处理机制
5. **安全增强**：添加更详细的安全措施

### 7.3 性能优化建议

1. **数据库优化**：添加查询缓存和优化
2. **代码优化**：实现更高效的算法和数据结构
3. **资源优化**：优化容器资源配置
4. **网络优化**：优化 API 响应大小和请求处理

---

这就是 OpenHands 项目的完整架构文档，包含了前端应用、智能体系统、后端服务和部署架构的详细分析。项目具有清晰的模块化设计，支持多种部署选项，并提供了完整的智能体管理和会话功能。