"""
File: ingest_pipeline.py
Công dụng: Script xử lý PDF và đẩy vector lên Qdrant (chạy tay, không phải runtime)

Quy trình:
1. Đọc PDF từ mock_data/ folder
2. Text extraction từ PDF (qua PyPDF2 hoặc pdfplumber)
3. Text cleaning (normalize, remove noise)
4. Chunking text (chia thành các chunk nhỏ với overlap)
5. Tạo embedding cho mỗi chunk (qua embedding model)
6. Insert vectors vào Qdrant với metadata (document_name, chunk_id, text)
7. Log kết quả (số chunks, số vectors inserted)

Chạy bằng: python scripts/ingest_pipeline.py
"""
