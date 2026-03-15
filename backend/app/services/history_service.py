"""
File: history_service.py
Công dụng: Service layer quản lý lịch sử chat
- create_chat_session(): Tạo phiên chat mới
- get_chat_history(): Lấy lịch sử chat của một phiên
- save_message(): Lưu tin nhắn vào database
- delete_message(): Xóa một tin nhắn
- get_previous_context(): Lấy các message trước đó để build context

Tương tác với ChatRepository để thao tác với database
"""
