import axiosClient from '../axiosClient';
import { Message } from '@/types';

interface ChatResponse {
  answer: string;
  sources?: unknown[];
}

interface ChatHistoryResponse {
  session_id: string;
  messages: Array<{
    role: 'user' | 'ai';
    content: string;
  }>;
}

/**
 * Send a message to the chat API
 * 
 * ✅ FIX: Now accepts sessionId parameter and uses it explicitly in headers
 * This prevents cross-session data leak from localStorage interceptor
 */
export async function sendMessage(message: string, sessionId: string): Promise<ChatResponse> {
  try {
    // ✅ Explicitly set sessionId in headers to override any interceptor default
    const response = await axiosClient.post('/chat/', 
      { message },
      { 
        headers: { 
          'x-session-id': sessionId 
        } 
      }
    );
    
    // Debug logging
    console.log('[sendMessage] Raw API Response:', response.data);
    console.log('[sendMessage] Using sessionId:', sessionId);
    
    const answerData = response.data?.data?.answer || response.data?.answer;
    const sourcesData = response.data?.data?.sources || response.data?.sources || [];
    
    console.log('[sendMessage] Extracted answer:', answerData);
    console.log('[sendMessage] Extracted sources:', sourcesData);
    
    if (!answerData) {
      console.warn('[sendMessage] Warning: answer field is empty or not present in API response');
      console.log('[sendMessage] Full response structure:', JSON.stringify(response.data, null, 2));
    }
    
    // Return consistent structure: { answer, sources }
    return {
      answer: answerData || 'Lỗi lấy nội dung từ API',
      sources: sourcesData
    };
  } catch (error) {
    throw new Error(
      `Failed to send message: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Get chat history
 * 
 * ✅ FIX: Now accepts sessionId parameter and uses it explicitly in headers
 * This prevents cross-session data leak from localStorage interceptor
 * 
 * Lưu ý: Backend có thể trả về role là 'assistant' hoặc 'ai'
 * Frontend sẽ convert tất cả thành 'ai' hoặc 'user'
 */
export async function getChatHistory(sessionId: string): Promise<Message[]> {
  try {
    // ✅ Explicitly set sessionId in headers to override any interceptor default
    const response = await axiosClient.get('/chat/history', {
      headers: { 
        'x-session-id': sessionId 
      }
    });
    
    const data = response.data;
    
    console.log('[Chat History] Raw API response:', data);
    console.log('[Chat History] Using sessionId:', sessionId);
    
    const messages = (data.messages || []).map((item: any, index: number) => {
      // Convert role từ backend thành format Frontend
      // 'assistant' → 'ai', 'user' → 'user'
      const normalizedRole: 'user' | 'ai' = item.role === 'user' ? 'user' : 'ai';
      
      const message: Message = {
        id: `msg-${Date.now()}-${index}`,
        role: normalizedRole,
        content: item.content,
        timestamp: new Date(),
      };
      
      console.log(`[Chat History] Message ${index}:`, {
        originalRole: item.role,
        normalizedRole: message.role,
        content: message.content.substring(0, 50) + '...'
      });
      
      return message;
    });
    
    console.log('[Chat History] Converted messages count:', messages.length);
    return messages;
  } catch (error) {
    throw new Error(
      `Failed to load chat history: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}