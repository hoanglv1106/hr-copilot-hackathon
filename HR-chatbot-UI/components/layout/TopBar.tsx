'use client';

import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';

export function TopBar() {
    const { theme, toggleTheme } = useTheme();

    return (
        <div className="flex items-center justify-end px-6 py-3 border-b border-slate-200 dark:border-ts-border bg-white dark:bg-ts-surface transition-colors duration-200">
            <button
                onClick={toggleTheme}
                className="p-2 rounded-full text-slate-500 hover:bg-slate-100 dark:text-ts-text-secondary dark:hover:bg-ts-surface-hover transition-colors"
                aria-label="Toggle theme"
            >
                {theme === 'dark' ? (
                    <Sun className="w-5 h-5" />
                ) : (
                    <Moon className="w-5 h-5" />
                )}
            </button>
        </div>
    );
}
