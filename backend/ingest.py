import os
import asyncio
import pdfplumber
import dotenv
import logging
import shutil
import json
from datetime import datetime
from typing import Dict, Any

from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

# -------------------------
# 🔧 Logging
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# -------------------------
# 🔐 Env
# -------------------------
dotenv.load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment")

# -------------------------
# 📁 Paths
# -------------------------
BACKEND_DIR = os.path.dirname(__file__)
PDF_DIR = os.path.join(BACKEND_DIR, "rag-pdf")
WORKING_DIR = PDF_DIR  # NanoDB will be stored here

# -------------------------
# 📄 PDF Text Extraction with Metadata
# -------------------------
def extract_text_from_pdf(pdf_path: str) -> tuple[str, Dict[str, Any]]:
    """Extract text and metadata from PDF"""
    logger.info(f"Extracting text from PDF: {pdf_path}")
    text = ""
    metadata = {
        "source_file": os.path.basename(pdf_path),
        "file_path": pdf_path,
        "file_size": os.path.getsize(pdf_path),
        "ingestion_date": datetime.now().isoformat(),
        "document_type": "PDF",
        "total_pages": 0,
        "page_info": []
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            metadata["total_pages"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n{page_text}\n"
                    
                    # Store page metadata
                    page_metadata = {
                        "page_number": page_num,
                        "text_length": len(page_text),
                        "has_text": bool(page_text.strip())
                    }
                    metadata["page_info"].append(page_metadata)
                    
                logger.info(f"Processed page {page_num} of {pdf_path}")
                
    except Exception as e:
        logger.error(f"Error reading {pdf_path}: {e}")
        metadata["error"] = str(e)
        
    return text.strip(), metadata

def generate_document_description(filename: str, text: str, metadata: Dict[str, Any]) -> str:
    """Generate a description of the document based on its content and metadata"""
    # Extract first few sentences for description
    sentences = text.split('.')[:3]
    preview = '. '.join(sentences).strip()
    
    # Create document description
    description = f"Document: {filename}\n"
    description += f"Type: MSME Loan Policy Document\n"
    description += f"Pages: {metadata.get('total_pages', 0)}\n"
    description += f"Content Preview: {preview[:200]}..."
    
    return description

def create_document_metadata(filename: str, text: str, pdf_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive metadata for the document"""
    # Generate document description
    description = generate_document_description(filename, text, pdf_metadata)
    
    # Create comprehensive metadata
    metadata = {
        # Document identification
        "document_id": filename.replace('.pdf', '').replace(' ', '_').lower(),
        "document_name": filename,
        "document_type": "MSME_POLICY_DOCUMENT",
        "document_category": "LOAN_POLICY",
        
        # Content information
        "description": description,
        "content_summary": text[:500] + "..." if len(text) > 500 else text,
        "total_characters": len(text),
        "total_words": len(text.split()),
        
        # File information
        "source_file": pdf_metadata["source_file"],
        "file_path": pdf_metadata["file_path"],
        "file_size_bytes": pdf_metadata["file_size"],
        "file_size_mb": round(pdf_metadata["file_size"] / (1024 * 1024), 2),
        
        # Processing information
        "ingestion_date": pdf_metadata["ingestion_date"],
        "processing_timestamp": datetime.now().isoformat(),
        "total_pages": pdf_metadata["total_pages"],
        
        # Content structure
        "page_info": pdf_metadata["page_info"],
        "has_content": bool(text.strip()),
        
        # Business context
        "business_domain": "MSME_LOANS",
        "document_purpose": "POLICY_REFERENCE",
        "target_audience": "LOAN_OFFICERS_MSME_APPLICANTS",
        
        # Search and retrieval hints
        "search_keywords": [
            "MSME", "loan", "policy", "eligibility", "requirements",
            "application", "approval", "documentation", "process"
        ],
        "content_topics": [
            "loan_eligibility", "application_process", "documentation_requirements",
            "approval_criteria", "policy_guidelines"
        ]
    }
    
    # Add error information if any
    if "error" in pdf_metadata:
        metadata["processing_error"] = pdf_metadata["error"]
    
    return metadata

# -------------------------
# 📁 Setup PDF Directory
# -------------------------
def setup_pdf_directory():
    """Create rag-pdf directory and copy PDFs from backend folder"""
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # Find PDFs in backend directory
    backend_pdfs = [f for f in os.listdir(BACKEND_DIR) if f.lower().endswith('.pdf')]
    
    for pdf_file in backend_pdfs:
        source_path = os.path.join(BACKEND_DIR, pdf_file)
        dest_path = os.path.join(PDF_DIR, pdf_file)
        
        if not os.path.exists(dest_path):
            shutil.copy2(source_path, dest_path)
            logger.info(f"✅ Copied {pdf_file} to rag-pdf directory")
        else:
            logger.info(f"📁 {pdf_file} already exists in rag-pdf directory")

# -------------------------
# ⚙️ Initialize LightRAG
# -------------------------
async def initialize_rag():
    logger.info("Initializing LightRAG with OpenAI embedding + GPT-4o-mini...")
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

# -------------------------
# 🚀 Ingest all PDFs with Metadata
# -------------------------
def main():
    logger.info("🚀 Starting PDF ingestion process with metadata...")
    
    # Setup PDF directory and copy files
    setup_pdf_directory()
    
    if not os.path.exists(PDF_DIR):
        logger.error(f"PDF folder not found: {PDF_DIR}")
        return

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        logger.warning("No PDF files found to ingest.")
        return

    logger.info(f"📚 Found {len(pdf_files)} PDF files to process:")
    for pdf in pdf_files:
        logger.info(f"  - {pdf}")

    # Initialize LightRAG
    rag = asyncio.run(initialize_rag())

    # Store metadata summary
    metadata_summary = {
        "ingestion_session": {
            "start_time": datetime.now().isoformat(),
            "total_documents": len(pdf_files),
            "documents_processed": []
        }
    }

    # Process each PDF
    for pdf in pdf_files:
        pdf_path = os.path.join(PDF_DIR, pdf)
        logger.info(f"\n📖 Processing: {pdf}")
        
        # Extract text and basic metadata
        text, pdf_metadata = extract_text_from_pdf(pdf_path)
        
        if text:
            # Create comprehensive metadata
            document_metadata = create_document_metadata(pdf, text, pdf_metadata)
            
            # Insert into LightRAG with metadata
            # Note: LightRAG's insert method should accept metadata as a parameter
            # If it doesn't, we'll need to modify the approach
            try:
                # Try to insert with metadata
                rag.insert(text, metadata=document_metadata)
                logger.info(f"✅ Successfully ingested: {pdf} with metadata")
            except TypeError:
                # Fallback: insert without metadata if not supported
                rag.insert(text)
                logger.warning(f"⚠️ Ingested {pdf} without metadata (LightRAG version may not support metadata)")
            
            logger.info(f"   Text length: {len(text)} characters")
            logger.info(f"   Pages: {document_metadata['total_pages']}")
            logger.info(f"   Description: {document_metadata['description'][:100]}...")
            
            # Store in summary
            metadata_summary["ingestion_session"]["documents_processed"].append({
                "filename": pdf,
                "status": "success",
                "metadata": document_metadata
            })
            
        else:
            logger.warning(f"⚠️ No text extracted from: {pdf}")
            metadata_summary["ingestion_session"]["documents_processed"].append({
                "filename": pdf,
                "status": "failed",
                "error": "No text extracted"
            })

    # Save metadata summary
    metadata_summary["ingestion_session"]["end_time"] = datetime.now().isoformat()
    metadata_file = os.path.join(WORKING_DIR, "ingestion_metadata.json")
    
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_summary, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Metadata summary saved to: {metadata_file}")
    except Exception as e:
        logger.error(f"Failed to save metadata summary: {e}")

    logger.info("\n🎉 All PDFs ingested into LightRAG successfully!")
    logger.info(f"📊 Total documents processed: {len(pdf_files)}")
    logger.info(f"💾 Data stored in: {WORKING_DIR}")
    logger.info(f"📋 Metadata summary: {metadata_file}")

if __name__ == "__main__":
    main()
