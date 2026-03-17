"""
SQLAlchemy model for document storage in PostgreSQL.
Stores PDF files as binary data to enable stateless application.
"""

from datetime import datetime
import uuid

from sqlalchemy import String, LargeBinary, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocumentRecord(Base):
    """
    Represents a stored PDF document with file data and metadata.
    Prevents file system dependency - all data stored in PostgreSQL.

    Attributes:
        id: UUID (Primary Key) - Unique document identifier
        filename: String - Original filename
        file_hash: String - SHA256 hash for deduplication
        file_data: LargeBinary - PDF file content as bytes
        created_at: DateTime - Upload timestamp
    """
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    """UUID identifier for document"""

    filename: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    """Original PDF filename"""

    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )
    """SHA256 hash of file content for deduplication"""

    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    """PDF file content as bytes"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    """Timestamp when document was uploaded"""

    __table_args__ = (
        Index("idx_file_hash_created", "file_hash", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<DocumentRecord(id={self.id}, filename={self.filename}, hash={self.file_hash[:16]}...)>"
