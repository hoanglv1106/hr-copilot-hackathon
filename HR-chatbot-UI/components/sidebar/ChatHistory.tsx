'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, MoreHorizontal, Share2, Trash2 } from 'lucide-react';
import { ChatSession } from '@/types';

interface ChatHistoryProps {
    sessions: ChatSession[];
    activeSessionId?: string;
    onSelectSession: (id: string) => void;
    onDeleteSession?: (id: string) => void;
    onShareSession?: (id: string) => void;
}

export function ChatHistory({ sessions, activeSessionId, onSelectSession, onDeleteSession, onShareSession }: ChatHistoryProps) {
    const [openMenuId, setOpenMenuId] = useState<string | null>(null);
    const menuRef = useRef<HTMLDivElement>(null);

    // Close menu on click outside
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
                setOpenMenuId(null);
            }
        };
        if (openMenuId) {
            document.addEventListener('mousedown', handleClickOutside);
        }
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [openMenuId]);

    const handleMenuToggle = (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation();
        setOpenMenuId(prev => (prev === sessionId ? null : sessionId));
    };

    const handleShare = (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation();
        onShareSession?.(sessionId);
        setOpenMenuId(null);
    };

    const handleDelete = (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation();
        onDeleteSession?.(sessionId);
        setOpenMenuId(null);
    };

    return (
        <div className="flex-1 overflow-y-auto mt-4 px-3 space-y-1 scrollbar-subtle">
            <div className="text-xs font-semibold text-slate-400 dark:text-ts-text-secondary uppercase tracking-wider mb-3 px-2">
                Recent Chats
            </div>
            {sessions.map((session) => (
                <div
                    key={session.id}
                    onClick={() => onSelectSession(session.id)}
                    className={`w-full cursor-pointer group flex items-center justify-between px-3 py-2 rounded-xl transition-all duration-200 text-sm relative ${activeSessionId === session.id
                        ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 font-medium'
                        : 'text-slate-600 dark:text-ts-text-secondary hover:bg-slate-100/80 dark:hover:bg-ts-surface-hover/50 hover:text-slate-900 dark:hover:text-ts-text'
                        }`}
                >
                    <div className="flex items-center space-x-3 overflow-hidden">
                        <MessageSquare className={`w-4 h-4 shrink-0 ${activeSessionId === session.id ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 dark:text-ts-text-secondary group-hover:text-slate-600 dark:group-hover:text-ts-text'}`} />
                        <span className="truncate">{session.title}</span>
                    </div>

                    {/* Three-dot button */}
                    <div className="relative" ref={openMenuId === session.id ? menuRef : undefined}>
                        <button
                            onClick={(e) => handleMenuToggle(e, session.id)}
                            className={`p-1 rounded-md opacity-0 group-hover:opacity-100 transition-opacity ${activeSessionId === session.id ? 'hover:bg-indigo-100 dark:hover:bg-indigo-500/20' : 'hover:bg-slate-200 dark:hover:bg-ts-surface-hover'} ${openMenuId === session.id ? '!opacity-100' : ''}`}
                        >
                            <MoreHorizontal className="w-4 h-4 text-slate-400 dark:text-ts-text-secondary group-hover:text-slate-600 dark:group-hover:text-ts-text" />
                        </button>

                        {/* Dropdown Menu */}
                        {openMenuId === session.id && (
                            <div className="absolute right-0 top-full mt-1 w-44 bg-white dark:bg-ts-surface border border-slate-200 dark:border-ts-border rounded-xl shadow-lg dark:shadow-black/30 py-1 z-50 animate-in fade-in duration-150">
                                <button
                                    onClick={(e) => handleShare(e, session.id)}
                                    className="w-full flex items-center space-x-2.5 px-3 py-2 text-sm text-slate-600 dark:text-ts-text-secondary hover:bg-slate-100 dark:hover:bg-ts-surface-hover hover:text-slate-900 dark:hover:text-ts-text transition-colors"
                                >
                                    <Share2 className="w-4 h-4" />
                                    <span>Share chat</span>
                                </button>
                                <div className="mx-2 my-1 border-t border-slate-100 dark:border-ts-border/50"></div>
                                <button
                                    onClick={(e) => handleDelete(e, session.id)}
                                    className="w-full flex items-center space-x-2.5 px-3 py-2 text-sm text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                                >
                                    <Trash2 className="w-4 h-4" />
                                    <span>Delete chat</span>
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
