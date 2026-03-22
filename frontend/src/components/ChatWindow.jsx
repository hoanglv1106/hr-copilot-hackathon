import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Loader } from 'lucide-react';
import axiosClient from '../api/axiosClient';

/**
 * ChatWindow Component
 * - Giao diện: ChatBox + ChatInput (giống ChatGPT)
 * - Logic:
 *   1. useEffect: Load lịch sử chat từ API GET /chat/history
 *   2. User input: Gõ câu hỏi và bấm Gửi
 *   3. Thêm tin nhắn user vào state ngay (optimistic update)
 *   4. Hiển thị "AI đang suy nghĩ..." (loading indicator)
 *   5. Gọi API POST /chat/
 *   6. Nhận response, thêm vào messages
 *   7. Auto scroll đến message cuối cùng
 *   8. Render markdown cho tin nhắn AI
 */

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef(null);

  /**
   * Auto scroll đến message cuối cùng
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Load lịch sử chat khi component mount
   * GET /chat/history
   */
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setIsLoadingHistory(true);
        const response = await axiosClient.get('/chat/history');
        
        // API trả về format: { messages: [...] }
        const historyMessages = response.data.messages || [];
        setMessages(historyMessages);
      } catch (error) {
        console.error('Failed to load history:', error);
        // Nếu lỗi, vẫn cho user chat tiếp nhưng không có history
        setMessages([]);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadHistory();
  }, []);

  /**
   * Xử lý gửi tin nhắn
   * 1. Thêm tin nhắn user vào state ngay (optimistic)
   * 2. Gọi API POST /chat/
   * 3. Thêm response AI vào state
   */
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    // Optimistic update: thêm user message ngay
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axiosClient.post('/chat/', {
        message: input,
      });

      const aiMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.data.data.answer,
        timestamp: new Date().toISOString(),
      };

      // Thêm AI message vào state
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      // Thêm error message
      const errorMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '❌ Lỗi kết nối với AI. Vui lòng thử lại.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Xử lý khi user bấm Enter
   */
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoadingHistory) {
    return (
      <div className="h-full flex flex-col items-center justify-center">
        <Loader className="w-8 h-8 animate-spin text-blue-500 mb-2" />
        <p className="text-gray-600">Đang tải lịch sử chat...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <p className="text-lg font-medium">Hãy bắt đầu cuộc trò chuyện</p>
            <p className="text-sm mt-2">Đặt câu hỏi về chính sách nhân sự</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-900'
                }`}
              >
                {message.role === 'assistant' ? (
                  <ReactMarkdown
                    className="prose prose-sm dark:prose-invert max-w-none"
                    components={{
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      table: ({ children }) => (
                        <table className="border-collapse border border-gray-400 w-full my-2">
                          {children}
                        </table>
                      ),
                      th: ({ children }) => (
                        <th className="border border-gray-400 p-2 bg-gray-300 font-bold">
                          {children}
                        </th>
                      ),
                      td: ({ children }) => (
                        <td className="border border-gray-400 p-2">{children}</td>
                      ),
                      strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                      em: ({ children }) => <em className="italic">{children}</em>,
                      ul: ({ children }) => (
                        <ul className="list-disc list-inside my-2">{children}</ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal list-inside my-2">{children}</ol>
                      ),
                      li: ({ children }) => <li className="mb-1">{children}</li>,
                      code: ({ children }) => (
                        <code className="bg-gray-800 text-white px-2 py-1 rounded text-sm">
                          {children}
                        </code>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                ) : (
                  <p className="text-sm">{message.content}</p>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-900 rounded-lg p-4 flex gap-2">
              <Loader className="w-5 h-5 animate-spin" />
              <span className="text-sm">AI đang suy nghĩ...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-300 p-4 bg-gray-50">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi của bạn (N/A để xuống dòng)..."
            disabled={isLoading}
            rows={3}
            className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className={`
              px-4 py-3 rounded-lg font-medium
              transition-all duration-200
              flex items-center gap-2
              ${
                isLoading || !input.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }
            `}
          >
            {isLoading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Sending...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Gửi</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
