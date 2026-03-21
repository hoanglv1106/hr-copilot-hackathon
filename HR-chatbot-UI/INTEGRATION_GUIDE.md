# 🎯 HR Copilot Frontend - Backend API Integration Guide

## ✅ What Was Implemented

### 1. **API Client Setup**

**File:** `lib/axiosClient.ts`
- Configures axios to connect to `http://localhost:8000/api/v1`
- Auto-generates and manages session ID using `uuid`
- Stores session ID in `localStorage` with key `hr_session_id`
- **Adds `x-session-id` header to all requests automatically**

```typescript
// Automatically added to every request
Header: x-session-id: [UUID stored in localStorage]
```

### 2. **Chat Service API Calls**

**File:** `lib/services/chatService.ts`

**Function 1: `sendMessage(message)`**
```typescript
// Calls: POST /chat/
// Expects response: { answer: string, sources?: unknown[] }
const response = await sendMessage("What is PTO policy?");
// Returns: { answer: "..." }
```

**Function 2: `getChatHistory()`**
```typescript
// Calls: GET /chat/history
// Expects response: { session_id: string, messages: [...] }
const messages = await getChatHistory();
// Returns: Message[] (properly typed)
```

### 3. **Main Application Logic**

**File:** `app/page.tsx`

#### A. Session Management
```typescript
// Loads sessions from localStorage on mount
useEffect(() => {
  const savedSessions = localStorage.getItem('hr_chat_sessions');
  // If empty, creates first session with UUID
  // Saves sessions to localStorage whenever they change
}, []);
```

#### B. Chat History Loading
```typescript
// Watches activeSessionId and loads history
useEffect(() => {
  if (!activeSessionId) return;
  setIsLoading(true);
  const messages = await getChatHistory(); // Fetches from API
  // Updates messages in current session
}, [activeSessionId]);
```

#### C. Sending Messages
```typescript
const handleSendMessage = async (content: string) => {
  // 1. Add user message immediately (UI feedback)
  // 2. Call API: sendMessage(content)
  // 3. Add AI response to messages
  // 4. Show loading state while fetching
  // 5. Handle errors gracefully
};
```

### 4. **Local Collection & Persistence**

✅ **localStorage Keys Used:**
- `hr_session_id` - Session identifier (UUID)
- `hr_chat_sessions` - Array of chat sessions with titles

✅ **Session Structure:**
```typescript
{
  id: "uuid",
  title: "First 30 chars of first message",
  updatedAt: Date,
  messages: [
    { id: string, role: "user" | "ai", content: string, timestamp: Date }
  ]
}
```

## 🔌 How It Works (Flow Diagram)

```
User Type Message
    ↓
Click Send / Press Enter
    ↓
Add message to local state immediately (UI updates instantly)
    ↓
Show "HR Copilot is thinking..." loading indicator
    ↓
API Call: POST /chat/ with header x-session-id
    ↓
Backend processes and returns: { answer: "..." }
    ↓
Add AI response to messages array
    ↓
Hide loading indicator
    ↓
UI shows full conversation
```

## 🔄 Session Flow

```
1. App loads → Check localStorage for saved sessions
   ↓
2. No sessions found → Create first session with UUID
   ↓
3. User opens session → GET /chat/history (with session ID)
   ↓
4. Load messages from backend
   ↓
5. User sends message → POST /chat/ (with session ID)
   ↓
6. Get response, add to messages
   ↓
7. Auto-save to localStorage
```

## ⚙️ Configuration

**Backend Base URL:** `http://localhost:8000/api/v1`
(Update in `lib/axiosClient.ts` if different)

**Header for all requests:**
```
x-session-id: [UUID from localStorage]
```

## 🧪 Testing the Integration

1. **Start the backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start the frontend:**
   ```bash
   cd HR-chatbot-UI
   npm run dev
   ```

3. **Test in browser:**
   - Open http://localhost:3000
   - Type a message and press Send
   - Check Network tab to see API calls
   - Refresh page - chat history should persist

## 📝 Component Integration Points

### ✅ No Changes to Components
- `ChatWindow.tsx` - Already has auto-scroll and loading indicators
- `ChatInput.tsx` - Already handles submit events
- `MessageItem.tsx` - Already renders messages correctly
- `Sidebar.tsx` - Already displays sessions list

### ✅ All Original Tailwind CSS Preserved
- 100% of existing styling maintained
- Only added `useState` and `useEffect` hooks
- Only added conditional rendering for loading states

## 🚀 Key Features Implemented

✅ Persistent sessions (saved to localStorage)  
✅ Auto-generate session IDs (uuidv4)  
✅ Fetch chat history on session open  
✅ Send messages to backend API  
✅ Loading states  
✅ Error handling with user messages  
✅ Auto-scroll to latest message  
✅ Immediate UI feedback (optimistic updates)  
✅ localStorage auto-save  

## 📦 Dependencies Used
- `axios` - HTTP client
- `uuid` - Generate unique session IDs
- `react-toastify` - Ready for notifications (optional)

## ⚠️ Important Notes

1. **Session ID is auto-generated** - No login required
2. **Messages persist** - Even after page refresh
3. **One session per browser** - Stored in localStorage
4. **Error messages shown to user** - If API fails
5. **Loading indicator shown** - While waiting for response

## 🔗 API Contract Reference

```
POST /chat/
  Header: x-session-id
  Body: { "message": "..." }
  Response: { "answer": "...", "sources": [...] }

GET /chat/history
  Header: x-session-id
  Response: { "session_id": "...", "messages": [...] }
```

---

**Integration Status:** ✅ COMPLETE - Ready to connect to backend!
