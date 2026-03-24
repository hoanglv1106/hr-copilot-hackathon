import React, { useState, useRef } from 'react';
import { Upload, FileText } from 'lucide-react';
import { toast } from 'react-toastify';
import { uploadDocument } from '../services/api';

export default function DocumentUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleUploadFile = async (file) => {
    if (!file) return;

    if (!file.type.includes('pdf')) {
      toast.error('❌ Chỉ chấp nhận file PDF');
      return;
    }

    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error('❌ File quá lớn (tối đa 50MB)');
      return;
    }

    setIsUploading(true);

    try {
      const { status, message } = await uploadDocument(file);

      if (status === 'warning') {
        toast.warning(`⚠️ ${message}`);
      } else if (status === 'success') {
        toast.success(`✅ ${message}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('❌ Lỗi upload file. Vui lòng thử lại.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      handleUploadFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];
    if (file) {
      handleUploadFile(file);
    }
  };

  return (
    <div
      className={`
        w-full p-6 mb-6 border-2 border-dashed rounded-lg
        transition-all duration-200 cursor-pointer
        ${isDragging
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 bg-gray-50 hover:border-blue-400'
        }
        ${isUploading ? 'opacity-60 pointer-events-none' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClickUpload}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="hidden"
      />

      <div className="flex flex-col items-center justify-center gap-3">
        {isUploading ? (
          <>
            <div className="animate-spin">
              <Upload className="w-8 h-8 text-blue-500" />
            </div>
            <p className="text-sm font-medium text-gray-700">Đang upload...</p>
          </>
        ) : (
          <>
            <FileText className="w-8 h-8 text-gray-400" />
            <div className="text-center">
              <p className="text-sm font-medium text-gray-900">
                Kéo & thả PDF vào đây hoặc bấm để chọn
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Tối đa 50MB, format PDF
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
