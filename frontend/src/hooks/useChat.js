import { useState, useEffect, useRef } from 'react';
import { getChatHistory, sendChatMessage } from '../services/api';

export default function useChat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                setIsLoadingHistory(true);
                const historyMessages = await getChatHistory();
                setMessages(historyMessages);
            } catch (error) {
                console.error('Failed to load history:', error);
                setMessages([]);
            } finally {
                setIsLoadingHistory(false);
            }
        };

        loadHistory();
    }, []);

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const answer = await sendChatMessage(input);

            const aiMessage = {
                id: `ai-${Date.now()}`,
                role: 'assistant',
                content: answer,
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            console.error('Chat error:', error);

            const errorMessage = {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: '❌ Lỗi kết nối với AI. Vui lòng thử lại.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        input,
        setInput,
        isLoading,
        isLoadingHistory,
        messagesEndRef,
        handleSendMessage,
    };
}
