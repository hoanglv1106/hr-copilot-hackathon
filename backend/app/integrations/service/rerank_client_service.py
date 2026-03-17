import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

try:
    import cohere # type: ignore
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("cohere package not installed")


class CohereRerankService:
    """Service for reranking documents based on relevance score."""

    def __init__(self):
        """Initialize Cohere Rerank Service with API key."""
        try:
            self.cohere_api_key = os.getenv("COHERE_API_KEY", "")

            if not COHERE_AVAILABLE:
                logger.warning("cohere package unavailable, using fallback")
                self.client = None
                return

            if not self.cohere_api_key:
                logger.warning("COHERE_API_KEY not set, using fallback")
                self.client = None
                return

            logger.info("Initializing Cohere Client")
            self.client = cohere.Client(api_key=self.cohere_api_key)
            logger.info("Cohere Client initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize Cohere Client: {e}")
            self.client = None

    def rerank(self, query: str, documents: list[str], top_n: int = 3) -> list[str]:
        """
        Rerank documents based on relevance to query.

        Args:
            query: Query text
            documents: List of documents to rerank
            top_n: Number of top documents to return (default: 3)

        Returns:
            List of reranked documents
        """
        try:
            if not documents:
                logger.warning("documents list is empty")
                return []

            if self.client is None:
                logger.info("Using fallback: returning top_n documents")
                return documents[:top_n]

            logger.info(f"Reranking {len(documents)} documents")

            results = self.client.rerank(
                model="rerank-multilingual-v3.0",
                query=query,
                documents=documents,
                top_n=top_n,
            )

            reranked_docs = [
                documents[result.index]
                for result in results.results
            ]

            logger.info(f"Reranking completed: {len(reranked_docs)} documents")
            return reranked_docs

        except Exception as e:
            logger.error(f"Reranking failed: {e}", exc_info=True)
            logger.info("Fallback: returning top_n documents")
            return documents[:top_n]
