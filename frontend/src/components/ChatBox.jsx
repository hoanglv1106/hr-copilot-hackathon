import React from 'react';
import { Loader, Brain } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatBox({ messages, isLoading, messagesEndRef }) {
    return (
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
            {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center">
                    <div className="w-13 h-13 rounded-[18px] bg-[#FDFBF7] dark:bg-[#2A2421] border border-[#EBE5D9] dark:border-[#3E352F] shadow-sm flex items-center justify-center mb-5 p-2 text-peach" style={{width: '56px', height: '56px'}}>
                        <Brain strokeWidth={2.25} className="w-full h-full" />
                    </div>
                    <p className="text-[17px] font-medium text-text-primary dark:text-dark-text mb-2 tracking-tight">Xin chào, tôi có thể giúp gì cho bạn?</p>
                    <p className="text-[14px] text-text-muted dark:text-dark-text-muted">Hỏi đáp về các chính sách và tài liệu nhân sự</p>
                </div>
            ) : (
                messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                ))
            )}

            {isLoading && (
                <div className="flex justify-start">
                    <div className="bg-card dark:bg-dark-card text-text-secondary dark:text-dark-text-secondary rounded-2xl px-4 py-3 flex gap-2 items-center border border-border dark:border-dark-border">
                        <Loader className="w-3.5 h-3.5 animate-spin text-peach" />
                        <span className="text-sm">AI đang suy nghĩ...</span>
                    </div>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}
