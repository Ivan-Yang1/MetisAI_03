import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

// 定义消息类型
export interface Message {
  id: number;
  conversation_id: number;
  role: string;
  content: string;
  metadata: any;
  created_at: string;
  updated_at: string;
}

// 定义状态类型
interface MessagesState {
  messages: Message[];
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: MessagesState = {
  messages: [],
  loading: false,
  error: null,
};

// 异步操作 - 获取会话的消息
export const fetchMessagesByConversation = createAsyncThunk(
  'messages/fetchMessagesByConversation',
  async (conversationId: number) => {
    const response = await axios.get(`/api/conversations/${conversationId}/messages`);
    return response.data;
  }
);

// 异步操作 - 发送消息
export const sendMessage = createAsyncThunk(
  'messages/sendMessage',
  async (messageData: Omit<Message, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await axios.post('/api/conversations/messages', messageData);
    return response.data;
  }
);

// 异步操作 - 更新消息
export const updateMessage = createAsyncThunk(
  'messages/updateMessage',
  async ({ id, ...messageData }: Message) => {
    const response = await axios.put(`/api/conversations/messages/${id}`, messageData);
    return response.data;
  }
);

// 异步操作 - 删除消息
export const deleteMessage = createAsyncThunk(
  'messages/deleteMessage',
  async (id: number) => {
    await axios.delete(`/api/conversations/messages/${id}`);
    return id;
  }
);

// 消息状态切片
const messagesSlice = createSlice({
  name: 'messages',
  initialState,
  reducers: {
    clearMessages: (state) => {
      state.messages = [];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取会话的消息
      .addCase(fetchMessagesByConversation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMessagesByConversation.fulfilled, (state, action: PayloadAction<Message[]>) => {
        state.loading = false;
        state.messages = action.payload;
      })
      .addCase(fetchMessagesByConversation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取消息失败';
      })
      // 发送消息
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action: PayloadAction<Message>) => {
        state.loading = false;
        state.messages.push(action.payload);
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '发送消息失败';
      })
      // 更新消息
      .addCase(updateMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateMessage.fulfilled, (state, action: PayloadAction<Message>) => {
        state.loading = false;
        const index = state.messages.findIndex(msg => msg.id === action.payload.id);
        if (index !== -1) {
          state.messages[index] = action.payload;
        }
      })
      .addCase(updateMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '更新消息失败';
      })
      // 删除消息
      .addCase(deleteMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteMessage.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false;
        state.messages = state.messages.filter(msg => msg.id !== action.payload);
      })
      .addCase(deleteMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '删除消息失败';
      });
  },
});

export const { clearMessages, clearError } = messagesSlice.actions;

export default messagesSlice.reducer;
