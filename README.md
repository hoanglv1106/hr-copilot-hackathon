# 🚀 HR Copilot - Trợ Lý Nhân Sự Ảo

**HR Copilot** là nền tảng chatbot AI thông minh cho phòng Nhân Sự, giúp nhân viên truy vấn chính sách, quy định, lương thưởng, bảo hiểm từ các tài liệu PDF, với độ chính xác cao và thời gian phản hồi cực nhanh (< 1 giây).

---

## ✨ Điểm Nhấn Kỹ Thuật

| Tính năng | Mô tả | Công nghệ |
|----------|-------|----------|
| ⚡ **Phản hồi cực nhanh (< 1s)** | Cơ chế Redis Cache chặn trước, nếu Cache Hit sẽ trả lời ngay mà không cần gọi LLM | Redis + MD5 Hashing |
| 🎯 **2-Stage Retrieval Precision** | Truy xuất Dense Vector qua Qdrant (top-10) rồi Rerank ngữ nghĩa qua Cohere (top-3) để tăng độ chính xác | Qdrant + Cohere Rerank API |
| 📊 **Bảo toàn Format Bảng Biểu** | Dùng `pdfplumber` để trích xuất và giữ nguyên bảng biểu từ PDF sang Markdown, giúp AI đọc hiểu chính xác lương, bảo hiểm | pdfplumber + Markdown |
| 🔄 **Đồng bộ Tự động Event-driven** | Backend tự động quét PostgreSQL, băm SHA-256 và đồng bộ lên Qdrant khi khởi động, chống trùng lặp 100% | SHA-256 Hashing + Lifespan Events |

---

## 🏗️ Cấu Trúc Project

```
hr-copilot-hackathon/
│
├── 📁 backend/                          ⭐ FastAPI Backend (Port 8000)
│   ├── app/
│   │   ├── 📁 api/v1/                  # API Routes (Chat, Documents, Health)
│   │   ├── 📁 services/                # Core Business Logic
│   │   │   ├── rag_service.py          # 6-Step RAG Pipeline (Retrieve→Rerank→Format→Prompt→Generate→Parse)
│   │   │   ├── document_service.py     # PDF Processing + pdfplumber Table Extraction
│   │   │   ├── history_service.py      # Chat History Management
│   │   │   └── ...
│   │   ├── 📁 integrations/            # External Services
│   │   │   ├── llm_client.py           # Gemini LLM Integration
│   │   │   ├── qdrant_client.py        # Vector DB (Dense Retrieval)
│   │   │   ├── rerank_client.py        # Cohere Rerank API (Semantic Reranking)
│   │   │   └── ...
│   │   ├── 📁 repositories/
│   │   │   ├── cache_repo.py           # Redis Cache Layer
│   │   │   ├── chat_repo.py            # Chat Storage Layer
│   │   │   └── ...
│   │   ├── 📁 models/                  # SQLAlchemy ORM Models (Document, History)
│   │   ├── 📁 schemas/                 # Pydantic Request/Response Models
│   │   ├── 📁 core/
│   │   │   ├── config.py               # Configuration Management
│   │   │   ├── database.py             # PostgreSQL Connection Pool
│   │   │   └── prompt_templates.py     # RAG Prompt Templates
│   │   └── main.py                     # ❤️ FastAPI App + Startup Lifespan (Auto-Sync Logic)
│   ├── requirements.txt                # Dependency Management
│   ├── .env.example                    # Environment Variables Template
│   │
│   └── 📦 Docker services (via docker-compose.yml):
│       ├── Qdrant (Vector DB)          - Port 6333
│       ├── PostgreSQL (Data Storage)   - Port 5432
│       └── Redis (Cache Layer)         - Port 6379
│
│
├── 📁 HR-chatbot-UI/                   ⭐ Next.js Frontend - Admin/HR Dashboard (Port 3000)
│   ├── app/                            # Next.js App Router
│   ├── components/                     # React Components (Chat, Sidebar, etc.)
│   ├── lib/                            # Utilities (axiosClient, chatService)
│   ├── package.json
│   └── tailwind.config.js
│
│
├── 📁 frontend/                        ⭐ Vite/React Frontend - Employee User Site (Port 5173)
│   ├── src/
│   │   ├── components/                 # React Components
│   │   ├── hooks/                      # Custom Hooks (useChat)
│   │   ├── services/                   # API Integration
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
│
└── 🐳 docker-compose.yml               # Orchestrate Qdrant, PostgreSQL, Redis

```

---

## ⚙️ Setup & Hướng Dẫn Chạy Local

### **Bước 1: Clone & Thiết Lập Thư Mục**
```bash
cd hr-copilot-hackathon
```

### **Bước 2: Khởi Động Docker (Qdrant, PostgreSQL, Redis)**
```bash
docker-compose up -d
```
✅ Kiểm tra: Mở http://localhost:6333 để kiểm tra Qdrant Dashboard  
✅ PostgreSQL: `localhost:5432` | Redis: `localhost:6379`

---

### **Bước 3: Cấu Hình & Chạy Backend (FastAPI)**

Mở **Terminal 1** tại `backend/`:

```bash
# 3.1 Tạo Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3.2 Cài Dependency
pip install -r requirements.txt

# 3.3 Cấu Hình Environment Variables
# → Tạo file .env dựa trên .env.example
# → Điền các API Keys: GEMINI_API_KEY, COHERE_API_KEY, QDRANT_URL, REDIS_URL, DATABASE_URL
copy .env.example .env
# Edit .env với các giá trị thực

# 3.4 Khởi Tạo Database & Chạy Backend
uvicorn app.main:app --reload

```
✅ Backend đã sẵn sàng tại: `http://localhost:8000`  
✅ API Docs (Swagger): `http://localhost:8000/docs`  
✨ **Lưu ý**: Khi backend khởi động, nó tự động đồng bộ dữ liệu từ PostgreSQL lên Qdrant (event-driven sync).

