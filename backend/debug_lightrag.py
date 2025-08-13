#!/usr/bin/env python3
"""
Debug script to explore LightRAG's available methods
"""

import asyncio
import os
from rag_store import rag_store

async def debug_lightrag():
    """Debug LightRAG to understand available methods"""
    
    print("🔍 Debugging LightRAG Methods")
    print("=" * 50)
    
    # Initialize RAG store
    await rag_store.initialize()
    
    print(f"RAG object type: {type(rag_store.rag)}")
    print(f"RAG object: {rag_store.rag}")
    
    # Check available attributes
    print("\n📋 Available attributes:")
    for attr in dir(rag_store.rag):
        if not attr.startswith('_'):
            print(f"  {attr}")
    
    # Check if retriever exists
    if hasattr(rag_store.rag, 'retriever'):
        print(f"\n🔍 Retriever found: {rag_store.rag.retriever}")
        print(f"Retriever type: {type(rag_store.rag.retriever)}")
        
        # Check retriever methods
        print("\n📋 Retriever methods:")
        for attr in dir(rag_store.rag.retriever):
            if not attr.startswith('_'):
                print(f"  {attr}")
    else:
        print("\n❌ No retriever found")
    
    # Check if vector store exists
    if hasattr(rag_store.rag, 'vector_store'):
        print(f"\n🔍 Vector store found: {rag_store.rag.vector_store}")
        print(f"Vector store type: {type(rag_store.rag.vector_store)}")
        
        # Check vector store methods
        print("\n📋 Vector store methods:")
        for attr in dir(rag_store.rag.vector_store):
            if not attr.startswith('_'):
                print(f"  {attr}")
    else:
        print("\n❌ No vector store found")
    
    # Check if knowledge graph exists
    if hasattr(rag_store.rag, 'kg'):
        print(f"\n🔍 Knowledge graph found: {rag_store.rag.kg}")
        print(f"Knowledge graph type: {type(rag_store.rag.kg)}")
        
        # Check KG methods
        print("\n📋 Knowledge graph methods:")
        for attr in dir(rag_store.rag.kg):
            if not attr.startswith('_'):
                print(f"  {attr}")
    else:
        print("\n❌ No knowledge graph found")
    
    # Try a simple search to see what we get
    print("\n🔍 Testing simple search...")
    try:
        from lightrag import QueryParam
        query_param = QueryParam(mode="local", top_k=3)
        result = await rag_store.rag.aquery("MSME loan eligibility", param=query_param)
        print(f"Search result type: {type(result)}")
        print(f"Search result: {result}")
        
        if isinstance(result, list) and len(result) > 0:
            print(f"First item type: {type(result[0])}")
            print(f"First item: {result[0]}")
    except Exception as e:
        print(f"Search failed: {e}")
    
    # Test chunks_vdb access
    print("\n🔍 Testing chunks_vdb access...")
    try:
        if hasattr(rag_store.rag, 'chunks_vdb'):
            print(f"chunks_vdb type: {type(rag_store.rag.chunks_vdb)}")
            print(f"chunks_vdb methods: {[attr for attr in dir(rag_store.rag.chunks_vdb) if not attr.startswith('_')]}")
            
            # Try to get some sample data
            if hasattr(rag_store.rag.chunks_vdb, 'data'):
                print(f"chunks_vdb data length: {len(rag_store.rag.chunks_vdb.data)}")
                if len(rag_store.rag.chunks_vdb.data) > 0:
                    print(f"Sample chunk: {rag_store.rag.chunks_vdb.data[0]}")
        else:
            print("❌ chunks_vdb not found")
    except Exception as e:
        print(f"chunks_vdb test failed: {e}")
    
    # Test text_chunks access
    print("\n🔍 Testing text_chunks access...")
    try:
        if hasattr(rag_store.rag, 'text_chunks'):
            print(f"text_chunks type: {type(rag_store.rag.text_chunks)}")
            print(f"text_chunks length: {len(rag_store.rag.text_chunks) if rag_store.rag.text_chunks else 0}")
            
            if rag_store.rag.text_chunks and len(rag_store.rag.text_chunks) > 0:
                # Get first chunk
                first_chunk_id = list(rag_store.rag.text_chunks.keys())[0]
                first_chunk_content = rag_store.rag.text_chunks[first_chunk_id]
                print(f"First chunk ID: {first_chunk_id}")
                print(f"First chunk content preview: {first_chunk_content[:200]}...")
        else:
            print("❌ text_chunks not found")
    except Exception as e:
        print(f"text_chunks test failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_lightrag())
