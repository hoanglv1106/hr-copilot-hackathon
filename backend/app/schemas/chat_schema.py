"""
File: chat_schema.py
Công dụng: Định nghĩa Pydantic models để validate dữ liệu đầu vào/ra
- ChatRequest: Khối dữ liệu request từ Frontend
  {
    "session_id": "UUID",
    "message": "Câu hỏi từ user",
    "context": {...}
  }
- ChatResponse: Khối dữ liệu response về Frontend
  {
    "response": "Câu trả lời từ bot",
    "sources": [SourceLink, ...],
    "message_id": "UUID"
  }
- SourceLink: Thông tin tài liệu tham chiếu
  {
    "title": "Chính sách...",
    "section": "Điều X, Khoản Y",
    "document_name": "file.pdf",
    "confidence": 0.95
  }
- ChatHistory: Ghi lại một lần trao đổi
- ChatSession: Thông tin phiên chat
"""
