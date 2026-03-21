export interface Message {
    id: string;
    role: 'user' | 'ai';
    content: string;
    timestamp: Date;
}

export interface ChatSession {
    id: string;
    title: string;
    updatedAt: Date;
    messages: Message[];
}
