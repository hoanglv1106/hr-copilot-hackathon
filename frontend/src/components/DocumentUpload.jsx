import React, { useState, useRef } from 'react';
import { Upload } from 'lucide-react';
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
        w-full px-3 py-2.5 rounded-xl cursor-pointer
        border transition-all duration-300 ease-out
        flex items-center gap-3 shadow-[0_1px_2px_rgba(0,0,0,0.02)]
        ${isDragging
          ? 'border-peach bg-[#FDFBF7] dark:bg-[#2A2421]'
          : 'border-[#EBE5D9] dark:border-[#3E352F] bg-white dark:bg-[#1E1A18] hover:border-peach/40 hover:shadow-sm'
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

      {isUploading ? (
        <>
          <div className="w-7 h-7 rounded-lg bg-peach/10 flex items-center justify-center flex-shrink-0">
            <div className="w-3.5 h-3.5 border-2 border-peach border-t-transparent rounded-full animate-spin" />
          </div>
          <span className="text-[12px] font-medium text-text-secondary dark:text-dark-text-secondary">Đang tải lên...</span>
        </>
      ) : (
        <>
          <div className="w-8 h-8 rounded-xl bg-peach/10 dark:bg-peach/10 border border-peach/20 dark:border-peach/20 flex items-center justify-center flex-shrink-0 text-peach">
            <Upload className="w-4 h-4" strokeWidth={2.5} />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[13px] font-bold tracking-tight text-[#E87E60] dark:text-[#F39A80] truncate">
              Tải tài liệu PDF
            </p>
            <p className="text-[11px] text-[#A6998A] dark:text-[#9A8D7E] mt-[2px] font-medium truncate">
              Kéo thả hoặc nhấn để chọn
            </p>
          </div>
        </>
      )}
    </div>
  );
}
