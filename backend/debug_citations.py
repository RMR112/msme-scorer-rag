#!/usr/bin/env python3
"""
Debug script to test citation system
"""

import asyncio
import logging
from rag_store import search_documents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_citations():
    """Debug the citation system"""
    
    print("🔍 Debugging Citation System")
    print("=" * 50)
    
    # Test query
    query = "What are the eligibility criteria for MSME loans?"
    
    print(f"Query: '{query}'")
    print("-" * 40)
    
    # Test without re-ranking first
    print("📊 Testing WITHOUT re-ranking:")
    try:
        results_no_rerank = await search_documents(query, top_k=3, enable_rerank=False)
        print(f"Results count: {len(results_no_rerank)}")
        
        for i, result in enumerate(results_no_rerank, 1):
            print(f"\nResult {i}:")
            print(f"  Content preview: {result.get('content', '')[:100]}...")
            print(f"  Score: {result.get('score', 0)}")
            print(f"  Metadata keys: {list(result.get('metadata', {}).keys())}")
            
            doc_metadata = result.get('document_metadata', {})
            print(f"  Document metadata keys: {list(doc_metadata.keys())}")
            print(f"  Document name: {doc_metadata.get('document_name', 'NOT FOUND')}")
            print(f"  Document ID: {doc_metadata.get('document_id', 'NOT FOUND')}")
            print(f"  Source file: {doc_metadata.get('source_file', 'NOT FOUND')}")
            
    except Exception as e:
        print(f"❌ Error without re-ranking: {e}")
    
    print("\n" + "=" * 50)
    
    # Test with re-ranking
    print("📊 Testing WITH re-ranking:")
    try:
        results_with_rerank = await search_documents(query, top_k=3, enable_rerank=True)
        print(f"Results count: {len(results_with_rerank)}")
        
        for i, result in enumerate(results_with_rerank, 1):
            print(f"\nResult {i}:")
            print(f"  Content preview: {result.get('content', '')[:100]}...")
            print(f"  Score: {result.get('score', 0)}")
            print(f"  Metadata keys: {list(result.get('metadata', {}).keys())}")
            
            doc_metadata = result.get('document_metadata', {})
            print(f"  Document metadata keys: {list(doc_metadata.keys())}")
            print(f"  Document name: {doc_metadata.get('document_name', 'NOT FOUND')}")
            print(f"  Document ID: {doc_metadata.get('document_id', 'NOT FOUND')}")
            print(f"  Source file: {doc_metadata.get('source_file', 'NOT FOUND')}")
            
    except Exception as e:
        print(f"❌ Error with re-ranking: {e}")

async def debug_rag_store_state():
    """Debug the RAG store internal state"""
    
    print("\n🔧 Debugging RAG Store State")
    print("=" * 50)
    
    from rag_store import rag_store
    
    # Check if initialized
    print(f"RAG Store initialized: {rag_store._initialized}")
    
    if hasattr(rag_store, 'chunk_to_doc_mapping'):
        print(f"Chunk-to-doc mapping count: {len(rag_store.chunk_to_doc_mapping)}")
        if rag_store.chunk_to_doc_mapping:
            sample_chunk = list(rag_store.chunk_to_doc_mapping.keys())[0]
            sample_doc = rag_store.chunk_to_doc_mapping[sample_chunk]
            print(f"Sample mapping: {sample_chunk} -> {sample_doc}")
    
    if hasattr(rag_store, 'doc_id_to_file_path'):
        print(f"Doc ID to file path count: {len(rag_store.doc_id_to_file_path)}")
        if rag_store.doc_id_to_file_path:
            sample_doc_id = list(rag_store.doc_id_to_file_path.keys())[0]
            sample_file_path = rag_store.doc_id_to_file_path[sample_doc_id]
            print(f"Sample file path: {sample_doc_id} -> {sample_file_path}")
    
    if hasattr(rag_store, 'metadata_cache'):
        print(f"Metadata cache count: {len(rag_store.metadata_cache)}")
        if rag_store.metadata_cache:
            sample_doc_id = list(rag_store.metadata_cache.keys())[0]
            sample_metadata = rag_store.metadata_cache[sample_doc_id]
            print(f"Sample metadata keys: {list(sample_metadata.keys())}")

if __name__ == "__main__":
    asyncio.run(debug_citations())
    asyncio.run(debug_rag_store_state())
