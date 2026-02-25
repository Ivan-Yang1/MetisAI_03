import axios from 'axios';
import type { Conversation } from '../store/slices/conversationsSlice';

const API_BASE_URL = '/api/conversations';

// 获取所有会话
export const getConversations = async (): Promise<Conversation[]> => {
  const response = await axios.get<Conversation[]>(API_BASE_URL);
  return response.data;
};

// 获取单个会话
export const getConversation = async (id: number): Promise<Conversation> => {
  const response = await axios.get<Conversation>(`${API_BASE_URL}/${id}`);
  return response.data;
};

// 获取智能体的会话
export const getConversationsByAgent = async (agentId: number): Promise<Conversation[]> => {
  const response = await axios.get<Conversation[]>(`${API_BASE_URL}/agent/${agentId}`);
  return response.data;
};

// 创建会话
export const createConversation = async (conversationData: Omit<Conversation, 'id' | 'created_at' | 'updated_at'>): Promise<Conversation> => {
  const response = await axios.post<Conversation>(API_BASE_URL, conversationData);
  return response.data;
};

// 更新会话
export const updateConversation = async (id: number, conversationData: Partial<Conversation>): Promise<Conversation> => {
  const response = await axios.put<Conversation>(`${API_BASE_URL}/${id}`, conversationData);
  return response.data;
};

// 删除会话
export const deleteConversation = async (id: number): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/${id}`);
};

// 开始会话
export const startConversation = async (id: number): Promise<void> => {
  await axios.post(`${API_BASE_URL}/${id}/start`);
};

// 停止会话
export const stopConversation = async (id: number): Promise<void> => {
  await axios.post(`${API_BASE_URL}/${id}/stop`);
};

// 获取会话状态
export const getConversationStatus = async (id: number): Promise<any> => {
  const response = await axios.get(`${API_BASE_URL}/${id}/status`);
  return response.data;
};
