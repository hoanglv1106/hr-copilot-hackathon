
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1 import chat as chat_router
from app.core.database import init_db, close_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="HR Copilot API",
    description="HR Copilot - Employee Assistant Chatbot API",
    version="0.1.0",
)

# Cấu hình CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Session-ID"],  # ⭐ Allow custom X-Session-ID header
)

# Gắn các routers
app.include_router(chat_router.router, prefix="/api/v1")


# ============================================================================
# DATABASE LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event - initialize database
    """
    logger.info("🚀 Application starting up...")
    try:
        init_db()
        logger.info("✅ Database initialized on startup")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event - close database
    """
    logger.info("🛑 Application shutting down...")
    try:
        close_db()
        logger.info("✅ Database closed on shutdown")
    except Exception as e:
        logger.error(f"❌ Failed to close database: {e}", exc_info=True)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

# Endpoint test cơ bản - Health Check
@app.get("/health")
async def health_check():
    """
    Health check endpoint để kiểm tra xem API có chạy hay không
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "HR Copilot API is running successfully!"
        }
    )


# Endpoint ping đơn giản
@app.get("/ping")
async def ping():
    """
    Ping endpoint - trả về pong
    """
    return {"message": "pong"}


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "name": "HR Copilot API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
