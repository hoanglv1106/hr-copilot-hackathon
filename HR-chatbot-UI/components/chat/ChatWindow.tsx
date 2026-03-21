'use client';

import React, { useEffect, useRef } from 'react';
import { Message } from '@/types';
import { MessageItem } from './MessageItem';
import { ChatInput } from './ChatInput';
import { Bot, Sparkles } from 'lucide-react';

interface ChatWindowProps {
    messages: Message[];
    isTyping: boolean;
    onSendMessage: (content: string) => void;
}

export function ChatWindow({ messages, isTyping, onSendMessage }: ChatWindowProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    return (
        <div className="flex-1 flex flex-col h-full bg-slate-50 dark:bg-ts-bg relative transition-colors duration-200">
            {/* Header (Mobile Only) */}
            <div className="md:hidden flex items-center px-4 py-3 bg-white dark:bg-ts-surface border-b border-slate-200 dark:border-ts-border shadow-sm z-10 transition-colors duration-200">
                <div className="font-bold text-lg text-indigo-600 dark:text-indigo-400 flex items-center gap-2">
                    <Bot className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    HR Copilot
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 md:py-8 w-full max-w-4xl mx-auto scroll-smooth scrollbar-subtle">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center px-4">
                        <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900/30 rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                            <Sparkles className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <h2 className="text-2xl font-bold text-slate-800 dark:text-ts-text mb-2">Welcome to HR Copilot</h2>
                        <p className="text-slate-500 dark:text-ts-text-secondary max-w-md">
                            I'm your AI assistant for all HR-related questions. Ask me about policies, benefits, onboarding, or general employee guidance.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {messages.map((message) => (
                            <MessageItem key={message.id} message={message} />
                        ))}

                        {isTyping && (
                            <div className="flex w-full mb-6 justify-start">
                                <div className="flex max-w-[80%] md:max-w-[70%] flex-row block">
                                    <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 dark:bg-ts-surface-hover text-indigo-600 dark:text-indigo-400 mr-3 mt-1">
                                        <Bot className="w-5 h-5" />
                                    </div>
                                    <div className="flex flex-col items-start block">
                                        <div className="flex items-center space-x-2 mb-1">
                                            <span className="text-xs font-semibold text-slate-700 dark:text-ts-text">HR Copilot</span>
                                        </div>
                                        {/* Flat typing indicator */}
                                        <div className="py-2 text-slate-800 dark:text-ts-text flex items-center space-x-1.5 h-10 px-1">
                                            <div className="w-1.5 h-1.5 bg-indigo-500 dark:bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                            <div className="w-1.5 h-1.5 bg-indigo-500 dark:bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                            <div className="w-1.5 h-1.5 bg-indigo-500 dark:bg-indigo-400 rounded-full animate-bounce"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input Area */}
            <ChatInput onSendMessage={onSendMessage} isSending={isTyping} />
        </div>
    );
}
