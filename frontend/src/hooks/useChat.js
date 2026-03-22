/*
 * File: useChat.js
 * Công dụng: Custom Hook quản lý state và logic chat
 * - State: messages (danh sách tin nhắn), loading, session_id, error
 * - Action: sendMessage (gửi tin nhắn, gọi API backend)
 * - Logic: handle response, update messages, manage session
 * - Handle error gracefully (show error toast)
 * 
 * Export: useChat() hook
 * Usage: const { messages, sendMessage, loading } = useChat();
 */
