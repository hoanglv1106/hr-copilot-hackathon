import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Brain } from 'lucide-react';

export default function MessageBubble({ message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
            {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-[#FDFBF7] dark:bg-[#2A2421] border border-[#EBE5D9] dark:border-[#3E352F] shadow-sm flex items-center justify-center mr-4 flex-shrink-0 mt-1 p-1 text-peach">
                    <Brain strokeWidth={2.5} className="w-full h-full" />
                </div>
            )}
            
            <div
                className={`
                    ${isUser ? 'max-w-[75%]' : 'max-w-[85%]'} 
                    transition-all duration-200
                    ${isUser
                        ? 'bg-[#FDFBF7] dark:bg-[#2A2421] border border-[#EBE5D9] dark:border-[#3E352F] rounded-2xl px-5 py-3.5 shadow-sm text-[15px]'
                        : 'pt-1.5 text-[15px]'
                    } text-text-primary dark:text-dark-text
                `}
            >
                {message.role === 'assistant' ? (
                    <ReactMarkdown
                        className="prose prose-sm dark:prose-invert max-w-none"
                        components={{
                            p: ({ children }) => <p className="mb-2 last:mb-0 text-sm leading-relaxed">{children}</p>,
                            table: ({ children }) => (
                                <table className="border-collapse border border-border dark:border-dark-border w-full my-2 text-sm">
                                    {children}
                                </table>
                            ),
                            th: ({ children }) => (
                                <th className="border border-border dark:border-dark-border p-2 bg-surface-alt dark:bg-dark-hover font-semibold text-text-primary dark:text-dark-text text-left">
                                    {children}
                                </th>
                            ),
                            td: ({ children }) => (
                                <td className="border border-border dark:border-dark-border p-2 text-sm">{children}</td>
                            ),
                            strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                            em: ({ children }) => <em className="italic">{children}</em>,
                            ul: ({ children }) => (
                                <ul className="list-disc list-inside my-2 text-sm">{children}</ul>
                            ),
                            ol: ({ children }) => (
                                <ol className="list-decimal list-inside my-2 text-sm">{children}</ol>
                            ),
                            li: ({ children }) => <li className="mb-1">{children}</li>,
                            code: ({ children }) => (
                                <code className="bg-dark-bg dark:bg-dark-card text-peach-light px-1.5 py-0.5 rounded-md text-xs font-mono">
                                    {children}
                                </code>
                            ),
                        }}
                    >
                        {message.content}
                    </ReactMarkdown>
                ) : (
                    <p className="text-sm leading-relaxed">{message.content}</p>
                )}
            </div>
        </div>
    );
}
