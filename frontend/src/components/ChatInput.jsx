import React from 'react';
import { Send, Loader } from 'lucide-react';

export default function ChatInput({ input, setInput, isLoading, onSend }) {
    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            onSend();
        }
    };

    return (
        <div className="px-4 md:px-6 pb-6 pt-2 bg-surface dark:bg-dark-bg transition-colors duration-300">
            <div className="max-w-3xl mx-auto flex items-end gap-2 p-1.5 bg-white dark:bg-[#1E1A18] border border-[#EBE5D9] dark:border-[#3E352F] shadow-sm rounded-2xl focus-within:ring-2 focus-within:ring-peach/20 focus-within:border-peach/40 transition-all">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Hỏi bất cứ điều gì..."
                    disabled={isLoading}
                    rows={1}
                    className="
                        flex-1 px-3 py-2.5 resize-none bg-transparent
                        text-text-primary dark:text-dark-text text-[14px] leading-relaxed
                        placeholder:text-text-muted/70 dark:placeholder:text-dark-text-muted/70
                        focus:outline-none disabled:opacity-50
                    "
                    style={{ minHeight: '44px', maxHeight: '160px' }}
                    onInput={(e) => {
                        e.target.style.height = '44px';
                        e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
                    }}
                />
                <button
                    onClick={onSend}
                    disabled={isLoading || !input.trim()}
                    className={`
                        w-10 h-10 rounded-xl mb-0.5 mr-0.5 flex-shrink-0 flex items-center justify-center transition-all duration-200
                        ${isLoading || !input.trim()
                            ? 'bg-[#FDFBF7] dark:bg-[#2A2421] text-[#D8D0C5] dark:text-[#5C5046] cursor-not-allowed'
                            : 'bg-peach text-white shadow-sm hover:opacity-90 active:scale-95'
                        }
                    `}
                >
                    {isLoading ? (
                        <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                        <Send className="w-4 h-4 relative -mr-0.5" />
                    )}
                </button>
            </div>
            <div className="text-center mt-3">
               <p className="text-[11px] text-text-muted/60 dark:text-dark-text-muted/60 font-medium tracking-wide">AI có thể cung cấp thông tin không chính xác. Vui lòng kiểm tra lại.</p>
            </div>
        </div>
    );
}
