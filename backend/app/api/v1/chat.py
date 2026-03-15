"""
File: chat.py
Công dụng: Router xử lý các endpoint liên quan tới chat
- POST /v1/chat: Gửi câu hỏi, nhận câu trả lời từ RAG system
- GET /v1/chat/history/{session_id}: Lấy lịch sử chat của một phiên
- POST /v1/chat/sessions: Tạo phiên chat mới
- DELETE /v1/chat/{message_id}: Xóa một tin nhắn

Controller Layer: Validate request từ Frontend -> gọi Service -> trả response
"""
