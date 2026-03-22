# 🚀 HR Copilot Frontend Setup Guide

Hướng dẫn chi tiết để setup và chạy Frontend React cho dự án HR Copilot.

## 📋 Yêu cầu

- **Node.js**: v16+ (khuyến khích v18+)
- **npm**: v8+
- **Backend API**: Chạy tại `http://localhost:8000` (xem backend setup)

---

## 📦 Bước 1: Cài đặt Dependencies

Chạy lệnh sau trong thư mục `frontend`:

```bash
npm install
```

**Các package mới được cài:**

- `uuid` - Tạo Session ID duy nhất
- `lucide-react` - Icon library
- `react-toastify` - Toast notifications

---

## 📁 Bước 2: Cấu trúc tệp

Dự án được tổ chức theo kiến trúc **Component-based**:

```
frontend/
├── src/
│   ├── api/
│   │   └── axiosClient.js          # ✨ Axios instance + Session ID logic
│   ├── components/
│   │   ├── DocumentUpload.jsx       # ✨ Upload component
│   │   ├── ChatWindow.jsx           # ✨ Chat + Messages component
│   │   ├── ChatInput.jsx            # (old - có thể xóa)
│   │   ├── MessageBubble.jsx        # (old - có thể xóa)
│   │   └── ...
│   ├── styles/
│   │   └── index.css                # Global + Tailwind styles
│   ├── App.jsx                      # ✨ Layout chính (Sidebar + Chat)
│   └── main.jsx                     # ✨ Entry point
├── .env                             # API URL config
├── vite.config.js                   # Vite config
├── tailwind.config.js               # ✨ Tailwind config
├── postcss.config.js                # ✨ PostCSS config
└── package.json                     # Dependencies
```

---

## 🎯 Bước 3: Chạy Frontend Development Server

```bash
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:5173**

Mở trình duyệt và truy cập URL trên.

---

## 🏗️ Bước 4: Đảm bảo Backend API Chạy

Trước khi test UI, hãy chắc chắn rằng **Backend API chạy tại port 8000**:

```bash
# Trong thư mục backend
python -m uvicorn app.main:app --reload --port 8000
```

**API Endpoints cần:**

- `POST /api/v1/documents/upload` - Upload tài liệu PDF
- `POST /api/v1/chat/` - Gửi câu hỏi
- `GET /api/v1/chat/history` - Lấy lịch sử chat
- Header `x-session-id` - Tự động gắn bởi axiosClient

---

## 🎨 Kiến trúc Frontend

### **App.jsx** (Layout chính)

```
┌─────────────────────────────────┐
│  Sidebar (25%)  │  Main (75%)   │
├─────────────────┼───────────────┤
│  Logo           │  Top Bar      │
│  "HR Copilot"   │  Title        │
├─────────────────┼───────────────┤
│  Upload Section │               │
│  ┌───────────┐  │  ChatWindow   │
│  │ Drag Drop │  │  - Messages   │
│  │ Component │  │  - Auto scroll│
│  └───────────┘  │  - Loading    │
│                 │  - Input Area │
│  Tips Section   │               │
│  ✓ Tải PDF ...  │               │
└─────────────────┴───────────────┘
```

---

## 📝 Tính năng chính

### 1️⃣ **axiosClient.js** (API Client)

- Khởi tạo Axios instance với `baseURL: http://localhost:8000/api/v1`
- Tạo **Session ID** (UUID) tự động lần đầu → lưu vào `localStorage`
- **Interceptor Request**: Tự động thêm `x-session-id` vào header mọi request

**Cách dùng:**

```javascript
import axiosClient from '../api/axiosClient';

const response = await axiosClient.post('/chat/', {
  question: 'What is HR policy?'
});
```

---

### 2️⃣ **DocumentUpload.jsx** (Upload Component)

- **Giao diện**: Drag & Drop zone + nút chọn file
- **Validation**:
  - Chỉ chấp nhận file `.pdf`
  - Tối đa 50MB
- **Logic**:
  1. User chọn/kéo file PDF
  2. API POST `/documents/upload` (multipart/form-data)
  3. **Toast Notifications**:
     - ⚠️ **Warning** (vàng): File trùng nhau
     - ✅ **Success** (xanh): Upload thành công
     - ❌ **Error** (đỏ): Lỗi upload

**Ví dụ Response:**

```json
// Nếu file trùng
{
  "status": "warning",
  "message": "Tài liệu này đã tồn tại..."
}

// Nếu upload thành công
{
  "status": "success", 
  "message": "Đã tiếp nhận tài liệu. AI đang học..."
}
```

---

