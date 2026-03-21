'use client';

import React from 'react';
import { Plus, Settings, User } from 'lucide-react';
import { ChatHistory } from './ChatHistory';
import { ChatSession } from '@/types';

interface SidebarProps {
    sessions: ChatSession[];
    activeSessionId?: string;
    onSelectSession: (id: string) => void;
    onNewChat: () => void;
    onDeleteSession?: (id: string) => void;
    onShareSession?: (id: string) => void;
}

export function Sidebar({ sessions, activeSessionId, onSelectSession, onNewChat, onDeleteSession, onShareSession }: SidebarProps) {
    return (
        <div className="hidden md:flex flex-col w-72 bg-white dark:bg-ts-surface border-r border-slate-200 dark:border-ts-border h-screen py-4 shadow-[1px_0_10px_rgba(0,0,0,0.02)] dark:shadow-none transition-colors duration-200 z-10">
            {/* Header & New Chat Button */}
            <div className="px-4 mb-4">
                <div className="flex items-center justify-between mb-6 px-2">
                    <div className="font-bold text-xl text-indigo-600 dark:text-indigo-400">
                        HR Copilot
                    </div>
                </div>

                <button
                    onClick={onNewChat}
                    className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 text-white py-2.5 px-4 rounded-xl transition-colors duration-200 shadow-sm font-medium text-sm"
                >
                    <Plus className="w-5 h-5" />
                    <span>New Chat</span>
                </button>
            </div>

            {/* Chat History */}
            <ChatHistory
                sessions={sessions}
                activeSessionId={activeSessionId}
                onSelectSession={onSelectSession}
                onDeleteSession={onDeleteSession}
                onShareSession={onShareSession}
            />

            {/* Footer / User Profile */}
            <div className="mt-auto px-4 pt-4 border-t border-slate-200 dark:border-ts-border/50">
                <div className="flex items-center space-x-3 p-2 rounded-xl hover:bg-slate-100/50 dark:hover:bg-ts-surface-hover/50 transition-colors cursor-pointer text-sm text-slate-600 dark:text-ts-text-secondary">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center shrink-0 text-indigo-600 dark:text-indigo-400">
                        <User className="w-4 h-4" />
                    </div>
                    <div className="flex-1 font-medium truncate">
                        HR Manager
                    </div>
                    <button className="p-1 hover:bg-slate-200 dark:hover:bg-ts-surface-hover rounded-lg text-slate-400 dark:text-ts-text-secondary transition-colors">
                        <Settings className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
