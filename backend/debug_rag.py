#!/usr/bin/env python3
"""
Debug script to test LightRAG functionality directly
"""

import asyncio
import logging
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_lightrag():
    """Debug LightRAG functionality"""
    print("🔍 Debugging LightRAG functionality...")
    
    # Initialize LightRAG
    working_dir = "rag-pdf"
    print(f"📁 Working directory: {working_dir}")
    
    try:
        rag = LightRAG(
            working_dir=working_dir,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete
        )
        await rag.initialize_storages()
        await initialize_pipeline_status()
        print("✅ LightRAG initialized successfully")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        query = "MSME loan eligibility criteria"
        print(f"Query: {query}")
        
        try:
            results = await rag.retrieve(query, top_k=3)
            print(f"✅ Search successful: {len(results)} results found")
            
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  Content: {result.content[:200]}...")
                print(f"  Score: {result.score}")
                if hasattr(result, 'metadata'):
                    print(f"  Metadata: {result.metadata}")
                else:
                    print(f"  Metadata: None")
                    
        except Exception as e:
            print(f"❌ Search failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test LLM functionality
        print("\n🤖 Testing LLM functionality...")
        try:
            test_prompt = "What is MSME?"
            response = await gpt_4o_mini_complete(test_prompt)
            print(f"✅ LLM test successful: {response[:100]}...")
        except Exception as e:
            print(f"❌ LLM test failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ LightRAG initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_lightrag())
