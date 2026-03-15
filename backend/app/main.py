"""
File: main.py
Công dụng: Entrypoint của FastAPI application
- Khởi tạo FastAPI instance (app = FastAPI(...))
- Gắn các Router (include_router())
  - /api/v1/chat
  - /api/v1/health
- Cấu hình CORS (để Frontend có thể gọi API)
- Cấu hình Middleware (logging, exception handling)
- Cấu hình startup/shutdown events (init DB, close connections)

Chạy bằng: uvicorn main:app --reload
"""
