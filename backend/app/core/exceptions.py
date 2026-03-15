"""
File: exceptions.py
Công dụng: Định nghĩa các exception class tùy chỉnh cho ứng dụng
- ChatNotFoundException: Không tìm thấy session chat
- DatabaseException: Lỗi database
- ExternalAPIException: Lỗi khi gọi API bên thứ 3 (Gemini, Cohere, Qdrant)
- ValidationException: Lỗi validate input
- RateLimitException: Vượt quá rate limit

Được sử dụng để throw exception từ Services, và handle trong Exception Handlers
"""
