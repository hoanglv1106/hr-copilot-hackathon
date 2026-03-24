import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ChatWindow from './components/ChatWindow';
import DocumentUpload from './components/DocumentUpload';

/**
 * App Component - Root component của ứng dụng
 * 
 * Layout: Sidebar (25%) + MainContent (75%)
 * - Sidebar: Logo, tiêu đề, DocumentUpload component
 * - MainContent: ChatWindow component
 * - ToastContainer: Hiển thị toast notifications
 */

export default function App() {
  return (
    <div className="h-screen flex bg-gray-100">
      {/* ToastContainer cho react-toastify */}
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

      {/* Sidebar - 25% width */}
      <div className="w-1/4 bg-white border-r border-gray-300 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-300">
          {/* Logo and Title */}
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">HR</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">HR Copilot</h1>
          </div>
          <p className="text-xs text-gray-500">Admin Assistant</p>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {/* Upload Document Section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-900 mb-3">
                📚 Tải tài liệu
              </h2>
              <DocumentUpload />
            </div>

            {/* Info Section */}
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mt-6">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">
                💡 Mẹo sử dụng
              </h3>
              <ul className="text-xs text-blue-800 space-y-2">
                <li>✓ Tải PDF chính sách nhân sự</li>
                <li>✓ AI sẽ học hỏi từ tài liệu</li>
                <li>✓ Đặt câu hỏi qua chat</li>
                <li>✓ Phản hồi nhanh & chính xác</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-300 bg-gray-50">
          <p className="text-xs text-gray-500 text-center">
            v1.0.0
          </p>
        </div>
      </div>

      {/* Main Content - 75% width */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Top Bar */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-md">
          <h2 className="text-lg font-semibold">Hỏi đáp chính sách nhân sự</h2>
          <p className="text-sm text-blue-100 mt-1">Sử dụng AI để giải đáp nhanh chóng</p>
        </div>

        {/* Chat Window */}
        <ChatWindow />
      </div>
    </div>
  );
}
