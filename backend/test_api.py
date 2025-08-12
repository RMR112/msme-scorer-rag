#!/usr/bin/env python3
"""
Test script for the MSME Loan Scorer with LightRAG API
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

async def test_health(session: aiohttp.ClientSession) -> bool:
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        async with session.get(f"{BASE_URL}/api/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_info(session: aiohttp.ClientSession) -> bool:
    """Test info endpoint"""
    print("\n🔍 Testing info endpoint...")
    try:
        async with session.get(f"{BASE_URL}/api/info") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Info endpoint: {data['name']}")
                print(f"   Version: {data['version']}")
                print(f"   Features: {', '.join(data['features'])}")
                return True
            else:
                print(f"❌ Info endpoint failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Info endpoint error: {e}")
        return False

async def test_documents(session: aiohttp.ClientSession) -> bool:
    """Test documents endpoint"""
    print("\n🔍 Testing documents endpoint...")
    try:
        async with session.get(f"{BASE_URL}/api/documents") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Documents endpoint: {data.get('total_documents', 0)} documents")
                if 'documents' in data and data['documents']:
                    for doc in data['documents'][:2]:  # Show first 2 documents
                        print(f"   📄 {doc.get('document_name', 'Unknown')} ({doc.get('total_pages', 0)} pages)")
                return True
            else:
                print(f"❌ Documents endpoint failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Documents endpoint error: {e}")
        return False

async def test_search(session: aiohttp.ClientSession) -> bool:
    """Test search endpoint"""
    print("\n🔍 Testing search endpoint...")
    search_data = {
        "query": "MSME loan eligibility criteria",
        "top_k": 3
    }
    
    try:
        async with session.post(
            f"{BASE_URL}/api/search",
            json=search_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Search successful: {data['total_results']} results found")
                if data['results']:
                    print(f"   Top result: {data['results'][0]['content'][:100]}...")
                return True
            else:
                print(f"❌ Search failed: {response.status}")
                error_text = await response.text()
                print(f"   Error: {error_text}")
                return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

async def test_generate(session: aiohttp.ClientSession) -> bool:
    """Test generate endpoint"""
    print("\n🔍 Testing generate endpoint...")
    generate_data = {
        "query": "What are the key requirements for MSME loan approval?"
    }
    
    try:
        async with session.post(
            f"{BASE_URL}/api/generate",
            json=generate_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Generation successful")
                print(f"   Answer: {data['answer'][:200]}...")
                return True
            else:
                print(f"❌ Generation failed: {response.status}")
                error_text = await response.text()
                print(f"   Error: {error_text}")
                return False
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

async def test_assess(session: aiohttp.ClientSession) -> bool:
    """Test assess endpoint"""
    print("\n🔍 Testing assess endpoint...")
    assess_data = {
        "businessName": "Tech Solutions Ltd",
        "industryType": "Technology",
        "annualTurnover": 5000000,
        "netProfit": 750000,
        "loanAmount": 2000000,
        "udyamRegistration": True,
        "businessPlan": "Our business plan focuses on developing innovative software solutions for small and medium enterprises. We aim to digitize traditional business processes and provide cost-effective technology solutions."
    }
    
    try:
        async with session.post(
            f"{BASE_URL}/api/assess",
            json=assess_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Assessment successful")
                print(f"   Score: {data['score']}")
                print(f"   Risk Level: {data['risk_level']}")
                print(f"   Recommendations: {len(data['recommendations'])} items")
                return True
            else:
                print(f"❌ Assessment failed: {response.status}")
                error_text = await response.text()
                print(f"   Error: {error_text}")
                return False
    except Exception as e:
        print(f"❌ Assessment error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print(f"📡 Testing against: {BASE_URL}")
    
    async with aiohttp.ClientSession() as session:
        tests = [
            test_health,
            test_info,
            test_documents,
            test_search,
            test_generate,
            test_assess
        ]
        
        results = []
        for test in tests:
            try:
                result = await test(session)
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append(False)
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Your LightRAG API is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
