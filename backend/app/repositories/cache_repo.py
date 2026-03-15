"""
File: cache_repo.py
Công dụng: Repository/DAO layer thao tác với Redis cache
- set_cache(): SET key-value vào Redis (với TTL)
  Ví dụ: cache user question -> embedding để tránh re-compute
- get_cache(): GET value từ Redis
- delete_cache(): DELETE key từ Redis
- exists_cache(): Check key có tồn tại hay không

Dùng để cache kết quả để tăng performance (VD: cache embedding của câu hỏi)
"""
