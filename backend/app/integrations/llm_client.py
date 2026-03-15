"""
File: llm_client.py
Công dụng: Adapter gọi API LLM (Google Gemini)
- initialize_llm(): Khởi tạo client kết nối tới Gemini API
- generate_text(): Gọi API Gemini để sinh text
  Input: prompt (chứa system prompt + context + user question)
  Output: Generated response từ LLM
- call_with_retry(): Gọi API với retry logic (nếu fail thì retry 3 lần)

Bọc API của bên thứ 3 để dễ dàng swap với LLM khác sau này
"""
