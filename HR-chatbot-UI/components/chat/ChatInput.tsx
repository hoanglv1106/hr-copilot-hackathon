'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';

interface ChatInputProps {
    onSendMessage: (content: string) => void;
    isSending: boolean;
}

export function ChatInput({ onSendMessage, isSending }: ChatInputProps) {
    const [input, setInput] = useState('');
    const inputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto';
            inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
        }
    }, [input]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isSending) {
            onSendMessage(input.trim());
            setInput('');
            if (inputRef.current) {
                inputRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className="bg-white dark:bg-ts-bg border-t border-slate-200 dark:border-ts-border p-4 transition-colors duration-200">
            <div className="max-w-4xl mx-auto">
                <form
                    onSubmit={handleSubmit}
                    className="relative flex items-end bg-slate-50 dark:bg-ts-surface border border-slate-200 dark:border-ts-border rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-indigo-100 dark:focus-within:ring-indigo-900/30 focus-within:border-indigo-500 dark:focus-within:border-indigo-500 transition-all"
                >
                    <button
                        type="button"
                        className="p-3 text-slate-400 dark:text-ts-text-secondary hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors rounded-xl flex-shrink-0"
                    >
                        <Paperclip className="w-5 h-5" />
                    </button>

                    <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your message to HR Copilot..."
                        className="flex-1 max-h-[120px] min-h-[44px] bg-transparent py-3 px-2 resize-none outline-none text-slate-700 dark:text-ts-text text-[15px] leading-relaxed placeholder:text-slate-400 dark:placeholder:text-ts-text-secondary"
                        rows={1}
                        disabled={isSending}
                    />

                    <button
                        type="submit"
                        disabled={!input.trim() || isSending}
                        className={`p-2 m-1.5 rounded-xl flex-shrink-0 transition-all flex items-center justify-center ${input.trim() && !isSending
                            ? 'bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 shadow-sm'
                            : 'bg-slate-200 dark:bg-ts-surface-hover text-slate-400 dark:text-ts-text-secondary/50 cursor-not-allowed'
                            }`}
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
                <div className="text-center mt-2">
                    <span className="text-[11px] text-slate-400 dark:text-ts-text-secondary">
                        HR Copilot can make mistakes. Consider verifying important information.
                    </span>
                </div>
            </div>
        </div>
    );
}
