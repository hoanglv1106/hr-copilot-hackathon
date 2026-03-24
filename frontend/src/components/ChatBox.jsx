import React from 'react';
import { Loader } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatBox({ messages, isLoading, messagesEndRef }) {
    return (
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-500">
                    <p className="text-lg font-medium">Hãy bắt đầu cuộc trò chuyện</p>
                    <p className="text-sm mt-2">Đặt câu hỏi về chính sách nhân sự</p>
                </div>
            ) : (
                messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                ))
            )}

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
    );
}
