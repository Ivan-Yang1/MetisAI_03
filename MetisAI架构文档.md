# MetisAI 项目架构文档

## 项目概述

MetisAI 是一个基于 OpenHands 架构的 AI 驱动开发平台，专注于提供智能体执行环境和用户交互界面。系统支持多种部署方式，包括本地开发、容器化部署和云端服务。

**项目目标**：复刻 OpenHands 基本功能，添加注册登录和持久化存储，并部署到服务器。

**架构版本**：V1.0 (初始版本)

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
│  │ (/api/v1/*)  │ │  (事件流)    │ │              │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     应用服务层 (Application Services)              │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐    │
│  │ 核心业务逻辑            │  │ 会话管理与智能体控制器        │    │
│  │ (metisai/app/)           │  │ (MetisConversationService)   │    │
│  └──────────────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     核心服务层 (Core Services)                      │
│  ┌─────────────────┐ ┌────────────────────┐ ┌──────────────────┐  │
│  │ LLM 集成        │ │ 运行时管理         │ │ 存储系统         │  │
│  │ (litellm包装)    │ │ (Docker/Local)     │ │ (PostgreSQL)     │  │
│  └─────────────────┘ └────────────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     执行环境层 (Execution Environment)             │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐   │
│  │ Docker 容器      │ │ 本地执行         │ │ 沙箱执行服务器    │   │
│  │ (沙箱化运行)      │ │ (开发环境)       │ │ (ActionExecution)│   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘   │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐   │
│  │ Bash 会话        │ │ 文件操作         │ │ 代码执行         │   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈概览

| 层级 | 组件 | 技术栈 |
|------|------|--------|
| **前端** | React 应用 | React 19.2.3, TypeScript, Vite, Redux Toolkit |
| **后端** | API 服务器 | Python 3.12, FastAPI, SQLAlchemy, JWT |
| **LLM 集成** | LLM 抽象层 | litellm (≥1.74.3) |
| **数据库** | 存储系统 | PostgreSQL 15, SQLAlchemy ORM |
| **容器化** | 执行环境 | Docker, Docker Compose |
| **依赖管理** | 包管理 | Poetry (Python), npm (前端) |

## 2. 前端应用架构

### 2.1 项目结构

```
frontend/
├── package.json                 # 项目依赖
├── package-lock.json            # 依赖锁定文件
├── public/                      # 静态资源
└── src/
    ├── components/             # UI 组件
    │   ├── common/            # 通用组件
    │   ├── features/          # 功能组件
    │   └── layout/           # 布局组件
    ├── pages/                 # 页面组件
    │   ├── Auth/              # 认证页面
    │   ├── Dashboard/        # 仪表板
    │   ├── AgentManagement/  # 智能体管理
    │   ├── Conversations/    # 会话
    │   └── Settings/         # 设置
    ├── services/             # API 服务
    │   ├── api/             # REST API 客户端
    │   ├── websocket/       # WebSocket 客户端
    │   └── auth/            # 认证服务
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

#### 2.2.1 认证页面

```javascript
// src/pages/Auth/Login.jsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { login } from '../../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const resultAction = await dispatch(login({ email, password }));
      if (login.fulfilled.match(resultAction)) {
        navigate('/dashboard');
      } else {
        setError(resultAction.payload?.message || '登录失败');
      }
    } catch (err) {
      setError('登录过程中出现错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h1>MetisAI 登录</h1>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">邮箱</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
        <div className="auth-links">
          <a href="/register">注册新账户</a>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

#### 2.2.2 智能体管理界面

```javascript
// src/pages/AgentManagement/AgentList.jsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAgents, startAgent, stopAgent, deleteAgent } from '../../store/slices/agentsSlice';
import { AgentCard } from '../../components/features';

const AgentList = () => {
  const dispatch = useDispatch();
  const { list: agents, loading, error } = useSelector((state) => state.agents);

  useEffect(() => {
    dispatch(fetchAgents());
  }, [dispatch]);

  const handleStartAgent = (agentId) => {
    dispatch(startAgent(agentId));
  };

  const handleStopAgent = (agentId) => {
    dispatch(stopAgent(agentId));
  };

  const handleDeleteAgent = (agentId) => {
    if (window.confirm('确定要删除此智能体吗？')) {
      dispatch(deleteAgent(agentId));
    }
  };

  return (
    <div className="agent-list">
      <div className="agent-list-header">
        <h1>智能体管理</h1>
        <button className="create-agent-btn">创建智能体</button>
      </div>
      {loading ? (
        <div className="loading">加载中...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
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

#### 2.2.3 会话管理界面

```javascript
// src/pages/Conversations/ConversationPanel.jsx
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchMessages, sendMessage } from '../../store/slices/messagesSlice';
import { ChatMessage, ChatInput } from '../../components/features';

const ConversationPanel = ({ conversationId }) => {
  const dispatch = useDispatch();
  const [inputText, setInputText] = useState('');
  const { messages, loading, error } = useSelector((state) => state.messages);

  useEffect(() => {
    if (conversationId) {
      dispatch(fetchMessages(conversationId));
    }
  }, [dispatch, conversationId]);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    dispatch(sendMessage({ conversationId, content: inputText }));
    setInputText('');
  };

  return (
    <div className="conversation-panel">
      <div className="messages-container">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          messages.map(message => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
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
// src/store/slices/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authApi } from '../../services/api';

export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials);
      localStorage.setItem('token', response.data.token);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: '登录失败' });
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authApi.register(userData);
      localStorage.setItem('token', response.data.token);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: '注册失败' });
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    localStorage.removeItem('token');
    return {};
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || '登录失败';
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message || '注册失败';
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
```

### 2.4 API 集成架构

```javascript
// src/services/api/index.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

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

// 认证 API
export const authApi = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
};

// 智能体管理 API
export const agentsApi = {
  getAgents: () => api.get('/agents'),
  getAgentById: (id) => api.get(`/agents/${id}`),
  createAgent: (data) => api.post('/agents', data),
  updateAgent: (id, data) => api.put(`/agents/${id}`, data),
  deleteAgent: (id) => api.delete(`/agents/${id}`),
  startAgent: (id) => api.post(`/agents/${id}/start`),
  stopAgent: (id) => api.post(`/agents/${id}/stop`),
};

// 会话管理 API
export const conversationsApi = {
  getConversations: () => api.get('/conversations'),
  getConversationById: (id) => api.get(`/conversations/${id}`),
  createConversation: (data) => api.post('/conversations', data),
  deleteConversation: (id) => api.delete(`/conversations/${id}`),
  getMessages: (conversationId) => api.get(`/conversations/${conversationId}/messages`),
  sendMessage: (conversationId, content) =>
    api.post(`/conversations/${conversationId}/messages`, { content }),
};

// 设置 API
export const settingsApi = {
  getSettings: () => api.get('/settings'),
  updateSettings: (data) => api.put('/settings', data),
  getSecrets: () => api.get('/secrets'),
  createSecret: (data) => api.post('/secrets', data),
  deleteSecret: (id) => api.delete(`/secrets/${id}`),
};

export default api;
```

## 3. 后端架构

### 3.1 API 服务器架构

```python
# metisai/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from metisai.app.database import get_db
from metisai.app.models.user import User
from metisai.app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from metisai.app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentStatusResponse
)
from metisai.app.services.auth_service import AuthService
from metisai.app.services.agent_service import AgentService
from metisai.app.services.conversation_service import MetisConversationService
from metisai.core.config import settings


app = FastAPI(title="MetisAI API", version="1.0.0")

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


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    """获取当前用户"""
    auth_service = AuthService(db)
    token = credentials.credentials
    user = await auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    return user


# 依赖注入
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """获取认证服务"""
    return AuthService(db)


def get_agent_service(db: AsyncSession = Depends(get_db)) -> AgentService:
    """获取智能体服务"""
    return AgentService(db)


def get_conversation_service(db: AsyncSession = Depends(get_db)) -> MetisConversationService:
    """获取会话服务"""
    return MetisConversationService(db)


# 认证接口
@app.post("/api/v1/auth/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """注册新用户"""
    return await auth_service.register(user_data)


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登录"""
    return await auth_service.login(user_data)


@app.post("/api/v1/auth/logout", status_code=204)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # 可选：在数据库中标记令牌为已过期
    return {}


@app.get("/api/v1/auth/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取用户信息"""
    return current_user


# 智能体管理接口
@app.get("/api/v1/agents", response_model=list[AgentResponse])
async def list_agents(
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """获取智能体列表"""
    return await agent_service.get_all_agents(current_user.id)


@app.get("/api/v1/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """获取智能体详情"""
    agent = await agent_service.get_agent(agent_id, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    return agent


@app.post("/api/v1/agents", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """创建智能体"""
    return await agent_service.create_agent(agent_data, current_user.id)


@app.put("/api/v1/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """更新智能体"""
    agent = await agent_service.update_agent(agent_id, agent_data, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="智能体不存在")
    return agent


@app.delete("/api/v1/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """删除智能体"""
    deleted = await agent_service.delete_agent(agent_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="智能体不存在")


@app.post("/api/v1/agents/{agent_id}/start", response_model=AgentStatusResponse)
async def start_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """启动智能体"""
    await agent_service.start_agent(agent_id, current_user.id)
    return {"status": "running"}


@app.post("/api/v1/agents/{agent_id}/stop", response_model=AgentStatusResponse)
async def stop_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user)
):
    """停止智能体"""
    await agent_service.stop_agent(agent_id, current_user.id)
    return {"status": "stopped"}


# 会话管理接口
@app.get("/api/v1/conversations", response_model=list)
async def list_conversations(
    conversation_service: MetisConversationService = Depends(get_conversation_service),
    current_user: User = Depends(get_current_user)
):
    """获取会话列表"""
    return await conversation_service.get_conversations(current_user.id)


@app.post("/api/v1/conversations", status_code=201)
async def create_conversation(
    conversation_service: MetisConversationService = Depends(get_conversation_service),
    current_user: User = Depends(get_current_user)
):
    """创建新会话"""
    return await conversation_service.create_conversation(current_user.id)


@app.get("/api/v1/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    conversation_service: MetisConversationService = Depends(get_conversation_service),
    current_user: User = Depends(get_current_user)
):
    """获取会话消息"""
    return await conversation_service.get_messages(conversation_id, current_user.id)


@app.post("/api/v1/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: dict,
    conversation_service: MetisConversationService = Depends(get_conversation_service),
    current_user: User = Depends(get_current_user)
):
    """发送消息"""
    return await conversation_service.send_message(
        conversation_id,
        message["content"],
        current_user.id
    )
```

### 3.2 认证服务

```python
# metisai/app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import JWTError, jwt

from metisai.app.models.user import User
from metisai.app.schemas.auth import UserCreate, UserLogin, TokenResponse
from metisai.core.config import settings


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.auth.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm)
        return encoded_jwt

    async def register(self, user_data: UserCreate) -> TokenResponse:
        """注册新用户"""
        # 检查邮箱是否已存在
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("邮箱已被注册")

        # 创建新用户
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            password=hashed_password,
            name=user_data.name,
            is_active=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # 生成访问令牌
        access_token = self.create_access_token(data={"sub": str(user.id)})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        )

    async def login(self, user_data: UserLogin) -> TokenResponse:
        """用户登录"""
        # 查找用户
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()
        if not user or not self.verify_password(user_data.password, user.password):
            raise ValueError("邮箱或密码错误")

        # 生成访问令牌
        access_token = self.create_access_token(data={"sub": str(user.id)})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        )

    async def get_user_from_token(self, token: str) -> Optional[User]:
        """从令牌获取用户"""
        try:
            payload = jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
        except JWTError:
            return None

        result = await self.db.execute(select(User).where(User.id == UUID(user_id)))
        return result.scalar_one_or_none()
```

### 3.3 数据库架构

```python
# metisai/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from metisai.core.config import settings


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


# metisai/app/models/user.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from metisai.app.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self):
        return f"<User {self.email}>"


# metisai/app/models/agent.py
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from metisai.app.database import Base


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
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    config: Mapped[dict] = mapped_column(JSON)
    status: Mapped[AgentStatus] = mapped_column(
        String(50),
        default=AgentStatus.STOPPED
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    user = relationship("User", backref="agents")

    def __repr__(self):
        return f"<Agent {self.name}>"


# metisai/app/models/conversation.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from metisai.app.database import Base


class Conversation(Base):
    """会话模型"""
    __tablename__ = 'conversations'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    agent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('agents.id'))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    user = relationship("User", backref="conversations")
    agent = relationship("Agent", backref="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.id}>"


class Message(Base):
    """消息模型"""
    __tablename__ = 'messages'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey('conversations.id'))
    role: Mapped[str] = mapped_column(String(50))  # user, assistant
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id}>"
```

### 3.4 智能体服务

```python
# metisai/app/services/agent_service.py
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from metisai.app.models.agent import Agent, AgentStatus
from metisai.app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    """智能体服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_agents(self, user_id: UUID) -> List[Agent]:
        """获取用户的所有智能体"""
        result = await self.db.execute(
            select(Agent).where(Agent.user_id == user_id, Agent.is_active == True)
        )
        return result.scalars().all()

    async def get_agent(self, agent_id: str, user_id: UUID) -> Optional[Agent]:
        """获取智能体详情"""
        result = await self.db.execute(
            select(Agent).where(
                Agent.id == UUID(agent_id),
                Agent.user_id == user_id,
                Agent.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def create_agent(self, agent_data: AgentCreate, user_id: UUID) -> Agent:
        """创建智能体"""
        agent = Agent(
            user_id=user_id,
            name=agent_data.name,
            description=agent_data.description,
            config=agent_data.config,
            status=AgentStatus.STOPPED
        )
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def update_agent(self, agent_id: str, agent_data: AgentUpdate, user_id: UUID) -> Optional[Agent]:
        """更新智能体"""
        agent = await self.get_agent(agent_id, user_id)
        if not agent:
            return None

        for key, value in agent_data.dict(exclude_unset=True).items():
            setattr(agent, key, value)

        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def delete_agent(self, agent_id: str, user_id: UUID) -> bool:
        """删除智能体"""
        agent = await self.get_agent(agent_id, user_id)
        if not agent:
            return False

        agent.is_active = False
        await self.db.commit()
        return True

    async def start_agent(self, agent_id: str, user_id: UUID) -> None:
        """启动智能体"""
        agent = await self.get_agent(agent_id, user_id)
        if not agent:
            raise ValueError("智能体不存在")

        if agent.status != AgentStatus.STOPPED:
            raise ValueError("智能体状态无效")

        agent.status = AgentStatus.STARTING
        await self.db.commit()

        try:
            # 启动逻辑...
            agent.status = AgentStatus.RUNNING
            await self.db.commit()
        except Exception as e:
            agent.status = AgentStatus.ERROR
            await self.db.commit()
            raise

    async def stop_agent(self, agent_id: str, user_id: UUID) -> None:
        """停止智能体"""
        agent = await self.get_agent(agent_id, user_id)
        if not agent:
            raise ValueError("智能体不存在")

        if agent.status != AgentStatus.RUNNING:
            raise ValueError("智能体状态无效")

        agent.status = AgentStatus.STOPPING
        await self.db.commit()

        try:
            # 停止逻辑...
            agent.status = AgentStatus.STOPPED
            await self.db.commit()
        except Exception as e:
            agent.status = AgentStatus.ERROR
            await self.db.commit()
            raise
```

### 3.5 会话服务

```python
# metisai/app/services/conversation_service.py
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from metisai.app.models.conversation import Conversation, Message


class MetisConversationService:
    """会话服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_conversations(self, user_id: UUID) -> List[Conversation]:
        """获取用户的所有会话"""
        result = await self.db.execute(
            select(Conversation).where(Conversation.user_id == user_id)
        )
        return result.scalars().all()

    async def get_conversation(self, conversation_id: str, user_id: UUID) -> Optional[Conversation]:
        """获取会话详情"""
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == UUID(conversation_id),
                Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def create_conversation(self, user_id: UUID) -> Conversation:
        """创建新会话"""
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def delete_conversation(self, conversation_id: str, user_id: UUID) -> bool:
        """删除会话"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()
        return True

    async def get_messages(self, conversation_id: str, user_id: UUID) -> List[Message]:
        """获取会话消息"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("会话不存在")

        result = await self.db.execute(
            select(Message).where(
                Message.conversation_id == UUID(conversation_id)
            ).order_by(Message.timestamp)
        )
        return result.scalars().all()

    async def send_message(self, conversation_id: str, content: str, user_id: UUID) -> Message:
        """发送消息"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("会话不存在")

        # 保存用户消息
        user_message = Message(
            conversation_id=UUID(conversation_id),
            role="user",
            content=content
        )
        self.db.add(user_message)
        await self.db.commit()

        # 生成智能体响应
        # 这里应该调用 LLM 服务生成响应
        # 暂时使用占位符
        assistant_message = Message(
            conversation_id=UUID(conversation_id),
            role="assistant",
            content="这是智能体的响应..."
        )
        self.db.add(assistant_message)
        await self.db.commit()
        await self.db.refresh(assistant_message)

        return assistant_message
```

### 3.6 运行时管理架构

```python
# metisai/runtime/manager.py
from typing import Optional
from abc import ABC, abstractmethod

from metisai.core.config import settings
from metisai.runtime.impl.docker import DockerRuntime
from metisai.runtime.impl.local import LocalRuntime


class RuntimeManager:
    """运行时管理器 - 管理不同类型的运行时环境"""

    def __init__(self):
        self._runtimes = {
            'docker': DockerRuntime(),
            'local': LocalRuntime(),
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


class LocalRuntime(BaseRuntime):
    """本地运行时实现"""

    async def start_session(self, config: dict) -> str:
        """启动本地会话"""
        # 生成会话 ID
        import uuid
        session_id = str(uuid.uuid4())
        # 初始化本地环境
        # ...
        return session_id

    async def execute_command(self, session_id: str, command: str) -> dict:
        """在本地执行命令"""
        import subprocess
        import json
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "命令执行超时",
                "returncode": 1
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": 1
            }

    async def stop_session(self, session_id: str) -> None:
        """停止本地会话"""
        # 清理本地环境
        # ...
        pass


class DockerRuntime(BaseRuntime):
    """Docker 运行时实现"""

    async def start_session(self, config: dict) -> str:
        """启动 Docker 容器"""
        # 实现 Docker 容器启动逻辑
        # ...
        return "docker-session-id"

    async def execute_command(self, session_id: str, command: str) -> dict:
        """在 Docker 容器中执行命令"""
        # 实现 Docker 命令执行逻辑
        # ...
        return {
            "stdout": "Docker 命令输出",
            "stderr": "",
            "returncode": 0
        }

    async def stop_session(self, session_id: str) -> None:
        """停止 Docker 容器"""
        # 实现 Docker 容器停止逻辑
        # ...
        pass
```

### 3.7 配置管理

```python
# metisai/core/config.py
from pydantic_settings import BaseSettings
from typing import List


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str = "postgresql+asyncpg://admin:password@localhost:5432/metisai"
    echo: bool = False


class AuthSettings(BaseSettings):
    """认证配置"""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class CorsSettings(BaseSettings):
    """CORS 配置"""
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class RuntimeSettings(BaseSettings):
    """运行时配置"""
    default_type: str = "local"


class Settings(BaseSettings):
    """应用配置"""
    project_name: str = "MetisAI"
    version: str = "1.0.0"
    description: str = "MetisAI 智能体平台"
    
    database: DatabaseSettings = DatabaseSettings()
    auth: AuthSettings = AuthSettings()
    cors: CorsSettings = CorsSettings()
    runtime: RuntimeSettings = RuntimeSettings()


settings = Settings()
```

## 4. 部署架构

### 4.1 Docker Compose 部署

```yaml
# docker-compose.yml
version: "3.8"

services:
  # 后端 API 服务
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: metisai-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:password@postgres:5432/metisai
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data

  # PostgreSQL 数据库
  postgres:
    image: postgres:15
    container_name: metisai-postgres
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=metisai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # 前端应用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: metisai-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

  # Redis 缓存
  redis:
    image: redis:7
    container_name: metisai-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: metisai-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/certs:/etc/nginx/certs
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 4.2 服务器部署步骤

1. **准备服务器环境**
   - 安装 Docker 和 Docker Compose
   - 配置防火墙，开放 80、443 端口

2. **配置部署文件**
   - 复制 `docker-compose.yml` 到服务器
   - 创建 `nginx` 目录，配置 `nginx.conf`
   - 准备 SSL 证书（可选，用于 HTTPS）

3. **启动服务**
   - 运行 `docker-compose up -d`
   - 检查服务状态 `docker-compose ps`

4. **初始化数据库**
   - 运行 `docker-compose exec backend python -m metisai.app.database init_db`

5. **配置域名**
   - 将域名指向服务器 IP
   - 配置 Nginx 反向代理

6. **测试部署**
   - 访问前端应用 `http://your-domain.com`
   - 测试注册登录功能
   - 测试智能体管理和会话功能

### 4.3 环境变量配置

创建 `.env` 文件，配置以下环境变量：

```
# 数据库配置
DATABASE_URL=postgresql+asyncpg://admin:password@postgres:5432/metisai

# 认证配置
SECRET_KEY=your-secret-key-here

# 前端配置
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# 运行时配置
RUNTIME_TYPE=docker  # 可选: local, docker
```

## 5. 架构特点总结

### 5.1 核心优势

1. **模块化架构**：清晰的层次结构，易于扩展和维护
2. **完整的认证系统**：支持用户注册、登录和会话管理
3. **多运行时支持**：支持本地和 Docker 运行时
4. **高性能**：异步设计，支持高并发处理
5. **可扩展性**：模块化设计，易于添加新功能
6. **安全性**：完整的认证和授权机制

### 5.2 架构改进建议

1. **API 版本控制**：增强 API 版本控制机制
2. **监控与日志**：添加详细的应用监控和日志记录
3. **缓存优化**：实现响应缓存，提高性能
4. **异步处理**：增强异步任务处理机制
5. **安全增强**：添加更详细的安全措施
6. **CI/CD 集成**：实现自动化部署和测试

### 5.3 性能优化建议

1. **数据库优化**：添加查询缓存和优化
2. **代码优化**：实现更高效的算法和数据结构
3. **资源优化**：优化容器资源配置
4. **网络优化**：优化 API 响应大小和请求处理
5. **负载均衡**：添加负载均衡机制，支持水平扩展

---

## 6. 实施路线图

### 6.1 阶段一：基础架构搭建
- 初始化项目结构
- 配置开发环境
- 实现基本的目录结构

### 6.2 阶段二：后端核心功能
- 实现数据库模型
- 开发认证系统
- 实现智能体管理 API
- 实现会话管理 API

### 6.3 阶段三：前端界面开发
- 实现登录注册页面
- 开发智能体管理界面
- 开发会话管理界面
- 实现状态管理

### 6.4 阶段四：运行时实现
- 实现本地运行时
- 实现 Docker 运行时
- 测试运行时功能

### 6.5 阶段五：部署与测试
- 配置 Docker Compose
- 部署到服务器
- 测试完整功能
- 优化性能

### 6.6 阶段六：扩展与优化
- 添加更多运行时支持
- 实现高级功能
- 优化用户体验
- 增强安全性

---

## 7. 技术栈依赖

| 类别 | 技术/库 | 版本 | 用途 |
|------|---------|------|------|
| **前端** | React | 19.2.3 | 前端框架 |
| | TypeScript | 5.4.5 | 类型系统 |
| | Redux Toolkit | 2.2.3 | 状态管理 |
| | React Router | 6.22.3 | 路由管理 |
| | Axios | 1.6.8 | HTTP 客户端 |
| | Vite | 5.2.0 | 构建工具 |
| **后端** | Python | 3.12 | 后端语言 |
| | FastAPI | 0.109.2 | API 框架 |
| | SQLAlchemy | 2.0.27 | ORM |
| | PostgreSQL | 15 | 数据库 |
| | Pydantic | 2.6.1 | 数据验证 |
| | JWT | 2.8.0 | 认证令牌 |
| | passlib | 1.7.4 | 密码哈希 |
| **容器化** | Docker | 20.10+ | 容器运行时 |
| | Docker Compose | 1.29+ | 容器编排 |
| **依赖管理** | Poetry | 1.8.3 | Python 包管理 |
| | npm | 10.5.0 | 前端包管理 |

---

## 8. 安全考虑

1. **密码安全**：使用 bcrypt 进行密码哈希
2. **令牌安全**：使用 JWT 进行认证，设置合理的过期时间
3. **输入验证**：对所有用户输入进行严格验证
4. **权限控制**：实现基于用户的权限管理
5. **数据加密**：敏感数据加密存储
6. **CORS 配置**：合理配置 CORS 策略
7. **SQL 注入防护**：使用 ORM 和参数化查询
8. **XSS 防护**：对用户输入进行过滤和转义
9. **CSRF 防护**：实现 CSRF 令牌验证
10. **安全头部**：设置适当的安全 HTTP 头部

---

## 9. 总结

MetisAI 项目架构基于 OpenHands 的设计理念，结合了现代 web 开发的最佳实践。通过清晰的分层架构和模块化设计，实现了一个功能完整、性能优异的智能体平台。项目支持用户注册登录、智能体管理、会话管理等核心功能，并提供了多种运行时环境选择。

通过 Docker Compose 部署，MetisAI 可以快速部署到服务器，为用户提供稳定的智能体服务。未来可以通过扩展运行时支持、添加更多功能模块和优化性能，进一步提升平台的能力和用户体验。