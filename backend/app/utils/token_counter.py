"""
File: token_counter.py
Công dụng: Utility function đếm số token để tránh vượt context window của LLM
- count_tokens(): Đếm số token của một string text
- estimate_tokens(): Ước lượng số token (nếu không có tokenizer chính xác)
- is_within_limit(): Check text có vượt quá token limit hay không
- truncate_by_tokens(): Cắt text để đảm bảo không vượt token limit

Dùng trong RAG service để đảm bảo prompt không vượt context window của Gemini
"""
