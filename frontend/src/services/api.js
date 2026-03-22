/*
 * File: api.js
 * Công dụng: Cấu hình Axios instance để gọi API backend
 * - Base URL: lấy từ env var VITE_API_URL
 * - Headers: Content-Type: application/json
 * - Interceptors:
 *   - Request interceptor: thêm auth token (nếu cần)
 *   - Response interceptor: handle error responses
 * 
 * Export: apiClient instance
 * Usage: apiClient.get('/api/v1/chat'), apiClient.post('/api/v1/chat')
 */
