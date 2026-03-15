"""
File: qdrant_client.py
Công dụng: Adapter gọi API Qdrant Vector Database
- initialize_qdrant(): Khởi tạo kết nối tới Qdrant server
- search(): Tìm kiếm vector tương tự
  Input: query_vector (embedding của câu hỏi), limit (số kết quả)
  Output: Danh sách document IDs + similarity scores
- insert_vectors(): Thêm vector vào database (dùng trong ingest pipeline)
- delete_collection(): Xóa collection (dùng khi update documents)

Quản lý toàn bộ tương tác với vector database
"""
