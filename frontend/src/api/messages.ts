import axios from 'axios';
import type { Message } from '../store/slices/messagesSlice';

const API_BASE_URL = '/api/conversations';

// 获取会话的消息
export const getMessagesByConversation = async (conversationId: number): Promise<Message[]> => {
  const response = await axios.get<Message[]>(`${API_BASE_URL}/${conversationId}/messages`);
  return response.data;
};

// 获取单个消息
export const getMessage = async (id: number): Promise<Message> => {
  const response = await axios.get<Message>(`${API_BASE_URL}/messages/${id}`);
  return response.data;
};

// 发送消息
export const sendMessage = async (messageData: Omit<Message, 'id' | 'created_at' | 'updated_at'>): Promise<Message> => {
  const response = await axios.post<Message>(`${API_BASE_URL}/messages`, messageData);
  return response.data;
};

// 更新消息
export const updateMessage = async (id: number, messageData: Partial<Message>): Promise<Message> => {
  const response = await axios.put<Message>(`${API_BASE_URL}/messages/${id}`, messageData);
  return response.data;
};

// 删除消息
export const deleteMessage = async (id: number): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/messages/${id}`);
};
