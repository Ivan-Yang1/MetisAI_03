import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

// 定义智能体类型
export interface Agent {
  id: number;
  name: string;
  type: string;
  description: string;
  config: any;
  status: string;
  created_at: string;
  updated_at: string;
}

// 定义状态类型
interface AgentsState {
  agents: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AgentsState = {
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,
};

// 异步操作 - 获取所有智能体
export const fetchAgents = createAsyncThunk('agents/fetchAgents', async () => {
  const response = await axios.get('/api/agents');
  return response.data;
});

// 异步操作 - 创建智能体
export const createAgent = createAsyncThunk(
  'agents/createAgent',
  async (agentData: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await axios.post('/api/agents', agentData);
    return response.data;
  }
);

// 异步操作 - 更新智能体
export const updateAgent = createAsyncThunk(
  'agents/updateAgent',
  async ({ id, ...agentData }: Agent) => {
    const response = await axios.put(`/api/agents/${id}`, agentData);
    return response.data;
  }
);

// 异步操作 - 删除智能体
export const deleteAgent = createAsyncThunk(
  'agents/deleteAgent',
  async (id: number) => {
    await axios.delete(`/api/agents/${id}`);
    return id;
  }
);

// 异步操作 - 运行智能体
export const runAgent = createAsyncThunk(
  'agents/runAgent',
  async ({ id, input }: { id: number; input: any }) => {
    const response = await axios.post(`/api/agents/${id}/run`, { input });
    return response.data;
  }
);

// 智能体状态切片
const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    selectAgent: (state, action: PayloadAction<Agent | null>) => {
      state.selectedAgent = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取所有智能体
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgents.fulfilled, (state, action: PayloadAction<Agent[]>) => {
        state.loading = false;
        state.agents = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取智能体列表失败';
      })
      // 创建智能体
      .addCase(createAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createAgent.fulfilled, (state, action: PayloadAction<Agent>) => {
        state.loading = false;
        state.agents.push(action.payload);
      })
      .addCase(createAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '创建智能体失败';
      })
      // 更新智能体
      .addCase(updateAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAgent.fulfilled, (state, action: PayloadAction<Agent>) => {
        state.loading = false;
        const index = state.agents.findIndex(agent => agent.id === action.payload.id);
        if (index !== -1) {
          state.agents[index] = action.payload;
        }
        if (state.selectedAgent?.id === action.payload.id) {
          state.selectedAgent = action.payload;
        }
      })
      .addCase(updateAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '更新智能体失败';
      })
      // 删除智能体
      .addCase(deleteAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteAgent.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false;
        state.agents = state.agents.filter(agent => agent.id !== action.payload);
        if (state.selectedAgent?.id === action.payload) {
          state.selectedAgent = null;
        }
      })
      .addCase(deleteAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '删除智能体失败';
      })
      // 运行智能体
      .addCase(runAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(runAgent.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(runAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '运行智能体失败';
      });
  },
});

export const { selectAgent, clearError } = agentsSlice.actions;

export default agentsSlice.reducer;
