import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // 백엔드 서버의 URL
  timeout: 1000,
});

export default api;
