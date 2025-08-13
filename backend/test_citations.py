#!/usr/bin/env python3
"""
Test script to verify citation system with updated file paths
"""

import asyncio
import json
import os
from rag_store import rag_store

async def test_citation_system():
    """Test the citation system with updated file paths"""
    
    print("🔍 Testing Citation System with Updated File Paths")
    print("=" * 60)
    
    # Initialize RAG store
    await rag_store.initialize()
    
    print(f"📋 Loaded metadata for {len(rag_store.metadata_cache)} documents")
    print(f"📋 Loaded chunk-to-document mapping for {len(rag_store.chunk_to_doc_mapping)} chunks")
    print(f"📋 Loaded file paths for {len(rag_store.doc_id_to_file_path)} documents")
    
    print("\n📄 Document File Paths from KV Store:")
    for doc_id, file_path in rag_store.doc_id_to_file_path.items():
        print(f"  {doc_id} -> {file_path}")
    
    print("\n🔍 Testing Search with Citations...")
    
    # Test search
    test_query = "What are the eligibility criteria for MSME loans?"
    results = await rag_store.search(test_query, top_k=3)
    
    print(f"\n✅ Search Results for: '{test_query}'")
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results, 1):
        doc_metadata = result.get("document_metadata", {})
        doc_name = doc_metadata.get("document_name", "Unknown")
        score = result.get("score", 0)
        content_preview = result.get("content", "")[:100] + "..."
        
        print(f"\n📄 Result {i}:")
        print(f"  Document: {doc_name}")
        print(f"  Score: {score:.3f}")
        print(f"  Content: {content_preview}")
    
    print("\n✅ Citation system test completed!")

if __name__ == "__main__":
    asyncio.run(test_citation_system())
