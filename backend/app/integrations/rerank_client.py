"""
File: rerank_client.py
Công dụng: Adapter gọi API Cohere Rerank
- initialize_rerank(): Khởi tạo client kết nối Cohere
- rerank(): Sắp xếp lại danh sách tài liệu theo relevance
  Input: query (câu hỏi), documents (danh sách tài liệu)
  Output: documents được sắp xếp lại kèm relevance scores

Giúp cải thiện chất lượng câu trả lời bằng cách sắp xếp lại các tài liệu tham chiếu
"""
