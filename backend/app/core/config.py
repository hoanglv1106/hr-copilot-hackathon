"""
File: config.py
Công dụng: Load và quản lý các biến cấu hình (Environment Variables)
- DATABASE_URL: Kết nối PostgreSQL
- REDIS_URL: Kết nối Redis
- QDRANT_URL: Kết nối Vector Database
- GEMINI_API_KEY: API key cho LLM Gemini
- COHERE_API_KEY: API key cho Cohere Rerank
- JWT_SECRET: Secret key cho authentication (nếu cần)
- LOG_LEVEL: Mức độ log (DEBUG, INFO, WARNING, ERROR)

Sử dụng Pydantic Settings để validate các biến môi trường
"""
