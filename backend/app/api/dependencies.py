"""
File: dependencies.py
Công dụng: Chứa các hàm Dependency Injection dùng chung cho API
- get_db_session(): Trả về database session cho mỗi request
- get_cache(): Trả về Redis connection cho caching
Được sử dụng trong các endpoint bằng FastAPI Depends()

Ví dụ:
    @router.get("/chat")
    async def get_chat(session = Depends(get_db_session)):
        ...
"""
