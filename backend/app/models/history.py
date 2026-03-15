"""
File: history.py
Công dụng: Định nghĩa SQLAlchemy ORM models (Entity) ánh xạ xuống Database
- ChatSession: Bảng lưu thông tin phiên chat
  Columns: id, user_id, created_at, updated_at, title, status
  
- ChatMessage: Bảng lưu từng tin nhắn trong phiên chat
  Columns: id, session_id, role (user/assistant), content, created_at, 
           message_sources (JSON chứa thông tin nguồn tài liệu)

Được sử dụng bởi Repository layer để thao tác database
"""
