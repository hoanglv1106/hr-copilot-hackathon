from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1 import chat as chat_router
from app.api.v1 import documents as documents_router
from app.core.database import init_db, close_db, SessionLocal  # Thêm SessionLocal vào đây
from app.models.document import DocumentRecord
from app.services.document_service import DocumentService
from qdrant_client import QdrantClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# LIFESPAN (QUẢN LÝ STARTUP & SHUTDOWN)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------------------------------------------------------
    # 1. LOGIC CHẠY LÚC STARTUP (Khởi tạo DB + Đồng bộ Qdrant)
    # ---------------------------------------------------------
    logger.info(" Application starting up...")
    try:
        init_db()
        logger.info(" Database initialized on startup")
    except Exception as e:
        logger.error(f" Failed to initialize database: {e}", exc_info=True)
        raise

    logger.info(" [STARTUP SYNC] Đang kiểm tra đồng bộ dữ liệu Postgres -> Qdrant...")
    db = SessionLocal()
    try:
        doc_service = DocumentService()
        qdrant_client = QdrantClient(url=doc_service.qdrant_url)
        
        # Lấy toàn bộ file đang có trong Postgres
        pg_docs = db.query(DocumentRecord).all()
        
        # Quét từng file, nếu Qdrant chưa có -> Bơm vào
        synced_count = 0
        for doc in pg_docs:
            is_exist = doc_service._check_duplicate_file(qdrant_client, doc.file_hash)
            
            if not is_exist:
                logger.info(f" Đang bơm tài liệu thiếu vào Qdrant: {doc.filename}")
                doc_service.process_and_embed_document_from_db(doc.id, db)
                synced_count += 1
                
        logger.info(f" [STARTUP SYNC] Đồng bộ hoàn tất. Đã bơm thêm {synced_count} tài liệu.")
    except Exception as e:
        logger.error(f" [STARTUP SYNC] Lỗi đồng bộ: {e}")
    finally:
        db.close()

    # ---------------------------------------------------------
    # 2. APP CHÍNH THỨC NHẬN REQUEST
    # ---------------------------------------------------------
    yield 
    
    # ---------------------------------------------------------
    # 3. LOGIC CHẠY LÚC SHUTDOWN (Tắt server)
    # ---------------------------------------------------------
    logger.info(" Application shutting down...")
    try:
        close_db()
        logger.info(" Database closed on shutdown")
    except Exception as e:
        logger.error(f" Failed to close database: {e}", exc_info=True)


# ============================================================================
# KHỞI TẠO ỨNG DỤNG FASTAPI (GẮN LIFESPAN VÀO ĐÂY)
# ============================================================================
app = FastAPI(
    title="HR Copilot API",
    description="HR Copilot - Employee Assistant Chatbot API",
    version="0.1.0",
    lifespan=lifespan  
)

# Cấu hình CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",    
        "http://127.0.0.1:3000",     
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Session-ID"],  
)

# Gắn các routers
app.include_router(chat_router.router, prefix="/api/v1")
app.include_router(documents_router.router, prefix="/api/v1")


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