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
                    onClick={onSend}
                    disabled={isLoading || !input.trim()}
                    className={`
            px-4 py-3 rounded-lg font-medium
            transition-all duration-200
            flex items-center gap-2
            ${isLoading || !input.trim()
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
    );
}
