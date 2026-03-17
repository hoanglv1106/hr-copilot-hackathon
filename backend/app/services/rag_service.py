import json
import logging
from typing import Optional

from app.core.prompt_templates import HR_RAG_PROMPT
from app.integrations.rerank_client import CohereRerankService
from app.integrations.qdrant_client import QdrantService
from app.integrations.llm_client import GeminiService

logger = logging.getLogger(__name__)


class RAGService:
    """
    Orchestrates the 6-step RAG pipeline: Retrieve → Rerank → Format → Prompt → Generate → Parse.
    """

    def __init__(self):
        """Initialize RAG Service with integration services and pipeline parameters."""
        try:
            self.qdrant_service = QdrantService()
            self.cohere_service = CohereRerankService()
            self.gemini_service = GeminiService(temperature=0.2)

            self.retrieve_top_k = 10
            self.rerank_top_n = 3

            logger.info("RAGService initialized")

        except Exception as e:
            logger.error(f"Failed to initialize RAGService: {e}", exc_info=True)
            raise

    def answer_question(
        self,
        question: str,
        conversation_history: list[dict] = None
    ) -> dict:
        """
        Answer a question using RAG pipeline with multi-turn conversation support.

        Args:
            question: User's question
            conversation_history: List of previous messages for context: [{"role": "user"|"assistant", "content": "..."}, ...]

        Returns:
            Dictionary with "answer" and "sources" keys
        """
        try:
            logger.info(f"Processing: {question[:60]}...")

            history_str = self._build_history_string(conversation_history)

            try:
                retrieved_docs = self.qdrant_service.search(
                    query=question,
                    top_k=self.retrieve_top_k
                )
                logger.info(f"Retrieved {len(retrieved_docs)} documents")
            except Exception as e:
                logger.error(f"Qdrant search failed: {e}", exc_info=True)
                return self._no_result_response()

            if not retrieved_docs:
                logger.warning("No documents found")
                return self._no_result_response()

            try:
                doc_strings = [doc["content"] for doc in retrieved_docs]
                reranked_docs_strings = self.cohere_service.rerank(
                    query=question,
                    documents=doc_strings,
                    top_n=self.rerank_top_n
                )
                logger.info(f"Reranked to {len(reranked_docs_strings)} documents")
            except Exception as e:
                logger.error(f"Cohere rerank failed: {e}", exc_info=True)
                reranked_docs_strings = doc_strings[:self.rerank_top_n]

            try:
                top_docs = []
                for reranked_str in reranked_docs_strings:
                    for original_doc in retrieved_docs:
                        if original_doc["content"] == reranked_str:
                            top_docs.append(original_doc)
                            break

                if not top_docs:
                    logger.warning("No documents matched after reranking")
                    return self._no_result_response()
            except Exception as e:
                logger.error(f"Document mapping failed: {e}", exc_info=True)
                return self._no_result_response()

            try:
                context_str = self._format_context(top_docs)
                logger.info(f"Context formatted ({len(context_str)} chars)")
            except Exception as e:
                logger.error(f"Context formatting failed: {e}", exc_info=True)
                context_str = ""

            try:
                full_prompt = HR_RAG_PROMPT.format(
                    history=history_str,
                    context=context_str,
                    question=question
                )
                logger.info(f"Prompt built ({len(full_prompt)} chars)")
            except KeyError as e:
                logger.error(f"Template variable missing: {e}", exc_info=True)
                return {"answer": f"Prompt error: {e}", "sources": []}
            except Exception as e:
                logger.error(f"Prompt building failed: {e}", exc_info=True)
                return self._no_result_response()

            try:
                llm_response = self.gemini_service.generate(prompt=full_prompt)
                logger.info(f"LLM response generated ({len(llm_response)} chars)")
            except Exception as e:
                logger.error(f"LLM generation failed: {e}", exc_info=True)
                return {"answer": f"LLM error: {str(e)}", "sources": []}

            try:
                parsed_response = self._parse_json_response(llm_response)
                logger.info("Response parsed successfully")
                return parsed_response
            except Exception as e:
                logger.error(f"Response parsing failed: {e}", exc_info=True)
                return {"answer": "Error processing response", "sources": []}

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return {"answer": f"Error: {str(e)}", "sources": []}

    def _build_history_string(self, conversation_history: list[dict] = None) -> str:
        """
        Build formatted conversation history string from database messages.

        Args:
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}, ...]

        Returns:
            Formatted history string or empty string if no history
        """
        try:
            if not conversation_history or len(conversation_history) == 0:
                return ""

            history_parts = []

            for msg in conversation_history:
                try:
                    role = msg.get("role", "").lower().strip()
                    content = msg.get("content", "")

                    if role == "user":
                        role_label = "**Nhân viên**"
                    elif role == "assistant":
                        role_label = "**HR Copilot**"
                    else:
                        role_label = f"**{role.upper()}**"

                    formatted_msg = f"{role_label}: {content}"
                    history_parts.append(formatted_msg)

                except Exception as e:
                    logger.warning(f"Error processing message: {e}")
                    continue

            if not history_parts:
                return ""

            history_str = "\n".join(history_parts)
            logger.info(f"Formatted {len(history_parts)} history messages")

            return history_str

        except Exception as e:
            logger.error(f"Error building history: {e}", exc_info=True)
            return ""


    def _format_context(self, documents: list[dict]) -> str:
        """
        Format documents into a readable context string with metadata.

        Args:
            documents: List of documents with keys: content, metadata, score

        Returns:
            Formatted context string
        """
        try:
            context_parts = []

            for i, doc in enumerate(documents, 1):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                score = doc.get("score", 0)

                source = metadata.get("source", "Unknown")
                page = metadata.get("page", "?")

                section = f"""[Document {i}]
Source: {source}
Page: {page}
Relevance: {score:.2%}

{content}

---"""

                context_parts.append(section)

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Context formatting error: {e}", exc_info=True)
            return ""

    def _parse_json_response(self, response_text: str) -> dict:
        """
        Parse JSON response from LLM, removing markdown code blocks if present.

        Args:
            response_text: Response text from LLM

        Returns:
            Dictionary with "answer" and "sources" keys
        """
        try:
            cleaned = response_text.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

            if "answer" not in parsed:
                parsed["answer"] = ""
            if "sources" not in parsed:
                parsed["sources"] = []

            logger.debug("JSON parsed successfully")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"answer": "Error processing response", "sources": []}

    def _no_result_response(self) -> dict:
        """
        Return default response when no documents are found.
        """
        return {
            "answer": "Xin lỗi, tôi không tìm thấy thông tin này trong quy định hiện tại",
            "sources": []
        }
