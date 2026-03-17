"""
SQLAlchemy models for chat history management.
Handles Session tracking and Message storage for multi-turn conversations.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Session(Base):
    """
    Represents a chat session identified by UUID from client.
    Each session tracks a user's conversation history.
    
    Attributes:
        id: String (Primary Key) - UUID sent by client in X-Session-ID header
        created_at: DateTime - Session creation timestamp
        updated_at: DateTime - Last activity timestamp
        messages: Relationship to Message objects in this session
    """
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    """UUID from client's X-Session-ID header (36 chars for UUID v4)"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    """Timestamp when session was created"""
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    """Timestamp of last message in this session"""

    # Relationship
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="select"
    )
    """List of messages in this session"""

    def __repr__(self) -> str:
        return f"<Session(id='{self.id}', created_at={self.created_at})>"


class Message(Base):
    """
    Represents a single message in a chat conversation.
    Stores both user questions and assistant responses.
    
    Attributes:
        id: Integer (Primary Key, Auto Increment)
        session_id: String (Foreign Key) - Reference to Session.id
        role: String - Either 'user' or 'assistant'
        content: Text - Full message content
        created_at: DateTime - When message was created
        session: Relationship back to Session object
    """
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    """Auto-incrementing primary key"""
    
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    """Foreign key referencing Session.id (UUID from client)"""
    
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    """Message role: 'user' or 'assistant' only"""
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    """Full message content (question or response)"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    """Timestamp when message was created"""

    # Relationship
    session: Mapped[Session] = relationship(
        "Session",
        back_populates="messages",
        lazy="select"
    )
    """Back-reference to the parent Session"""

    # Index for efficient querying by session_id and creation order
    __table_args__ = (
        Index("ix_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self) -> str:
        role_short = self.role[0].upper()
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, session='{self.session_id}', role='{role_short}', content='{content_preview}')>"

    def to_dict(self) -> dict:
        """Convert message to dictionary format for API responses."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
