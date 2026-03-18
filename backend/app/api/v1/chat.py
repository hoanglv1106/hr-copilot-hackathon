import logging
from fastapi import APIRouter, HTTPException, Header, Depends
from sqlalchemy.orm import Session as DBSession

from app.schemas.chat_schema import ChatRequest, ChatResponse, ChatResponseData, SourceLink
from app.services.rag_service import RAGService
from app.services.history_service import HistoryService
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)

rag_service = RAGService()


@router.post("/", response_model=ChatResponse)
async def post_chat(
    request: ChatRequest,
    x_session_id: str = Header(..., description="Client UUID"),
    db: DBSession = Depends(get_db),
) -> ChatResponse:
    """
    Answer a question with multi-turn conversation support.

    Headers:
        X-Session-ID: UUID from client (required, format: UUID v4)

    Returns:
        ChatResponse with answer and source documents
    """
    try:
        logger.info(f"Session: {x_session_id[:8]}... | Message: {request.message[:60]}...")

        history_service = HistoryService(db)

        session = history_service.get_or_create_session(x_session_id)
        logger.info(f"Session initialized")

        history_service.save_message(x_session_id, "user", request.message)
        logger.info(f"User message saved")

        chat_history = history_service.get_chat_history(x_session_id, limit=5)
        logger.info(f"Retrieved {len(chat_history)} history messages")

        result = rag_service.answer_question(
            question=request.message,
            conversation_history=chat_history
        )
        logger.info(f"RAG response generated")

        assistant_answer = result.get("answer", "")
        history_service.save_message(x_session_id, "assistant", assistant_answer)
        logger.info(f"Assistant message saved")

        sources_list = [
            SourceLink(
                doc_name=src.get("doc_name", ""),
                page=src.get("page", 0),
                article=src.get("article", "")
            )
            for src in result.get("sources", [])
        ]

        response_data = ChatResponseData(
            answer=assistant_answer,
            sources=sources_list
        )

        response = ChatResponse(
            status="success",
            data=response_data
        )

        logger.info(f"Response sent to client")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/history")
async def get_history(
    x_session_id: str = Header(..., description="Client UUID"),
    limit: int = 100,
    db: DBSession = Depends(get_db),
):
    """
    Get full chat history for a session.

    Headers:
        X-Session-ID: UUID from client

    Query Parameters:
        limit: Maximum messages to retrieve (default: 100)

    Returns:
        Dictionary with session info and messages
    """
    try:
        logger.info(f"Session: {x_session_id[:8]}... | Retrieving history (limit={limit})")

        history_service = HistoryService(db)

        chat_history = history_service.get_chat_history(x_session_id, limit=limit)

        session_info = history_service.get_session_info(x_session_id)

        if not session_info:
            logger.warning(f"Session not found: {x_session_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Session not found: {x_session_id}"
            )

        logger.info(f"Retrieved {len(chat_history)} messages")

        return {
            "status": "success",
            "session": session_info,
            "messages": chat_history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health():
    """Health check endpoint for chat service"""
    return {"status": "ok", "message": "Chat service is running"}
