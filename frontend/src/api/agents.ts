import axios from 'axios';
import type { Agent } from '../store/slices/agentsSlice';

const API_BASE_URL = '/api/agents';

// 获取所有智能体
export const getAgents = async (): Promise<Agent[]> => {
  const response = await axios.get<Agent[]>(API_BASE_URL);
  return response.data;
};

// 获取单个智能体
export const getAgent = async (id: number): Promise<Agent> => {
  const response = await axios.get<Agent>(`${API_BASE_URL}/${id}`);
  return response.data;
};

// 创建智能体
export const createAgent = async (agentData: Omit<Agent, 'id' | 'created_at' | 'updated_at'>): Promise<Agent> => {
  const response = await axios.post<Agent>(API_BASE_URL, agentData);
  return response.data;
};

// 更新智能体
export const updateAgent = async (id: number, agentData: Partial<Agent>): Promise<Agent> => {
  const response = await axios.put<Agent>(`${API_BASE_URL}/${id}`, agentData);
  return response.data;
};

// 删除智能体
export const deleteAgent = async (id: number): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/${id}`);
};

// 运行智能体
export const runAgent = async (id: number, input: any): Promise<any> => {
  const response = await axios.post(`${API_BASE_URL}/${id}/run`, { input });
  return response.data;
};

// 获取智能体状态
export const getAgentStatus = async (id: number): Promise<any> => {
  const response = await axios.get(`${API_BASE_URL}/${id}/status`);
  return response.data;
};

// 停止智能体
export const stopAgent = async (id: number): Promise<void> => {
  await axios.post(`${API_BASE_URL}/${id}/stop`);
};
