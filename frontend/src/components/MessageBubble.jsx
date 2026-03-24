import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageBubble({ message }) {
    return (
        <div
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
        >
            <div
                className={`max-w-[70%] rounded-lg p-4 ${message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-900'
                    }`}
            >
                {message.role === 'assistant' ? (
                    <ReactMarkdown
                        className="prose prose-sm dark:prose-invert max-w-none"
                        components={{
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            table: ({ children }) => (
                                <table className="border-collapse border border-gray-400 w-full my-2">
                                    {children}
                                </table>
                            ),
                            th: ({ children }) => (
                                <th className="border border-gray-400 p-2 bg-gray-300 font-bold">
                                    {children}
                                </th>
                            ),
                            td: ({ children }) => (
                                <td className="border border-gray-400 p-2">{children}</td>
                            ),
                            strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                            em: ({ children }) => <em className="italic">{children}</em>,
                            ul: ({ children }) => (
                                <ul className="list-disc list-inside my-2">{children}</ul>
                            ),
                            ol: ({ children }) => (
                                <ol className="list-decimal list-inside my-2">{children}</ol>
                            ),
                            li: ({ children }) => <li className="mb-1">{children}</li>,
                            code: ({ children }) => (
                                <code className="bg-gray-800 text-white px-2 py-1 rounded text-sm">
                                    {children}
                                </code>
                            ),
                        }}
                    >
                        {message.content}
                    </ReactMarkdown>
                ) : (
                    <p className="text-sm">{message.content}</p>
                )}
            </div>
        </div>
    );
}
