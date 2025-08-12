import os
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag import QueryParam

# -------------------------
# 🔧 Logging
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# 📁 Paths
# -------------------------
WORKING_DIR = os.path.join(os.path.dirname(__file__), "rag-pdf")

class RAGStore:
    def __init__(self):
        self.rag = None
        self._initialized = False
        self.metadata_cache = {}
        self._load_metadata_cache()
    
    def _load_metadata_cache(self):
        """Load metadata from ingestion summary if available"""
        metadata_file = os.path.join(WORKING_DIR, "ingestion_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_summary = json.load(f)
                
                # Create a lookup cache for document metadata
                for doc_info in metadata_summary.get("ingestion_session", {}).get("documents_processed", []):
                    if doc_info.get("status") == "success" and "metadata" in doc_info:
                        doc_metadata = doc_info["metadata"]
                        doc_id = doc_metadata.get("document_id", doc_info["filename"])
                        self.metadata_cache[doc_id] = doc_metadata
                
                logger.info(f"📋 Loaded metadata for {len(self.metadata_cache)} documents")
            except Exception as e:
                logger.warning(f"Failed to load metadata cache: {e}")
    
    async def initialize(self):
        """Initialize LightRAG with OpenAI embedding + GPT-4o-mini"""
        if self._initialized:
            return
            
        logger.info("Initializing LightRAG with OpenAI embedding + GPT-4o-mini...")
        self.rag = LightRAG(
            working_dir=WORKING_DIR,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete
        )
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        self._initialized = True
        logger.info("✅ LightRAG initialized successfully")
    
    def _enhance_result_with_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance search result with document metadata"""
        # Try to find matching metadata based on content or other clues
        content = result.get("content", "")
        
        # Look for document identifiers in content
        for doc_id, metadata in self.metadata_cache.items():
            if doc_id.lower() in content.lower() or metadata.get("document_name", "").lower() in content.lower():
                result["document_metadata"] = metadata
                break
        
        # If no specific metadata found, add general context
        if "document_metadata" not in result:
            result["document_metadata"] = {
                "document_type": "MSME_POLICY_DOCUMENT",
                "business_domain": "MSME_LOANS",
                "content_topics": ["loan_eligibility", "application_process", "documentation_requirements"]
            }
        
        return result
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using LightRAG"""
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Searching for query: '{query}' with top_k={top_k}")
            
            # Use LightRAG's aquery method with local mode for search
            query_param = QueryParam(mode="local", top_k=top_k)
            query_result = await self.rag.aquery(query, param=query_param)
            
            logger.info(f"Query result type: {type(query_result)}")
            logger.info(f"Query result: {query_result}")
            
            # Parse the query result to extract relevant content
            formatted_results = []
            
            # Handle different response formats from LightRAG
            if isinstance(query_result, str):
                # If it's a string response, create a single result
                formatted_results.append({
                    "rank": 1,
                    "content": query_result,
                    "score": 1.0,
                    "metadata": {}
                })
            elif isinstance(query_result, dict):
                # If it's a dict, extract relevant fields
                if "answer" in query_result:
                    formatted_results.append({
                        "rank": 1,
                        "content": query_result["answer"],
                        "score": 1.0,
                        "metadata": query_result.get("metadata", {})
                    })
                elif "content" in query_result:
                    formatted_results.append({
                        "rank": 1,
                        "content": query_result["content"],
                        "score": query_result.get("score", 1.0),
                        "metadata": query_result.get("metadata", {})
                    })
            elif isinstance(query_result, list):
                # If it's a list, process each item
                for i, item in enumerate(query_result):
                    if isinstance(item, str):
                        formatted_results.append({
                            "rank": i + 1,
                            "content": item,
                            "score": 1.0 - (i * 0.1),  # Decreasing score
                            "metadata": {}
                        })
                    elif isinstance(item, dict):
                        formatted_results.append({
                            "rank": i + 1,
                            "content": item.get("content", str(item)),
                            "score": item.get("score", 1.0 - (i * 0.1)),
                            "metadata": item.get("metadata", {})
                        })
            
            # Enhance with document metadata
            for result in formatted_results:
                self._enhance_result_with_metadata(result)
            
            logger.info(f"Returning {len(formatted_results)} formatted results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during RAG search: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def generate_answer(self, query: str, context: List[str] = None) -> str:
        """Generate an answer using LightRAG's generation capabilities"""
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Generating answer for query: '{query}'")
            
            if context:
                # Use provided context
                logger.info(f"Using provided context with {len(context)} items")
                combined_context = "\n\n".join(context)
            else:
                # Use LightRAG's aquery method with naive mode for generation
                logger.info("Using LightRAG aquery for answer generation...")
                query_param = QueryParam(mode="naive")
                result = await self.rag.aquery(query, param=query_param)
                
                if isinstance(result, str):
                    return result
                elif isinstance(result, dict) and "answer" in result:
                    return result["answer"]
                else:
                    # Fallback: use the result as is
                    return str(result)
            
        except Exception as e:
            logger.error(f"Error during answer generation: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"Sorry, I encountered an error while generating the answer: {str(e)}"
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get a summary of all ingested documents"""
        if not self.metadata_cache:
            return {"message": "No document metadata available"}
        
        summary = {
            "total_documents": len(self.metadata_cache),
            "documents": []
        }
        
        for doc_id, metadata in self.metadata_cache.items():
            doc_summary = {
                "document_id": doc_id,
                "document_name": metadata.get("document_name", "Unknown"),
                "document_type": metadata.get("document_type", "Unknown"),
                "total_pages": metadata.get("total_pages", 0),
                "total_characters": metadata.get("total_characters", 0),
                "description": metadata.get("description", "")[:200] + "..." if len(metadata.get("description", "")) > 200 else metadata.get("description", ""),
                "ingestion_date": metadata.get("ingestion_date", "Unknown"),
                "content_topics": metadata.get("content_topics", [])
            }
            summary["documents"].append(doc_summary)
        
        return summary

# Global RAG store instance
rag_store = RAGStore()

async def retrieve_recommendations(query: str, top_k: int = 3) -> List[str]:
    """Retrieve recommendations based on the query"""
    try:
        results = await rag_store.search(query, top_k=top_k)
        recommendations = []
        
        for result in results:
            # Extract key insights from the content
            content = result["content"]
            
            # Add document context if available
            doc_metadata = result.get("document_metadata", {})
            if doc_metadata:
                doc_name = doc_metadata.get("document_name", "Document")
                content = f"[From {doc_name}] {content}"
            
            # Truncate if too long
            if len(content) > 200:
                content = content[:200] + "..."
            recommendations.append(content)
        
        return recommendations if recommendations else ["No specific recommendations found based on your query."]
        
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        return ["Unable to retrieve recommendations at this time."]

async def search_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search documents and return detailed results with metadata"""
    return await rag_store.search(query, top_k=top_k)

async def generate_answer(query: str) -> str:
    """Generate a comprehensive answer to the query"""
    return await rag_store.generate_answer(query)

def get_document_summary() -> Dict[str, Any]:
    """Get a summary of all ingested documents"""
    return rag_store.get_document_summary()