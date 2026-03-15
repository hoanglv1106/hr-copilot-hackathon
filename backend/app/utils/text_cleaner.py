"""
File: text_cleaner.py
Công dụng: Utility function xử lý và chuẩn hóa text
- normalize_unicode(): Chuẩn hóa Unicode (NFC, NFKC)
- remove_extra_whitespace(): Xóa khoảng trắng thừa
- clean_pdf_text(): Xóa các ký tự lạ từ text PDF (newline, special chars)
- remove_html_tags(): Strip HTML tags
- trim_long_text(): Cut text dài vượt quá limit

Stateless utility, không depend vào database hay external services
"""
