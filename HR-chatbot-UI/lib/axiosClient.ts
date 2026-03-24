import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const SESSION_STORAGE_KEY = 'hr_session_id';


function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') {
    return uuidv4();
  }

  // ✅ Đọc từ localStorage mỗi lần request
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!sessionId) {
    sessionId = uuidv4();
    localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    console.log('[Axios] Created new session ID:', sessionId);
  } else {
    console.log('[Axios] Using existing session ID:', sessionId);
  }
  return sessionId;
}

/**
 * Create axios instance with interceptors
 */
const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});


axiosClient.interceptors.request.use(
  (config) => {
    // ✅ CRITICAL FIX: Respect explicitly set sessionId from caller
    // Check both lowercase and uppercase variants to handle different request origins
    const existingSessionId = 
      config.headers['x-session-id'] || 
      config.headers['X-Session-ID'];
    
    if (existingSessionId) {
      // ✅ Header already explicitly set by caller (e.g., chatService.ts)
      // Preserve it - DO NOT override with localStorage value
      console.log(
        `[Axios] Preserving explicit session ID from caller: ${existingSessionId}`
      );
      // Normalize to lowercase for consistency
      config.headers['x-session-id'] = existingSessionId;
      delete config.headers['X-Session-ID']; // Remove uppercase variant if present
    } else {
      // ✅ No session ID header provided by caller
      // Use fallback: load from localStorage or create new one
      const fallbackSessionId = getOrCreateSessionId();
      config.headers['x-session-id'] = fallbackSessionId;
      console.log(`[Axios] Using fallback session ID: ${fallbackSessionId}`);
    }
    
    console.log(`[Axios] Request to ${config.url} with x-session-id: ${config.headers['x-session-id']}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - handle errors
 */
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear session
      localStorage.removeItem(SESSION_STORAGE_KEY);
      console.warn('[Axios] Session cleared due to 401 Unauthorized');
    }
    return Promise.reject(error);
  }
);

export default axiosClient;