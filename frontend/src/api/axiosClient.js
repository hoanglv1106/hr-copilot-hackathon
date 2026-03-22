import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

/**
 * Khởi tạo Axios Client với cấu hình mặc định
 * - Base URL: Backend API v1
 * - Session ID: UUID lưu vào localStorage để tracking user
 * - Interceptor: Tự động gắn x-session-id header vào mọi request
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';
const SESSION_ID_KEY = 'hr_session_id';

/**
 * Hàm lấy hoặc tạo session ID
 * Nếu localStorage không có session_id thì tạo mới, ngược lại sử dụng cái cũ
 */
const getOrCreateSessionId = () => {
  let sessionId = localStorage.getItem(SESSION_ID_KEY);
  if (!sessionId) {
    sessionId = uuidv4();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
  }
  return sessionId;
};

// Khởi tạo Axios instance
const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * Tự động gắn x-session-id vào header của mọi request
 */
axiosClient.interceptors.request.use(
  (config) => {
    const sessionId = getOrCreateSessionId();
    config.headers['x-session-id'] = sessionId;
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor
 * Handle các lỗi HTTP response (optional)
 */
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log error để debugging
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export default axiosClient;
export { getOrCreateSessionId };
