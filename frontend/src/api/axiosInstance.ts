import axios from 'axios';

// 创建 axios 实例
const axiosInstance = axios.create({
  baseURL: '/',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    console.log('Request:', config);
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    console.log('Response:', response);
    return response;
  },
  (error) => {
    // 对响应错误做点什么
    console.error('Response Error:', error);
    return Promise.reject(error);
  }
);

export default axiosInstance;
