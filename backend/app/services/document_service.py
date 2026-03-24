import hashlib
import logging
import os
import tempfile
import time
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sqlalchemy.orm import Session
import pdfplumber

from app.utils.text_cleaner import clean_vietnamese_text
from app.models.document import DocumentRecord

logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class DocumentService:
    """Service for processing and embedding documents into Qdrant vector store."""

    def __init__(self):
        """Initialize DocumentService with API keys and configuration."""
        try:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            self.qdrant_url = os.getenv("QDRANT_URL")
            self.collection_name = "hr_policies"
            self.chunk_size = 2000
            self.chunk_overlap = 200
            self.batch_size = 10

            if not self.gemini_api_key or not self.qdrant_url:
                raise ValueError("Missing GEMINI_API_KEY or QDRANT_URL environment variables")

            logger.info("DocumentService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DocumentService: {e}", exc_info=True)
            raise

    def _load_pdf_with_fallback(self, pdf_path: Path ,original_filename: str = None ) -> list[Document]:
        """
        Load PDF file with optimized table extraction (no text duplication).
        
        OPTIMIZATION: Extract table bounding boxes FIRST, then filter out text within
        those regions before calling extract_text(). This prevents LLM from reading
        duplicated/garbled table content.
        
        PRIMARY: pdfplumber (detect + extract tables to markdown)
        FALLBACK: PyPDFLoader (simple text extraction)

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Document objects
        """
        documents = []

        try:
            logger.info(f"Loading and extracting tables from {pdf_path.name}...")

            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_num = page_idx + 1
                    content_parts = []

                    #  FIX #2: Extract tables FIRST to get their bounding boxes
                    tables = page.extract_tables()
                    table_bboxes = []
                    
                    if tables:
                        logger.info(f"Page {page_num}: Found {len(tables)} tables")
                        # Get bounding boxes of all detected tables
                        for table in page.find_tables():
                            table_bboxes.append(table.bbox)
                    
                    #  FIX #2: Filter out text objects within table bounding boxes
                    # This ensures extract_text() only gets regular text, not table content
                    if table_bboxes:
                        # Create filter to exclude text within table regions
                        filtered_page = page
                        for bbox in table_bboxes:
                            # pdfplumber's filter excludes objects OUTSIDE the given bbox
                            # We need to manually remove objects INSIDE bbox ranges
                            filtered_page = filtered_page.filter(
                                lambda obj: not (
                                    bbox[0] <= obj.get("x0", 0) < bbox[2] and
                                    bbox[1] <= obj.get("top", 0) < bbox[3]
                                )
                            )
                        text_content = filtered_page.extract_text()
                    else:
                        # No tables detected, extract all text normally
                        text_content = page.extract_text()
                    
                    if text_content and text_content.strip():
                        content_parts.append(text_content)

                    # ✅ Now add tables if they exist
                    if tables:
                        for table_idx, table in enumerate(tables):
                            try:
                                markdown_table = self._table_to_markdown(table)
                                if markdown_table:
                                    content_parts.append(
                                        f"\n\n**Table {table_idx + 1}:**\n{markdown_table}"
                                    )
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
                            "source": original_filename if original_filename else pdf_path.name,
                            "page": page_num,
                            "has_tables": bool(tables),
                        },
                    )
                    documents.append(doc)

            logger.info(f"Successfully loaded {len(documents)} pages with pdfplumber")
            return documents

        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, falling back to PyPDFLoader...")
            documents = []

        try:
            logger.info("Falling back to PyPDFLoader for basic text extraction...")
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
                        "source": original_filename if original_filename else pdf_path.name,
                        "page": page_num,
                        "has_tables": False,
                    },
                )
                documents.append(new_doc)

            logger.info(f"Successfully loaded {len(documents)} pages with PyPDFLoader")
            return documents

        except Exception as e:
            logger.error(f"Both pdfplumber and PyPDFLoader failed: {e}")
            return []

    def _table_to_markdown(self, table: list[list]) -> str:
        """
        Convert table list to markdown format with newline handling.
        
         FIX #1: Replace all newlines (\n, \r) with spaces in cell content
        to prevent markdown table structure from breaking. Each markdown row
        must be on a single line.

        Args:
            table: List of lists representing table rows

        Returns:
            Markdown formatted table string
        """
        if not table or len(table) == 0:
            return ""

        try:
            lines = []

            for row_idx, row in enumerate(table):
                # ✅ FIX #1: Clean cell content - remove newlines and strip whitespace
                cells = []
                for cell in row:
                    cell_str = str(cell) if cell else ""
                    # Replace all newlines and carriage returns with spaces
                    cell_str = re.sub(r'[\n\r]+', ' ', cell_str)
                    # Strip leading/trailing whitespace
                    cell_str = cell_str.strip()
                    # Remove extra internal spaces (multiple spaces → single space)
                    cell_str = re.sub(r'\s+', ' ', cell_str)
                    cells.append(cell_str)
                
                markdown_row = "| " + " | ".join(cells) + " |"
                lines.append(markdown_row)

                if row_idx == 0:
                    separator = "| " + " | ".join(["---"] * len(row)) + " |"
                    lines.append(separator)

            result = "\n".join(lines)
            logger.debug(f"Converted table to markdown: {len(result)} characters")
            return result

        except Exception as e:
            logger.warning(f"Error converting table to markdown: {e}")
            return ""

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file content for deduplication.

        Args:
            file_path: Path to file to hash

        Returns:
            Hexadecimal hash string
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}", exc_info=True)
            return ""

    def _check_duplicate_file(self, client: QdrantClient, file_hash: str) -> bool:
        """
        Check if file with same hash already exists in collection.

        Args:
            client: Qdrant client instance
            file_hash: Hash of file content

        Returns:
            True if duplicate exists, False otherwise
        """
        try:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="metadata.file_hash",
                        match=MatchValue(value=file_hash),
                    )
                ]
            )

            search_result = client.scroll(
                collection_name=self.collection_name,
                limit=1,
                scroll_filter=filter_condition,
            )

            if search_result and search_result[0]:
                logger.info(f"Duplicate file detected (hash: {file_hash[:16]}...)")
                return True

            return False
        except Exception as e:
            logger.warning(f"Error checking for duplicates: {e}")
            return False

    def _delete_old_versions(self, client: QdrantClient, filename: str) -> bool:
        """
        Delete all existing vectors with same source filename.

        Args:
            client: Qdrant client instance
            filename: Source filename to delete

        Returns:
            True if delete successful or nothing to delete, False on error
        """
        try:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="metadata.source",
                        match=MatchValue(value=filename),
                    )
                ]
            )

            client.delete(
                collection_name=self.collection_name,
                points_selector=filter_condition,
            )

            logger.info(f"Deleted old versions of document: {filename}")
            return True
        except Exception as e:
            logger.warning(f"No old versions to delete or error: {e}")
            return False

    def _chunk_and_embed(self, documents: list[Document], file_hash: str, qdrant_client: QdrantClient) -> bool:
        """
         FIX #3: Shared logic for chunking and embedding documents.
        
        Extracted common code from both process_and_embed_document and
        process_and_embed_document_from_db to follow DRY principle.
        
        Pipeline:
        1. Split documents into chunks using MarkdownTextSplitter
        2. Add file_hash to chunk metadata
        3. Initialize embeddings
        4. Batch push chunks to Qdrant (optimize vector store initialization)

        Args:
            documents: List of Document objects to chunk and embed
            file_hash: SHA256 hash to add to metadata
            qdrant_client: Qdrant client instance for embedding

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Chunking documents with MarkdownTextSplitter...")
            text_splitter = MarkdownTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            raw_chunks = text_splitter.split_documents(documents)

            chunks = [c for c in raw_chunks if c.page_content.strip()]

            if not chunks:
                logger.error("No chunks created after splitting")
                return False

            logger.info(f"Created {len(chunks)} chunks (markdown content preserved)")

            # Add file_hash to all chunks
            try:
                for chunk in chunks:
                    chunk.metadata["file_hash"] = file_hash
                logger.info("Updated chunk metadata with file_hash")
            except Exception as e:
                logger.warning(f"Error updating chunk metadata: {e}")

            # ✅ FIX #3: Initialize embeddings once, then do batched upserts
            logger.info("Embedding documents with GoogleGenerativeAI...")
            embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001",
                google_api_key=self.gemini_api_key,
            )

            total_chunks = len(chunks)
            vector_store = None

            for i in range(0, total_chunks, self.batch_size):
                batch = chunks[i : i + self.batch_size]
                batch_num = i // self.batch_size + 1
                logger.info(
                    f"Pushing batch {batch_num} (chunks {i} to {min(i + self.batch_size, total_chunks)})..."
                )

                try:
                    if i == 0:
                        # First batch: initialize vector store
                        vector_store = QdrantVectorStore.from_documents(
                            documents=batch,
                            embedding=embeddings,
                            url=self.qdrant_url,
                            collection_name=self.collection_name,
                        )
                        logger.info(f"Batch 1 (initialize) pushed successfully")
                    else:
                        # Subsequent batches: append to existing vector store
                        if vector_store:
                            vector_store.add_documents(batch)
                            logger.info(f"Batch {batch_num} (append) pushed successfully")

                    # Rate limiting: add delay between batches
                    if i + self.batch_size < total_chunks:
                        time.sleep(2)
                except Exception as e:
                    logger.error(f"Error pushing batch {batch_num}: {e}", exc_info=True)
                    raise

            logger.info(f"All {total_chunks} chunks embedded and pushed to Qdrant successfully")
            return True

        except Exception as e:
            logger.error(f"Error during chunking/embedding: {e}", exc_info=True)
            return False

    def process_and_embed_document(self, file_path: Path, filename: str) -> bool:
        """
        Process single PDF file and embed into Qdrant vector store.
        Includes deduplication and update logic to prevent duplicate vectors.

        Pipeline:
        1. Calculate file hash for deduplication
        2. Check if same content already exists (skip if duplicate)
        3. Delete old versions with same filename
        4. Extract, chunk, and embed PDF (using _chunk_and_embed)
        5. Append to Qdrant collection

        Args:
            file_path: Full path to PDF file
            filename: Original filename for metadata

        Returns:
            True if successful, False otherwise
        """
        qdrant_client = None

        try:
            logger.info(f"Starting document processing: {filename}")

            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False

            try:
                file_hash = self._calculate_file_hash(file_path)
                if not file_hash:
                    logger.error("Failed to calculate file hash")
                    return False
                logger.info(f"File hash calculated: {file_hash[:16]}...")
            except Exception as e:
                logger.error(f"Error calculating file hash: {e}", exc_info=True)
                return False

            try:
                qdrant_client = QdrantClient(url=self.qdrant_url)
                logger.info("Connected to Qdrant")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}", exc_info=True)
                return False

            try:
                if self._check_duplicate_file(qdrant_client, file_hash):
                    logger.info(f"Skipping document: content already exists in collection")
                    return True
            except Exception as e:
                logger.warning(f"Error checking duplicates: {e}")

            try:
                self._delete_old_versions(qdrant_client, filename)
            except Exception as e:
                logger.warning(f"Error deleting old versions: {e}")

            try:
                documents = self._load_pdf_with_fallback(file_path, original_filename=filename)
                if not documents:
                    logger.error("No documents loaded from PDF")
                    return False

                logger.info(f"Loaded {len(documents)} pages from {filename}")
            except Exception as e:
                logger.error(f"Error loading PDF: {e}", exc_info=True)
                return False

            # ✅ FIX #3: Use shared _chunk_and_embed method
            try:
                success = self._chunk_and_embed(documents, file_hash, qdrant_client)
                if success:
                    logger.info(f"Document {filename} processed and embedded successfully")
                    return True
                else:
                    logger.error(f"Failed to chunk and embed document {filename}")
                    return False
            except Exception as e:
                logger.error(f"Error in chunk_and_embed: {e}", exc_info=True)
                return False

        except Exception as e:
            logger.error(f"Critical error processing document: {e}", exc_info=True)
            return False

    def process_and_embed_document_from_db(
        self, document_id: str, db: Session
    ) -> bool:
        """
        Process document stored in PostgreSQL database and embed into Qdrant.
        File bytes are extracted from DB, written to temporary file for PDF processing,
        then temporary file is deleted after processing.

        Pipeline:
        1. Query DocumentRecord from database
        2. Write file_bytes to temporary file
        3. Calculate file hash
        4. Delete old versions with same filename
        5. Extract, chunk, and embed PDF (using _chunk_and_embed)
        6. Delete temporary file

        Args:
            document_id: UUID of DocumentRecord in database
            db: SQLAlchemy database session

        Returns:
            True if successful, False otherwise
        """
        temp_file_path = None
        qdrant_client = None

        try:
            logger.info(f"Starting document processing from database: {document_id}")

            try:
                doc_record = db.query(DocumentRecord).filter(
                    DocumentRecord.id == document_id
                ).first()

                if not doc_record:
                    logger.error(f"DocumentRecord not found: {document_id}")
                    return False

                logger.info(f"Retrieved document from database: {doc_record.filename}")
            except Exception as e:
                logger.error(f"Error querying database: {e}", exc_info=True)
                return False

            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf", mode="wb"
                ) as temp_file:
                    temp_file.write(doc_record.file_data)
                    temp_file_path = temp_file.name

                logger.info(f"Temporary file created: {temp_file_path} ({len(doc_record.file_data)} bytes)")
            except Exception as e:
                logger.error(f"Error creating temporary file: {e}", exc_info=True)
                return False

            try:
                file_path = Path(temp_file_path)
                file_hash = self._calculate_file_hash(file_path)

                if not file_hash:
                    logger.error("Failed to calculate file hash")
                    return False

                logger.info(f"File hash calculated: {file_hash[:16]}...")
            except Exception as e:
                logger.error(f"Error calculating file hash: {e}", exc_info=True)
                return False

            try:
                qdrant_client = QdrantClient(url=self.qdrant_url)
                logger.info("Connected to Qdrant")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}", exc_info=True)
                return False

            try:
                self._delete_old_versions(qdrant_client, doc_record.filename)
            except Exception as e:
                logger.warning(f"Error deleting old versions: {e}")

            try:
                documents = self._load_pdf_with_fallback(file_path, original_filename=doc_record.filename)
                if not documents:
                    logger.error("No documents loaded from PDF")
                    return False

                logger.info(f"Loaded {len(documents)} pages from {doc_record.filename}")
            except Exception as e:
                logger.error(f"Error loading PDF: {e}", exc_info=True)
                return False

            # ✅ FIX #3: Use shared _chunk_and_embed method
            try:
                success = self._chunk_and_embed(documents, file_hash, qdrant_client)
                if success:
                    logger.info(f"Document {doc_record.filename} processed and embedded successfully")
                    return True
                else:
                    logger.error(f"Failed to chunk and embed document {doc_record.filename}")
                    return False
            except Exception as e:
                logger.error(f"Error in chunk_and_embed: {e}", exc_info=True)
                return False

        except Exception as e:
            logger.error(f"Critical error processing document from database: {e}", exc_info=True)
            return False
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Temporary file deleted: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Error deleting temporary file: {e}", exc_info=True)

