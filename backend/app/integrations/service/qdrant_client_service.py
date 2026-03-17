import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant Vector Database."""

    def __init__(self):
        """Initialize Qdrant Service with embeddings and vector store."""
        try:
            self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
            self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
            self.collection_name = "hr_policies"

            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")

            logger.info("Initializing GoogleGenerativeAIEmbeddings")
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001",
                google_api_key=self.gemini_api_key,
            )
            logger.info("Embedding model initialized")

            logger.info(f"Connecting to Qdrant at {self.qdrant_url}")
            self.client = QdrantClient(url=self.qdrant_url)

            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings,
            )
            logger.info("QdrantService initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize QdrantService: {e}", exc_info=True)
            raise

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search for document similarities with query.

        Args:
            query: Search query text
            top_k: Number of top results to return (default: 5)

        Returns:
            List of documents with metadata and relevance scores
        """
        try:
            logger.info(f"Searching: '{query}' (top_k={top_k})")

            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
            logger.info(f"Found {len(docs_with_scores)} results")

            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []

    def health_check(self) -> bool:
        """Check if Qdrant service is healthy."""
        try:
            self.client.get_collections()
            logger.info("Qdrant health check: OK")
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False