### 3️⃣ **ChatWindow.jsx** (Chat Component)

**Tính năng:**

- **Load History** (on mount): `GET /chat/history`
- **Send Message**: `POST /chat/` với question
- **Auto Scroll**: Tự động scroll đến message mới
- **Loading State**: Hiển thị "AI đang suy nghĩ..."
- **Markdown Rendering**: Render markdown từ AI response (bảng, in đậm, v.v)
- **Textarea Input**: Support Shift+Enter để xuống dòng

**State Management:**

```javascript
const [messages, setMessages] = useState([]); // Array of messages
const [input, setInput] = useState('');       // User input
const [isLoading, setIsLoading] = useState(false); // Loading state
```

**Message Object:**

```javascript
{
  id: 'user-1234567890',
  role: 'user' | 'assistant',
  content: 'Nội dung tin nhắn',
  timestamp: '2026-03-17T10:30:00Z'
}
```

---

### 4️⃣ **App.jsx** (Layout)

- **Sidebar** (25%):
  - Logo + Title "HR Copilot"
  - `<DocumentUpload />` component
  - Tips section
- **Main Area** (75%):
  - Top bar (blue gradient)
  - `<ChatWindow />` component
- **Toast Container**: Hiển thị notifications

---

## 🎨 Styling (TailwindCSS)

Dự án sử dụng **TailwindCSS 3.3** cho styling:

- `bg-*` - Màu nền
- `text-*` - Màu text
- `p-*` - Padding
- `m-*` - Margin
- `rounded-*` - Border radius
- `flex`, `grid` - Layout
- v.v (xem https://tailwindcss.com/docs)

**Custom Colors:**

```javascript
// tailwind.config.js
colors: {
  primary: '#3b82f6',      // Blue
  secondary: '#10b981',    // Green
}
```

---

## 🧪 Kiểm tra

### Test Upload:

1. Chuẩn bị file PDF test
2. Kéo vào **Upload Zone** hoặc bấm để chọn file
3. Verify toast notification xuất hiện
4. Kiểm tra backend `/documents/upload` API nhận request

### Test Chat:

1. Gõ câu hỏi: "Chính sách phép năm là gì?"
2. Bấm "Gửi" hoặc Ctrl+Enter
3. Verify loading indicator hiển thị
4. Verify AI response nhận được và hiển thị markdown
5. Verify auto-scroll hoạt động

---

## 🐛 Debugging

### Enable Debug Mode:

Trong `.env`:

```
VITE_DEBUG=true
```

### Console Logs:

Mở **DevTools** (F12) → **Console** tab để xem logs:

```javascript
// axiosClient.js
console.error('API Error:', error.response?.status, error.response?.data);

// ChatWindow.jsx
console.error('Failed to load history:', error);
console.error('Chat error:', error);
```

### Check Network:

DevTools → **Network** tab để xem HTTP requests:

- `POST /api/v1/documents/upload`
- `POST /api/v1/chat/`
- `GET /api/v1/chat/history`

---

## 📦 Production Build

Tạo production build:

```bash
npm run build
```

Output sẽ nằm tại: `dist/` folder

Preview:

```bash
npm run preview
```

---

## 🚀 Deploy to Production

### Option 1: Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Option 2: Deploy to Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir dist
```

### Option 3: Manual Deploy (Nginx/Apache)

1. Build: `npm run build`
2. Copy `dist/` folder → web server root
3. Configure server để route tất cả paths về `index.html`

---

## 📚 Resources

- **React**: https://react.dev
- **Vite**: https://vitejs.dev
- **TailwindCSS**: https://tailwindcss.com
- **Axios**: https://axios-http.com
- **React Markdown**: https://github.com/remarkjs/react-markdown
- **Lucide React**: https://lucide.dev
- **React Toastify**: https://fkhadra.github.io/react-toastify/introduction

---

## ✅ Checklist

- [ ] `npm install` thành công
- [ ] Backend API chạy tại port 8000
- [ ] Frontend chạy tại port 5173 (`npm run dev`)
- [ ] Upload file PDF thành công → toast notification
- [ ] Chat: Gửi câu hỏi → Nhận response AI
- [ ] Chat history: Load các tin nhắn cũ
- [ ] Auto scroll: Scroll đến message mới
- [ ] Markdown rendering: Tables, bold, links hiển thị đúng

---

## 💬 Support

Nếu gặp lỗi:

1. Check console logs (F12)
2. Verify backend API chạy
3. Check `.env` API URL
4. Clear `localStorage` và refresh page
5. Xóa `node_modules` và chạy `npm install` lại

**Happy coding! 🎉**
