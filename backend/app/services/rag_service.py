"""
File: rag_service.py
Công dụng: Service layer chứa business logic chính của hệ thống RAG
- main_rag_pipeline(): Quy trình chính
  1. Nhận câu hỏi từ user
  2. Lấy embedding của câu hỏi
  3. Search Qdrant để lấy top K tài liệu liên quan
  4. Rerank kết quả với Cohere Rerank
  5. Ghép context vào prompt
  6. Gọi Gemini LLM để sinh text trả lời
  7. Trả về response + source links

- get_embeddings(): Gọi embedding model
- search_similar_documents(): Search vector database
- rerank_documents(): Sắp xếp lại kết quả theo relevance
- call_llm(): Gọi LLM để sinh câu trả lời

Là "Não bộ" của hệ thống
"""
