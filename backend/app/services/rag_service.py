"""
File: rag_service.py
Công dụng: Service layer chứa business logic chính của hệ thống RAG
- RAGService: Class chính orchestrate toàn bộ pipeline

Pipeline: Retrieve (Qdrant) → Rerank (Cohere) → Format Context → Prompting → Generate (Gemini) → Parse JSON

Là "Não bộ" của hệ thống
"""

import json
import logging
from typing import Optional

from app.core.prompt_templates import HR_RAG_PROMPT
from app.integrations.service.rerank_client_service import CohereRerankService
from app.integrations.service.qdrant_client_service import QdrantService
from app.integrations.service.gemini_llm_service import GeminiService

# ============================================================================
# SETUP
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# RAG SERVICE CLASS
# ============================================================================


class RAGService:
    """
    Service orchestrate toàn bộ RAG pipeline.
    
    Pipeline:
    1. Retrieve: Search Qdrant để lấy top 10 documents
    2. Rerank: Lọc với Cohere để lấy top 3 documents tốt nhất
    3. Format Context: Gom 3 docs thành chuỗi string rõ ràng với metadata
    4. Prompting: Đưa context + question vào HR_RAG_PROMPT
    5. Generate: Gọi GeminiService để sinh câu trả lời
    6. Parse JSON: Strip markdown, parse JSON response
    """

    def __init__(self):
        """
        Khởi tạo RAG Service.
        - Khởi tạo cả 3 integration services: Qdrant, Cohere, Gemini
        - Set thông số mặc định cho pipeline
        """
        try:
            logger.info("🔄 Khởi tạo RAGService...")

            # Khởi tạo services
            self.qdrant_service = QdrantService()
            logger.info("✅ QdrantService initialized")

            self.cohere_service = CohereRerankService()
            logger.info("✅ CohereRerankService initialized")

            self.gemini_service = GeminiService(temperature=0.2)
            logger.info("✅ GeminiService initialized")

            # Thông số mặc định
            self.retrieve_top_k = 10
            self.rerank_top_n = 3

            logger.info("✅ RAGService initialized successfully")

        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo RAGService: {e}", exc_info=True)
            raise

    def answer_question(self, question: str) -> dict:
        """
        Trả lời câu hỏi sử dụng RAG pipeline.

        Args:
            question (str): Câu hỏi từ user

        Returns:
            dict: {
                "answer": "Câu trả lời",
                "sources": [{"doc_name": "...", "page": X, "article": "..."}, ...]
            }
        """
        try:
            logger.info(f"📝 Processing question: {question}")

            # ================================================================
            # BƯỚC 1: RETRIEVE - Search Qdrant để lấy top 10 documents
            # ================================================================
            logger.info(f"[1/6] RETRIEVE: Searching Qdrant (top_k={self.retrieve_top_k})...")
            retrieved_docs = self.qdrant_service.search(
                query=question,
                top_k=self.retrieve_top_k
            )
            logger.info(f"✅ Retrieved {len(retrieved_docs)} documents")

            # Xử lý nếu không tìm thấy document nào
            if not retrieved_docs:
                logger.warning("⚠️  Không tìm thấy document nào")
                return self._no_result_response()

            # ================================================================
            # BƯỚC 2: RERANK - Lọc lại với Cohere để lấy top 3 documents
            # ================================================================
            logger.info(f"[2/6] RERANK: Reranking {len(retrieved_docs)} documents...")

            # Chuyển document objects thành list string để rerank
            doc_strings = [doc["content"] for doc in retrieved_docs]
            reranked_docs_strings = self.cohere_service.rerank(
                query=question,
                documents=doc_strings,
                top_n=self.rerank_top_n
            )
            logger.info(f"✅ Reranked to {len(reranked_docs_strings)} documents")

            # Map reranked strings back to original doc objects
            top_docs = []
            for reranked_str in reranked_docs_strings:
                # Tìm doc gốc từ content
                for original_doc in retrieved_docs:
                    if original_doc["content"] == reranked_str:
                        top_docs.append(original_doc)
                        break

            if not top_docs:
                logger.warning("⚠️  Sau rerank không còn document nào")
                return self._no_result_response()

            # ================================================================
            # BƯỚC 3: FORMAT CONTEXT - Gom documents thành chuỗi string
            # ================================================================
            logger.info(f"[3/6] FORMAT CONTEXT: Formatting {len(top_docs)} documents...")
            context_str = self._format_context(top_docs)
            logger.debug(f"   Context length: {len(context_str)} chars")

            # 
            print("\n" + "🚀"*15 + " DEBUG CONTEXT " + "🚀"*15)
            print(context_str)
            print("🚀"*37 + "\n")

            # ================================================================
            # BƯỚC 4: PROMPTING - Đưa question + context vào prompt template
            # ================================================================
            logger.info(f"[4/6] PROMPTING: Building prompt...")
            full_prompt = HR_RAG_PROMPT.format(
                question=question,
                context=context_str
            )
            logger.debug(f"   Prompt length: {len(full_prompt)} chars")

            # ================================================================
            # BƯỚC 5: GENERATE - Gọi Gemini LLM
            # ================================================================
            logger.info(f"[5/6] GENERATE: Calling Gemini LLM...")
            llm_response = self.gemini_service.generate(prompt=full_prompt)
            logger.info(f"✅ LLM response generated ({len(llm_response)} chars)")

            # ================================================================
            # BƯỚC 6: PARSE JSON - Parse response JSON từ LLM
            # ================================================================
            logger.info(f"[6/6] PARSE JSON: Parsing LLM response...")
            parsed_response = self._parse_json_response(llm_response)
            logger.info(f"✅ Response parsed successfully")

            
            logger.info(f"✅ Question answered successfully")
            return parsed_response

        except Exception as e:
            logger.error(f"❌ Lỗi trong RAG pipeline: {e}", exc_info=True)
            return {
                "answer": f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn: {str(e)}",
                "sources": []
            }

    def _format_context(self, documents: list[dict]) -> str:
        """
        Format danh sách documents thành chuỗi context rõ ràng.

        Args:
            documents: list[dict] với keys: content, metadata, score

        Returns:
            str: Formatted context string với metadata
        """
        context_parts = []

        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            score = doc.get("score", 0)

            # Trích xuất source info từ metadata
            source = metadata.get("source", "Không rõ")
            page = metadata.get("page", "?")

            # Format mỗi document
            section = f"""[Tài liệu {i}]
Nguồn: {source}
Trang: {page}
Độ liên quan: {score:.2%}

{content}

---"""

            context_parts.append(section)

        return "\n".join(context_parts)

    def _extract_sources(self, documents: list[dict]) -> list[dict]:
        """
        Trích xuất source information từ documents.

        Args:
            documents: list[dict] với metadata

        Returns:
            list[dict]: Danh sách sources với format: {"doc_name": "", "page": int, "article": ""}
        """
        sources = []

        for doc in documents[:self.rerank_top_n]:
            metadata = doc.get("metadata", {})
            source_dict = {
                "doc_name": metadata.get("source", "Không rõ").split("/")[-1],  # Lấy tên file
                "page": metadata.get("page", 0),
                "article": metadata.get("article", "Không rõ")
            }
            sources.append(source_dict)

        return sources

    def _parse_json_response(self, response_text: str) -> dict:
        """
        Parse JSON response từ LLM.
        - Strip bỏ markdown code blocks nếu có
        - Parse JSON safely
        - Return default dict if error

        Args:
            response_text (str): Response text từ LLM

        Returns:
            dict: {"answer": "", "sources": [...]}
        """
        try:
            # Strip markdown code blocks (```json...```)
            cleaned = response_text.strip()

            # Remove ```json at start
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Remove "```json"
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Remove "```"

            # Remove ``` at end
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            # Parse JSON
            parsed = json.loads(cleaned)

            # Validate structure
            if "answer" not in parsed:
                parsed["answer"] = ""
            if "sources" not in parsed:
                parsed["sources"] = []

            logger.debug(f"✅ JSON parsed successfully")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            logger.debug(f"   Response text: {response_text[:200]}...")

            return {
                "answer": "Xin lỗi, có lỗi khi xử lý phản hồi từ hệ thống.",
                "sources": []
            }

    def _no_result_response(self) -> dict:
        """
        Trả về response mặc định khi không tìm thấy document.

        Returns:
            dict: {"answer": "...", "sources": []}
        """
        return {
            "answer": "Xin lỗi, tôi không tìm thấy thông tin này trong quy định hiện tại",
            "sources": []
        }
