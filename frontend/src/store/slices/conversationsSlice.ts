import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

// 定义会话类型
export interface Conversation {
  id: number;
  agent_id: number;
  name: string;
  description: string;
  config: any;
  status: string;
  created_at: string;
  updated_at: string;
}

// 定义状态类型
interface ConversationsState {
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: ConversationsState = {
  conversations: [],
  selectedConversation: null,
  loading: false,
  error: null,
};

// 异步操作 - 获取所有会话
export const fetchConversations = createAsyncThunk('conversations/fetchConversations', async () => {
  const response = await axios.get('/api/conversations');
  return response.data;
});

// 异步操作 - 获取智能体的会话
export const fetchConversationsByAgent = createAsyncThunk(
  'conversations/fetchConversationsByAgent',
  async (agentId: number) => {
    const response = await axios.get(`/api/conversations/agent/${agentId}`);
    return response.data;
  }
);

// 异步操作 - 创建会话
export const createConversation = createAsyncThunk(
  'conversations/createConversation',
  async (conversationData: Omit<Conversation, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await axios.post('/api/conversations', conversationData);
    return response.data;
  }
);

// 异步操作 - 更新会话
export const updateConversation = createAsyncThunk(
  'conversations/updateConversation',
  async ({ id, ...conversationData }: Conversation) => {
    const response = await axios.put(`/api/conversations/${id}`, conversationData);
    return response.data;
  }
);

// 异步操作 - 删除会话
export const deleteConversation = createAsyncThunk(
  'conversations/deleteConversation',
  async (id: number) => {
    await axios.delete(`/api/conversations/${id}`);
    return id;
  }
);

// 会话状态切片
const conversationsSlice = createSlice({
  name: 'conversations',
  initialState,
  reducers: {
    selectConversation: (state, action: PayloadAction<Conversation | null>) => {
      state.selectedConversation = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取所有会话
      .addCase(fetchConversations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConversations.fulfilled, (state, action: PayloadAction<Conversation[]>) => {
        state.loading = false;
        state.conversations = action.payload;
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取会话列表失败';
      })
      // 获取智能体的会话
      .addCase(fetchConversationsByAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConversationsByAgent.fulfilled, (state, action: PayloadAction<Conversation[]>) => {
        state.loading = false;
        state.conversations = action.payload;
      })
      .addCase(fetchConversationsByAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取智能体会话失败';
      })
      // 创建会话
      .addCase(createConversation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createConversation.fulfilled, (state, action: PayloadAction<Conversation>) => {
        state.loading = false;
        state.conversations.push(action.payload);
      })
      .addCase(createConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '创建会话失败';
      })
      // 更新会话
      .addCase(updateConversation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateConversation.fulfilled, (state, action: PayloadAction<Conversation>) => {
        state.loading = false;
        const index = state.conversations.findIndex(conv => conv.id === action.payload.id);
        if (index !== -1) {
          state.conversations[index] = action.payload;
        }
        if (state.selectedConversation?.id === action.payload.id) {
          state.selectedConversation = action.payload;
        }
      })
      .addCase(updateConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '更新会话失败';
      })
      // 删除会话
      .addCase(deleteConversation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteConversation.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false;
        state.conversations = state.conversations.filter(conv => conv.id !== action.payload);
        if (state.selectedConversation?.id === action.payload) {
          state.selectedConversation = null;
        }
      })
      .addCase(deleteConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '删除会话失败';
      });
  },
});

export const { selectConversation, clearError } = conversationsSlice.actions;

export default conversationsSlice.reducer;
