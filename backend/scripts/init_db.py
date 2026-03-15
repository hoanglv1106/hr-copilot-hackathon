"""
File: init_db.py
Công dụng: Script khởi tạo database schema (chạy tay lần đầu setup)

Quy trình:
1. Kết nối tới PostgreSQL
2. Drop existing tables (nếu nhiệm vụ reset)
3. Create tables (ChatSession, ChatMessage) dựa trên SQLAlchemy models
4. Create indexes trên các fields tìm kiếm thường xuyên
5. Log thông tin kết quả

Chạy bằng: python scripts/init_db.py
"""
