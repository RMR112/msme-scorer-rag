#!/usr/bin/env python3
"""
Test script to check API response structure for citations
"""

import asyncio
import json
import logging
from rag_store import search_documents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_api_response():
    """Test the API response structure"""
    
    print("🔍 Testing API Response Structure")
    print("=" * 50)
    
    # Test query
    query = "What are the eligibility criteria for MSME loans?"
    
    print(f"Query: '{query}'")
    print("-" * 40)
    
    try:
        # Test search response
        results = await search_documents(query, top_k=3, enable_rerank=False)
        
        print(f"Results count: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Content preview: {result.get('content', '')[:100]}...")
            print(f"  Score: {result.get('score', 0)}")
            print(f"  Rank: {result.get('rank', 0)}")
            
            # Check metadata
            metadata = result.get('metadata', {})
            print(f"  Metadata keys: {list(metadata.keys())}")
            print(f"  Metadata content: {json.dumps(metadata, indent=2)}")
            
            # Check document_metadata
            doc_metadata = result.get('document_metadata', {})
            print(f"  Document metadata keys: {list(doc_metadata.keys())}")
            print(f"  Document metadata content: {json.dumps(doc_metadata, indent=2)}")
            
            # Check specific fields
            print(f"  Document name: {doc_metadata.get('document_name', 'NOT FOUND')}")
            print(f"  Document ID: {doc_metadata.get('document_id', 'NOT FOUND')}")
            print(f"  Source file: {doc_metadata.get('source_file', 'NOT FOUND')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_response())