---

### **Bước 4: Chạy Frontend Admin/HR (Next.js)**

Mở **Terminal 2** tại `HR-chatbot-UI/`:

```bash
# 4.1 Cài Dependency
npm install

# 4.2 Chạy Dev Server
npm run dev
```
✅ Mở: `http://localhost:3000`

---

### **Bước 5: Chạy Frontend User Site (Vite/React)**

Mở **Terminal 3** tại `frontend/`:

```bash
# 5.1 Cài Dependency
npm install

# 5.2 Chạy Dev Server
npm run dev
```
✅ Mở: `http://localhost:5173`

---

## 🔌 API Endpoints Cốt Lõi

| Endpoint | Method | Mô Tả | Tham số |
|----------|--------|-------|--------|
| `/api/v1/chat` | `POST` | Gửi câu hỏi, nhận câu trả lời + nguồn tài liệu | `message` (string), Header: `X-Session-ID` (UUID) |
| `/api/v1/chat/history` | `GET` | Lấy lịch sử chat của phiên | Header: `X-Session-ID`, Query: `limit` |
| `/api/v1/chat/health` | `GET` | Kiểm tra trạng thái Chat Service | - |
| `/api/v1/health` | `GET` | Kiểm tra tổng trạng thái (DB, Redis, Qdrant, LLM) | - |
| `/api/v1/documents/upload` | `POST` | Upload tài liệu PDF mới | `file` (PDF binary) |

### **Ví dụ Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "X-Session-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"message": "Lương tối thiểu bao nhiêu?"}'
```

### **Ví dụ Response:**
```json
{
  "status": "success",
  "data": {
    "answer": "Theo chính sách HR của công ty, lương tối thiểu là 5.5 triệu VND/tháng...",
    "sources": [
      {
        "doc_name": "Salary_Policy_2024.pdf",
        "page": 3,
        "article": "Article 2.1 - Minimum Wage"
      }
    ]
  }
}
```

---

## ⚠️ Lưu Ý Quan Trọng

### 🔐 **Environment Variables (.env)**
Bắt buộc điền các giá trị sau:
- `GEMINI_API_KEY`: Google Gemini API Key (cho LLM)
- `COHERE_API_KEY`: Cohere API Key (cho Reranking)
- `QDRANT_URL`: URL Qdrant (VD: http://localhost:6333)
- `REDIS_URL`: URL Redis (VD: redis://localhost:6379/0)
- `DATABASE_URL`: PostgreSQL Connection String
- `ENVIRONMENT`: `development` hoặc `production`

### 🔄 **Đồng Bộ Tự Động Data**
- **Mỗi lần backend khởi động**, hệ thống tự động:
  1. Quét tất cả tài liệu trong PostgreSQL
  2. Tính SHA-256 hash cho mỗi file
  3. So sánh với dữ liệu đã có trong Qdrant
  4. **Nếu file mới** → Tự động xử lý PDF + embed vectors + lưu vào Qdrant
  5. **Nếu file cũ** → Bỏ qua (chống trùng lặp 100%)
- ✅ **Không cần** chạy script riêng, tất cả diễn ra trong `lifespan` event

### 📊 **Cache Hit Performance**
- Lần đầu hỏi câu hỏi → Full RAG Pipeline (có thể lâu 1-2s)
- Lần thứ 2 hỏi **cùng câu hỏi** → **Trả lời từ Redis Cache [< 100ms]**

### 🐛 **Troubleshooting**
| Lỗi | Nguyên Nhân | Cách Sửa |
|------|----------|----------|
| `Connection refused: Qdrant` | Qdrant chưa chạy | Chạy `docker-compose up -d` |
| `GEMINI_API_KEY not found` | Chưa cấu hình .env | Tạo .env từ .env.example, điền API keys |
| `Redis connection failed` | Redis chưa chạy | Chạy `docker-compose up -d redis` |
| `Empty response from LLM` | Network issue | Kiểm tra kết nối internet, API quota |

---

## 📚 Tech Stack

**Backend**: FastAPI, SQLAlchemy, Langchain  
**Vector DB**: Qdrant + Google Generative AI Embeddings  
**Semantic Reranking**: Cohere Rerank API  
**LLM**: Google Gemini API  
**Cache Layer**: Redis  
**Data Storage**: PostgreSQL  
**PDF Processing**: pdfplumber (Table-Preserve) + PyPDF2  
**Frontend - Admin**: Next.js 14, TypeScript, Tailwind CSS  
**Frontend - User**: Vite, React 18, JavaScript  

---

## 🎯 Workflow Luồng Xử Lý

```
User Question
    ↓
[Cache Check] Redis
    ├─ HIT → Return immediately (< 100ms)
    └─ MISS ↓
[Dense Retrieval] Qdrant (top-10 vectors)
    ↓
[Semantic Rerank] Cohere API (top-3)
    ↓
[Context Formatting] Markdown Tables Preserved
    ↓
[Prompt Building] HR_RAG_PROMPT Template
    ↓
[LLM Generation] Google Gemini API (temperature=0.2)
    ↓
[Response Parsing] JSON Extract (Answer + Sources)
    ↓
[Cache Store] Redis (for next request)
    ↓
Return to User
```

---

## 📞 Support & Contact

- **Documentation**: Xem file `IMPLEMENTATION_CHECKLIST.md` trong `HR-chatbot-UI/`
- **Issues**: Report lỗi qua GitHub Issues
- **Deployment**: Sử dụng Docker Compose hoặc Kubernetes manifest trong thư mục `/deployment/`

---

**🏆 HR Copilot - Blowing the rest away!**  

