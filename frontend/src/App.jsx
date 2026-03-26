import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Brain } from 'lucide-react';
import ChatWindow from './components/ChatWindow';
import DocumentUpload from './components/DocumentUpload';
import ThemeToggle from './components/ThemeToggle';

export default function App() {
  return (
    <div className="h-screen flex bg-surface dark:bg-dark-bg transition-colors duration-300">
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />

      {/* Sidebar — compact & modern */}
      <div className="w-[260px] min-w-[260px] bg-sidebar dark:bg-dark-surface border-r border-[#EBE5D9] dark:border-[#3E352F] flex flex-col">
        {/* Header - Logo updated to minimalistic SaaS style */}
        <div className="px-4 py-4 flex items-center justify-between border-b border-[#EBE5D9]/50 dark:border-[#3E352F]/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-[#FDFBF7] dark:bg-[#2A2421] border border-[#EBE5D9] dark:border-[#3E352F] shadow-sm flex items-center justify-center p-1 text-peach">
              {/* Brain Logo */}
              <Brain strokeWidth={2.5} className="w-full h-full" />
            </div>
            <span className="text-[15px] font-medium tracking-tight text-text-primary dark:text-dark-text">HR Copilot</span>
          </div>
          <ThemeToggle />
        </div>

        {/* New Chat Button */}
        <div className="px-3 pt-4 pb-1">
          <button 
            className="w-full flex items-center gap-2 px-3 py-2.5 bg-white dark:bg-[#2A2421] hover:bg-[#FDFBF7] dark:hover:bg-[#3E352F] border border-[#EBE5D9] dark:border-[#3E352F] rounded-xl text-[13px] font-medium text-text-primary dark:text-dark-text transition-all shadow-sm"
            onClick={() => {
              localStorage.removeItem('hr_session_id');
              window.location.reload();
            }}
          >
            <span className="text-lg font-light leading-none mb-0.5 ml-1">+</span>
            <span>Cuộc trò chuyện mới</span>
          </button>
        </div>

        {/* Chat History area */}
        <div className="flex-1 overflow-y-auto px-3 py-2">
          <p className="text-[10px] font-medium text-text-muted/80 dark:text-dark-text-muted/80 uppercase tracking-widest mb-2.5 px-2 mt-2">
            Lịch sử
          </p>
          <div className="space-y-0.5">
            <div className="px-3 py-2.5 rounded-xl text-[13px] font-medium text-text-primary dark:text-dark-text truncate cursor-pointer bg-[#FDFBF7] dark:bg-[#2A2421] border border-[#EBE5D9] dark:border-[#3E352F] shadow-sm transition-colors">
              Cuộc trò chuyện hiện tại
            </div>
          </div>
        </div>

        {/* Upload section */}
        <div className="px-3 pb-5">
          <DocumentUpload />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-surface dark:bg-dark-bg min-w-0">
        <ChatWindow />
      </div>
    </div>
  );
}
