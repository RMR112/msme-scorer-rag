#!/usr/bin/env python3
"""
Test script to demonstrate LightRAG's built-in re-ranking functionality
"""

import asyncio
import logging
from rag_store import search_documents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_lightrag_reranking():
    """Test LightRAG's built-in re-ranking functionality"""
    
    print("🔄 Testing LightRAG Built-in Re-ranking")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What are the eligibility criteria for MSME loans?",
        "How to apply for Udyam registration?",
        "What documents are required for loan application?",
        "What are the interest rates for MSME loans?",
        "How does the loan approval process work?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing Query: '{query}'")
        print("-" * 40)
        
        # Test without re-ranking
        print("📊 Results WITHOUT re-ranking:")
        try:
            results_no_rerank = await search_documents(query, top_k=3, enable_rerank=False)
            for i, result in enumerate(results_no_rerank, 1):
                print(f"  {i}. Score: {result.get('score', 0):.3f} | Content: {result.get('content', '')[:100]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Test with re-ranking
        print("\n📊 Results WITH re-ranking:")
        try:
            results_with_rerank = await search_documents(query, top_k=3, enable_rerank=True)
            for i, result in enumerate(results_with_rerank, 1):
                print(f"  {i}. Score: {result.get('score', 0):.3f} | Content: {result.get('content', '')[:100]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print("\n" + "=" * 50)

async def test_rerank_function_directly():
    """Test the re-ranking function directly"""
    
    print("\n🧪 Testing Re-ranking Function Directly")
    print("=" * 50)
    
    from rerank_func import simple_rerank_func
    
    # Sample query and documents
    query = "MSME loan eligibility criteria"
    documents = [
        "MSME loans require businesses to have Udyam registration and meet certain turnover criteria. The business must be in operation for at least 2 years and have a good credit history.",
        "The weather today is sunny with clear skies. Temperature is around 25 degrees Celsius.",
        "Eligibility for MSME loans includes having proper business documentation, financial statements, and a viable business plan. The loan amount depends on the business category."
    ]
    
    print(f"Query: '{query}'")
    print(f"Documents: {len(documents)}")
    
    try:
        reranked_results = await simple_rerank_func(query, documents, top_n=3)
        print("\n📊 Re-ranked Results:")
        for i, result in enumerate(reranked_results, 1):
            print(f"  {i}. Score: {result.get('score', 0):.3f} | Content: {result.get('content', '')[:80]}...")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_lightrag_reranking())
    asyncio.run(test_rerank_function_directly())
