
from datetime import datetime
from typing import Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session as DBSession

from app.models.history import Session, Message


class HistoryService:
    """Service for managing chat history and multi-turn conversations."""

    def __init__(self, db: DBSession):
        """Initialize with database session."""
        self.db = db

    def get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one."""
        try:
            stmt = select(Session).where(Session.id == session_id)
            existing_session = self.db.execute(stmt).scalars().first()

            if existing_session:
                existing_session.updated_at = datetime.utcnow()
                self.db.commit()
                return existing_session

            new_session = Session(id=session_id)
            self.db.add(new_session)
            self.db.commit()
            self.db.refresh(new_session)

            return new_session

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error in get_or_create_session: {str(e)}")

    def save_message(self, session_id: str, role: str, content: str) -> Message:
        """Save a message to the database."""
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role '{role}'. Must be 'user' or 'assistant'.")

        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content
            )
            self.db.add(message)

            stmt = select(Session).where(Session.id == session_id)
            session = self.db.execute(stmt).scalars().first()
            if session:
                session.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(message)

            return message

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error in save_message: {str(e)}")

    def get_chat_history(
        self,
        session_id: str,
        limit: int = 5
    ) -> list[dict]:
        """
        Get chat history for a session, ordered chronologically.

        Args:
            session_id: UUID identifying the session
            limit: Maximum number of message pairs to retrieve (default: 5)

        Returns:
            List of message dicts: [{"role": "user"|"assistant", "content": "..."}, ...]

        Raises:
            Exception: If database operation fails
        """
        try:
            stmt = (
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(desc(Message.created_at))
                .limit(limit * 2)
            )
            messages = self.db.execute(stmt).scalars().all()

            messages.reverse()

            history = [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in messages
            ]

            return history

        except Exception as e:
            raise Exception(f"Error in get_chat_history: {str(e)}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its associated messages."""
        try:
            stmt = select(Session).where(Session.id == session_id)
            session = self.db.execute(stmt).scalars().first()

            if not session:
                return False

            self.db.delete(session)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error in delete_session: {str(e)}")

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get information about a session including message count."""
        try:
            stmt = select(Session).where(Session.id == session_id)
            session = self.db.execute(stmt).scalars().first()

            if not session:
                return None

            count_stmt = select(Message).where(Message.session_id == session_id)
            message_count = len(self.db.execute(count_stmt).scalars().all())

            return {
                "id": session.id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": message_count
            }

        except Exception as e:
            raise Exception(f"Error in get_session_info: {str(e)}")
