"""
File: chat_repo.py
Công dụng: Repository/DAO layer thao tác CRUD với PostgreSQL database
- create_session(): INSERT vào bảng chat_sessions
- get_session(): SELECT từ bảng chat_sessions
- create_message(): INSERT vào bảng chat_messages
- get_messages_by_session(): SELECT danh sách message của một session
- delete_message(): DELETE message từ database
- get_session_by_id(): Lấy thông tin chi tiết session

Tầng trừu tượng giữa Service layer và Database, dễ dàng swap database sau này
"""
