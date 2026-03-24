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
      <div className="h-full flex flex-col items-center justify-center">
        <Loader className="w-8 h-8 animate-spin text-blue-500 mb-2" />
        <p className="text-gray-600">Đang tải lịch sử chat...</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white">
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
