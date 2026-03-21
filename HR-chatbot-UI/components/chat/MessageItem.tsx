'use client';

import React from 'react';
import { Bot, User } from 'lucide-react';
import { Message } from '@/types';
import ReactMarkdown from 'react-markdown';

interface MessageItemProps {
    message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
    const isAI = message.role === 'ai';

    return (
        <div className={`flex w-full mb-6 ${isAI ? 'justify-start' : 'justify-end'}`}>
            <div className={`flex max-w-[80%] md:max-w-[70%] ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>

                {/* Avatar */}
                <div className={`flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full mt-1 ${isAI
                    ? 'bg-indigo-100 dark:bg-ts-surface-hover text-indigo-600 dark:text-indigo-400 mr-3'
                    : 'bg-indigo-600 dark:bg-indigo-500 text-white ml-3'
                    }`}>
                    {isAI ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                </div>

                {/* Message Bubble */}
                <div className={`flex flex-col ${isAI ? 'items-start' : 'items-end'}`}>
                    <div className={`flex items-center space-x-2 mb-1 ${!isAI && 'flex-row-reverse space-x-reverse'}`}>
                        <span className="text-xs font-semibold text-slate-700 dark:text-ts-text">
                            {isAI ? 'HR Copilot' : 'You'}
                        </span>
                        <span className="text-[10px] text-slate-400 dark:text-ts-text-secondary">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                    </div>

                    <div className={`text-[15px] leading-relaxed ${isAI
                        ? 'text-slate-800 dark:text-ts-text pt-1 [&_p]:mb-4 [&_p:last-child]:mb-0 [&_ul]:list-disc [&_ul]:ml-6 [&_ul]:mb-4 [&_ol]:list-decimal [&_ol]:ml-6 [&_ol]:mb-4 [&_li]:mb-1 [&_pre]:bg-slate-100 [&_pre]:dark:bg-ts-surface [&_pre]:p-3 [&_pre]:rounded-lg [&_pre]:overflow-x-auto [&_pre]:mb-4 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:bg-slate-100 [&_code]:dark:bg-ts-surface [&_code]:rounded-md [&_code]:text-sm [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mb-4 [&_h2]:text-xl [&_h2]:font-bold [&_h2]:mb-3 [&_h3]:text-lg [&_h3]:font-bold [&_h3]:mb-2 [&_a]:text-indigo-600 [&_a]:dark:text-indigo-400 [&_a]:underline [&_blockquote]:border-l-4 [&_blockquote]:border-slate-300 [&_blockquote]:dark:border-ts-border [&_blockquote]:pl-4 [&_blockquote]:italic'
                        : 'px-5 py-3.5 rounded-2xl bg-indigo-600 dark:bg-indigo-500 text-white rounded-tr-sm shadow-sm'
                        }`}>
                        {isAI ? (
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                        ) : (
                            message.content.split('\\n').map((line, i) => (
                                <React.Fragment key={i}>
                                    {line}
                                    {i !== message.content.split('\\n').length - 1 && <br />}
                                </React.Fragment>
                            ))
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
