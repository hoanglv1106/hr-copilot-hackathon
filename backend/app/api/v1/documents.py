import hashlib
import logging

from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.services.document_service import DocumentService
from app.models.document import DocumentRecord
from app.core.database import SessionLocal, get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)


class UploadResponse(BaseModel):
    """Response model for document upload."""

    status: str
    message: str


def calculate_file_hash(file_bytes: bytes) -> str:
    """
    Calculate SHA256 hash from file bytes.

    Args:
        file_bytes: File content

    Returns:
        Hexadecimal hash string
    """
    try:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_bytes)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash: {e}")
        return ""


async def process_document_background(document_id: str) -> None:
    """Background task to process document from database and embed into vector store."""
    try:
        db = SessionLocal()
        document_service = DocumentService()
        success = document_service.process_and_embed_document_from_db(document_id, db)

        if success:
            logger.info(f"Background processing completed for document {document_id}")
        else:
            logger.error(f"Background processing failed for document {document_id}")
    except Exception as e:
        logger.error(f"Error in background processing: {e}", exc_info=True)
    finally:
        db.close()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    background_tasks: BackgroundTasks = None,
    db: DBSession = Depends(get_db),
) -> UploadResponse:
    """
    Upload PDF document to database for processing and embedding.
    File is stored in PostgreSQL. Processing happens asynchronously in background.

    Args:
        file: PDF file from client
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        UploadResponse with status and message
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        logger.info(f"Received upload request for: {file.filename}")

        try:
            file_bytes = await file.read()
            logger.info(f"Read {len(file_bytes)} bytes from {file.filename}")
        except Exception as e:
            logger.error(f"Error reading file: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Error reading file")

        file_hash = calculate_file_hash(file_bytes)
        if not file_hash:
            raise HTTPException(status_code=500, detail="Error calculating file hash")

        logger.info(f"File hash calculated: {file_hash[:16]}...")

        try:
            existing_doc = db.query(DocumentRecord).filter(
                DocumentRecord.file_hash == file_hash
            ).first()

            if existing_doc:
                logger.info(f"Duplicate content detected for {file.filename}")
                return UploadResponse(
                    status="warning",
                    message="Tài liệu này đã tồn tại trong hệ thống (trùng khớp nội dung hoàn toàn). Không cần tải lên lại.",
                )
        except Exception as e:
            logger.warning(f"Error checking duplicates: {e}")

        try:
            doc_record = DocumentRecord(
                filename=file.filename,
                file_hash=file_hash,
                file_data=file_bytes
            )
            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)

            document_id = doc_record.id
            logger.info(f"Document record created in database: {document_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving document to database: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error saving document: {str(e)}"
            )

        logger.info(f"Adding background task for document processing: {document_id}")
        background_tasks.add_task(process_document_background, document_id)

        return UploadResponse(
            status="success",
            message="Đã tiếp nhận tài liệu. AI đang học và cập nhật dữ liệu ngầm...",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
