# HR Copilot Chatbot - Hackathon Project

## Mô tả
HR Copilot là một chatbot hỗ trợ nhân sự dựa trên RAG (Retrieval-Augmented Generation) giúp nhân viên trả lời các câu hỏi về chính sách, quy định công ty.

## Kiến trúc
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite (JavaScript)
- **Vector DB**: Qdrant
- **LLM**: Google Gemini
- **Rerank**: Cohere Rerank
- **Database**: PostgreSQL + Redis

## Cấu trúc Project
```
hr-copilot-hackathon/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docker-compose.yml# Docker services
├── .gitignore
└── README.md
```

## Setup & Chỉ dẫn

### Yêu cầu
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- API Keys: Gemini, Cohere

### Bước 1: Khởi động Database Services
```bash
docker-compose up -d
```
Chợi 30 giây để các services khởi động hoàn toàn.

### Bước 2: Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Tạo file `.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hr_copilot_db
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
GEMINI_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
```

Khởi tạo database:
```bash
python scripts/init_db.py
```

Đẩy dữ liệu vào Qdrant:
```bash
python scripts/ingest_pipeline.py
```

Chạy API:
```bash
uvicorn app.main:app --reload
```
API chạy tại http://localhost:8000

### Bước 3: Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend chạy tại http://localhost:5173

## API Endpoints

### Chat Routes
- `POST /api/v1/chat` - Gửi câu hỏi và nhận trả lời
- `GET /api/v1/chat/history/{session_id}` - Lấy lịch sử chat
- `POST /api/v1/chat/sessions` - Tạo phiên chat mới
- `DELETE /api/v1/chat/{message_id}` - Xóa tin nhắn

### Health Routes
- `GET /ping` - Check server có hoạt động
- `GET /health` - Check tổng trạng thái

## Development Tips
- Backend watch mode: `uvicorn app.main:app --reload`
- Frontend hot reload: `npm run dev`
- Format code: Backend `black app/`, Frontend `prettier --write 'src/**/*.{js,jsx}'`
- Test Backend: `pytest`

## Lưu ý quan trọng
- **KHÔNG commit file `.env` có chứa API keys**
- Kiểm tra `.gitignore` để đảm bảo các files sensitive được bỏ qua
- Update `VITE_API_URL` nếu backend chạy trên server khác
