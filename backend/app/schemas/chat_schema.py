"""
File: chat_schema.py
Công dụng: Định nghĩa Pydantic models để validate dữ liệu đầu vào/ra
- ChatRequest: Khối dữ liệu request từ Frontend
- SourceLink: Thông tin tài liệu tham chiếu
- ChatResponseData: Chứa answer và sources
- ChatResponse: Response được trả về Frontend
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """
    Model cho POST request /api/v1/chat
    """
    message: str = Field(..., min_length=1, description="Câu hỏi từ người dùng")

    class Config:
        example = {
            "message": "Nhân viên nghỉ ốm được trả lương bao nhiêu phần trăm?"
        }


class SourceLink(BaseModel):
    """
    Model định nghĩa cấu trúc nguồn tài liệu tham chiếu
    """
    doc_name: str = Field(..., description="Tên tài liệu PDF")
    page: int = Field(..., description="Số trang trong tài liệu")
    article: str = Field(..., description="Điều, khoản trong tài liệu")

    class Config:
        example = {
            "doc_name": "noi_quy.pdf",
            "page": 5,
            "article": "Điều 12"
        }


class ChatResponseData(BaseModel):
    """
    Model chứa dữ liệu response từ bot
    """
    answer: str = Field(..., description="Câu trả lời từ bot")
    sources: List[SourceLink] = Field(default_factory=list, description="Danh sách nguồn tài liệu tham chiếu")

    class Config:
        example = {
            "answer": "Nghỉ ốm được hưởng 75% lương theo quy định của Luật Bảo hiểm xã hội.",
            "sources": [
                {
                    "doc_name": "noi_quy.pdf",
                    "page": 5,
                    "article": "Điều 12"
                }
            ]
        }


class ChatResponse(BaseModel):
    """
    Model response chính được trả về Frontend
    """
    status: str = Field(default="success", description="Trạng thái response")
    data: ChatResponseData = Field(..., description="Dữ liệu response")

    class Config:
        example = {
            "status": "success",
            "data": {
                "answer": "Nghỉ ốm được hưởng 75% lương theo quy định của Luật Bảo hiểm xã hội.",
                "sources": [
                    {
                        "doc_name": "noi_quy.pdf",
                        "page": 5,
                        "article": "Điều 12"
                    }
                ]
            }
        }
