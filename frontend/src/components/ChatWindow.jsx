import React from 'react';
import { Loader } from 'lucide-react';
import useChat from '../hooks/useChat';
import ChatBox from './ChatBox';
import ChatInput from './ChatInput';

export default function ChatWindow() {
  const {
    messages,
    input,
    setInput,
    isLoading,
    isLoadingHistory,
    messagesEndRef,
    handleSendMessage,
  } = useChat();

  if (isLoadingHistory) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-surface dark:bg-dark-bg">
        <Loader className="w-6 h-6 animate-spin text-peach mb-3" />
        <p className="text-sm text-text-muted dark:text-dark-text-muted">Đang tải lịch sử chat...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-surface dark:bg-dark-bg">
      <ChatBox
        messages={messages}
        isLoading={isLoading}
        messagesEndRef={messagesEndRef}
      />
      <ChatInput
        input={input}
        setInput={setInput}
        isLoading={isLoading}
        onSend={handleSendMessage}
      />
    </div>
  );
}
