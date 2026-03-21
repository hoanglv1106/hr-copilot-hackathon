import logging
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Import LangChain components
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader

# Import PDF parsing libraries
import pdfplumber

# Import custom utilities
from app.utils.text_cleaner import clean_vietnamese_text


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

if not GEMINI_API_KEY or not QDRANT_URL:
    logger.error("Missing environment variables: GEMINI_API_KEY or QDRANT_URL")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
PDF_FOLDER = PROJECT_ROOT / "mock_data"


def load_pdf_with_fallback(pdf_path: Path) -> list[Document]:
    """
    Load PDF file with table optimization (ĐÃ FIX LỖI RÁC VÀ NHÂN ĐÔI DATA)
    """
    documents = []
    
    try:
        logger.info(f"Loading and extracting tables from {pdf_path.name}...")
        
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                content_parts = []
                
                # 1. Tìm bảng trên trang
                tables = page.find_tables()
                
                # 2. Lấy chữ NGOẠI TRỪ chữ trong bảng
                text_content = ""
                if tables:
                    non_table_page = page.filter(lambda obj: not any(t.bbox[0] <= obj["x0"] <= t.bbox[2] and t.bbox[1] <= obj["top"] <= t.bbox[3] for t in tables))
                    text_content = non_table_page.extract_text()
                else:
                    text_content = page.extract_text()
                
                if text_content and text_content.strip():
                    content_parts.append(text_content)
                
                # 3. Lấy dữ liệu bảng convert sang Markdown
                extracted_tables = page.extract_tables()
                if extracted_tables:
                    for table_idx, table in enumerate(extracted_tables):
                        try:
                            markdown_table = _table_to_markdown(table)
                            if markdown_table:
                                content_parts.append(f"\n\n**Table {table_idx + 1}:**\n{markdown_table}")
                        except Exception as e:
                            logger.warning(f"Error converting table {table_idx}: {e}")
                            continue
                
                full_content = "\n".join(content_parts)
                full_content = clean_vietnamese_text(full_content)
                
                if not full_content.strip():
                    continue
                
                doc = Document(
                    page_content=full_content,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_num,
                        "has_tables": bool(tables)
                    }
                )
                documents.append(doc)
        
        logger.info(f"Successfully loaded {len(documents)} pages with pdfplumber")
        return documents
    
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}, falling back to PyPDFLoader...")
        documents = []
    
    # ... (Giữ nguyên phần try catch PyPDFLoader ở dưới của ông) ...
    try:
        logger.info(f"Falling back to PyPDFLoader for basic text extraction...")
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        
        for doc in docs:
            cleaned_content = clean_vietnamese_text(doc.page_content)
            
            if not cleaned_content.strip():
                continue
            
            page_num = 1
            if "page" in doc.metadata:
                page_num = int(doc.metadata["page"]) + 1
            
            new_doc = Document(
                page_content=cleaned_content,
                metadata={
                    "source": pdf_path.name,
                    "page": page_num,
                    "has_tables": False
                }
            )
            documents.append(new_doc)
        
        logger.info(f"Successfully loaded {len(documents)} pages with PyPDFLoader")
        return documents
    
    except Exception as e:
        logger.error(f"Both pdfplumber and PyPDFLoader failed: {e}")
        return []


def _table_to_markdown(table: list[list]) -> str:
    """
    Convert table list to markdown format (ĐÃ FIX LỖI \n LÀM VỠ BẢNG)
    """
    if not table or len(table) == 0:
        return ""
    
    try:
        lines = []
        
        for row_idx, row in enumerate(table):
            # Xóa \n và \r để giữ cấu trúc bảng
            cells = [str(cell).replace('\n', ' ').replace('\r', '').strip() if cell else "" for cell in row]
            markdown_row = "| " + " | ".join(cells) + " |"
            lines.append(markdown_row)
            
            if row_idx == 0:
                separator = "| " + " | ".join(["---"] * len(row)) + " |"
                lines.append(separator)
        
        return "\n".join(lines)
    
    except Exception as e:
        logger.warning(f"Error converting table to markdown: {e}")
        return ""


def main() -> None:
    """
    Execute PDF processing pipeline with optimized table extraction.
    Pipeline steps:
    1. Load PDF and extract tables (pdfplumber) to markdown
    2. Clean text and fix page numbers
    3. Chunk with MarkdownTextSplitter (preserves tables)
    4. Batch embed and push to Qdrant
    """
    try:
        logger.info("Starting PDF loading and table extraction...")
        
        if not PDF_FOLDER.exists():
            logger.error(f"Directory {PDF_FOLDER} does not exist!")
            sys.exit(1)
        
        pdf_files = list(PDF_FOLDER.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {PDF_FOLDER}")
            return
        
        logger.info(f"Found {len(pdf_files)} files. Starting load...")
        
        cleaned_documents = []
        for pdf_file in pdf_files:
            logger.info(f"Loading: {pdf_file.name}")
            docs = load_pdf_with_fallback(pdf_file)
            cleaned_documents.extend(docs)
        
        if not cleaned_documents:
            logger.error("No documents loaded successfully!")
            sys.exit(1)
        
        logger.info(f"Loaded {len(cleaned_documents)} pages from {len(pdf_files)} files.")
        
        logger.info("Chunking documents with MarkdownTextSplitter...")
        
        text_splitter = MarkdownTextSplitter(chunk_size=2000, chunk_overlap=200)
        raw_chunks = text_splitter.split_documents(cleaned_documents)
        
        chunks = [c for c in raw_chunks if c.page_content.strip()]
        
        if not chunks:
            logger.error("No chunks created!")
            sys.exit(1)
            
        logger.info(f"Created {len(chunks)} chunks (table content preserved).")
        
        logger.info("Embedding and pushing to Qdrant...")
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=GEMINI_API_KEY,
        )
        
        COLLECTION_NAME = "hr_policies"
        batch_size = 10
        total_chunks = len(chunks)
        
        vector_store = None
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            logger.info(f"Pushing batch {i // batch_size + 1} (chunks {i} to {min(i + batch_size, total_chunks)})...")
            
            try:
                if i == 0:
                    vector_store = QdrantVectorStore.from_documents(
                        documents=batch,
                        embedding=embeddings,
                        url=QDRANT_URL,
                        collection_name=COLLECTION_NAME,
                        force_recreate=True, 
                    )
                    logger.info(f"Batch 1 (recreate) pushed successfully.")
                else:
                    if vector_store:
                        vector_store.add_documents(batch)
                        logger.info(f"Batch {i // batch_size + 1} (add) pushed successfully.")
                
                if i + batch_size < total_chunks:
                    time.sleep(2) 
            except Exception as e:
                logger.error(f"Error pushing batch {i // batch_size + 1}: {e}", exc_info=True)
                raise 
        
        logger.info("Pipeline completed successfully.")
        
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()