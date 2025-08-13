#!/usr/bin/env python3
"""
Test script to verify re-ranking function handles edge cases
"""

import asyncio
import logging
from rerank_func import simple_rerank_func

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_edge_cases():
    """Test re-ranking function with edge cases"""
    
    print("🧪 Testing Re-ranking Edge Cases")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Empty documents list",
            "query": "MSME loans",
            "documents": [],
            "expected": "Empty result list"
        },
        {
            "name": "Non-string documents",
            "query": "MSME loans",
            "documents": [123, None, {"key": "value"}, "Valid string"],
            "expected": "Should filter out non-strings"
        },
        {
            "name": "Empty string documents",
            "query": "MSME loans",
            "documents": ["", "   ", "Valid content", ""],
            "expected": "Should filter out empty strings"
        },
        {
            "name": "Invalid query",
            "query": "",
            "documents": ["Valid document content"],
            "expected": "Should return empty list"
        },
        {
            "name": "None query",
            "query": None,
            "documents": ["Valid document content"],
            "expected": "Should return empty list"
        },
        {
            "name": "Mixed content types",
            "query": "MSME loans",
            "documents": [
                "MSME loans require Udyam registration",
                123,
                None,
                "   ",
                "Business must have proper documentation",
                {"invalid": "content"},
                "Loan amount depends on business category"
            ],
            "expected": "Should process only valid strings"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            results = await simple_rerank_func(
                test_case['query'], 
                test_case['documents'], 
                top_n=5
            )
            
            print(f"   ✅ Results: {len(results)} items")
            if results:
                for j, result in enumerate(results[:3], 1):
                    content_preview = result['content'][:50] + "..." if len(result['content']) > 50 else result['content']
                    print(f"     {j}. Score: {result['score']:.3f} | Content: {content_preview}")
            else:
                print("     No results returned")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("-" * 40)

async def test_valid_case():
    """Test with valid data to ensure it still works"""
    
    print("\n✅ Testing Valid Case")
    print("=" * 50)
    
    query = "MSME loan eligibility"
    documents = [
        "MSME loans require businesses to have Udyam registration and meet certain turnover criteria.",
        "The business must be in operation for at least 2 years and have a good credit history.",
        "Eligibility for MSME loans includes having proper business documentation and financial statements."
    ]
    
    try:
        results = await simple_rerank_func(query, documents, top_n=3)
        print(f"✅ Valid case successful: {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['score']:.3f} | Content: {result['content'][:60]}...")
    except Exception as e:
        print(f"❌ Valid case failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_edge_cases())
    asyncio.run(test_valid_case())
