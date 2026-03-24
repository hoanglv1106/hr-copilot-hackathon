'use client';

import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Sidebar } from '@/components/sidebar/Sidebar';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ChatSession, Message } from '@/types';
import { TopBar } from '@/components/layout/TopBar';
import { getChatHistory, sendMessage } from '@/lib/services/chatService';

const SESSIONS_STORAGE_KEY = 'hr_chat_sessions';

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>(undefined);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Khởi tạo ban đầu
  useEffect(() => {
    const savedSessions = localStorage.getItem(SESSIONS_STORAGE_KEY);
    let initialSessions: ChatSession[] = [];

    if (savedSessions) {
      try {
        initialSessions = JSON.parse(savedSessions).map((s: any) => ({
          ...s,
          updatedAt: new Date(s.updatedAt),
          messages: [],
        }));
      } catch (e) {
        console.error('Failed to parse saved sessions:', e);
      }
    }

    setSessions(initialSessions);
    
    // Tự động tạo một session rỗng (Welcome screen) ngay khi mở web
    startFreshChat(initialSessions);
  }, []);

  const startFreshChat = (currentSessions: ChatSession[] = sessions) => {
    const newBackendSessionId = uuidv4();
    localStorage.setItem('hr_session_id', newBackendSessionId);
    
    const newSession: ChatSession = {
      id: uuidv4(),
      title: 'New Conversation',
      updatedAt: new Date(),
      messages: []
    };
    
    // Đưa session mới lên đầu danh sách
    setSessions([newSession, ...currentSessions]);
    setActiveSessionId(newSession.id);
  };

  // Load chat history khi đổi session
  useEffect(() => {
    if (!activeSessionId) return;
    
    const activeSession = sessions.find(s => s.id === activeSessionId);
    // Nếu session này vừa mới tạo (chưa có tin nhắn), không cần load API
    if (activeSession && activeSession.messages.length === 0 && activeSession.title === 'New Conversation') {
      return;
    }

    const loadHistory = async () => {
      setIsLoading(true);
      try {
        const messages = await getChatHistory(activeSessionId);
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeSessionId ? { ...s, messages } : s
          )
        );
      } catch (error) {
        console.error('Failed to load chat history:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadHistory();
  }, [activeSessionId]);

  // Lưu sessions vào localStorage (Chỉ lưu những cái đã có tin nhắn hoặc title đã đổi)
  useEffect(() => {
    const validSessions = sessions.filter(s => s.messages.length > 0 || s.title !== 'New Conversation');
    if (validSessions.length > 0) {
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(validSessions));
    }
  }, [sessions]);

  const activeSession = sessions.find(s => s.id === activeSessionId);
  const messages = activeSession?.messages || [];

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  const handleNewChat = () => {
    startFreshChat();
  };

  const handleDeleteSession = (id: string) => {
    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    if (activeSessionId === id) {
       // Nếu xóa chat hiện tại, tự động tạo chat mới trắng
      startFreshChat(newSessions);
    }
  };

  const handleShareSession = (id: string) => {
    const session = sessions.find(s => s.id === id);
    if (session) {
      navigator.clipboard?.writeText(`HR Copilot — ${session.title}`);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeSessionId) return;

    const newMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date()
    };

    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return {
          ...s,
          messages: [...s.messages, newMessage],
          title: s.title === 'New Conversation' ? content.slice(0, 30) + '...' : s.title,
          updatedAt: new Date()
        };
      }
      return s;
    }));

    setIsTyping(true);

    try {
      const response = await sendMessage(content, activeSessionId);
      const resAny = response as any;
      
      // ✅ FIX: Use optional chaining to safely extract answer from multiple possible paths
      const answerContent = 
        resAny?.data?.answer ||           // Nếu response = { status, data: { answer } }
        resAny?.answer ||                  // Nếu response = { answer }
        resAny?.data?.content ||           // Fallback nếu field là content thay vì answer
        'Lỗi lấy nội dung từ API';          // Fallback cuối cùng
      
      console.log('[Chat] Extracted answer:', answerContent);
      
      const aiMessage: Message = {
        id: uuidv4(),
        role: 'ai',
        content: answerContent,
        timestamp: new Date()
      };

      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          return {
            ...s,
            messages: [...s.messages, aiMessage],
            updatedAt: new Date()
          };
        }
        return s;
      }));
    } catch (error) {
       // ... (Giữ nguyên phần catch error cũ)
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'ai',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };

      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          return {
            ...s,
            messages: [...s.messages, errorMessage],
            updatedAt: new Date()
          };
        }
        return s;
      }));
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-ts-bg font-sans text-slate-900 dark:text-ts-text transition-colors duration-200">
      <Sidebar
        sessions={sessions.filter(s => s.messages.length > 0 || s.title !== 'New Conversation')} // Ẩn các session rỗng ở Sidebar
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onShareSession={handleShareSession}
      />
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative bg-slate-50 dark:bg-ts-bg transition-colors duration-200">
        <TopBar />
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center bg-slate-50 dark:bg-ts-bg">
            <div className="text-center">
              <div className="w-8 h-8 border-4 border-indigo-200 dark:border-indigo-900 border-t-indigo-600 dark:border-t-indigo-400 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-slate-600 dark:text-ts-text-secondary text-sm">Loading chat history...</p>
            </div>
          </div>
        ) : (
          <ChatWindow
            messages={messages}
            isTyping={isTyping}
            onSendMessage={handleSendMessage}
          />
        )}
      </main>
    </div>
  );
}