import os
import asyncio
import logging
import json
from typing import List, Dict, Any, Optional
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag import QueryParam
from rerank_func import simple_rerank_func

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
        kv_store_file = os.path.join(WORKING_DIR, "kv_store_doc_status.json")
        
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
        
        # Load KV store document status for chunk-to-document mapping and file paths
        self.chunk_to_doc_mapping = {}
        self.doc_id_to_file_path = {}
        if os.path.exists(kv_store_file):
            try:
                with open(kv_store_file, 'r', encoding='utf-8') as f:
                    kv_store_data = json.load(f)
                
                # Create mapping from chunks to document IDs
                for doc_id, doc_info in kv_store_data.items():
                    if "chunks_list" in doc_info:
                        for chunk_id in doc_info["chunks_list"]:
                            self.chunk_to_doc_mapping[chunk_id] = doc_id
                    
                    # Store the file_path for each document ID
                    file_path = doc_info.get("file_path", "unknown_source")
                    if file_path != "unknown_source":
                        self.doc_id_to_file_path[doc_id] = file_path
                
                logger.info(f"📋 Loaded chunk-to-document mapping for {len(self.chunk_to_doc_mapping)} chunks")
                logger.info(f"📋 Loaded file paths for {len(self.doc_id_to_file_path)} documents")
            except Exception as e:
                logger.warning(f"Failed to load KV store mapping: {e}")
    
    async def initialize(self):
        """Initialize LightRAG with OpenAI embedding + GPT-4o-mini"""
        if self._initialized:
            return
            
        logger.info("Initializing LightRAG with OpenAI embedding + GPT-4o-mini...")
        self.rag = LightRAG(
            working_dir=WORKING_DIR,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
            rerank_model_func=simple_rerank_func
        )
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        self._initialized = True
        logger.info("✅ LightRAG initialized successfully")
    
    def _enhance_result_with_metadata(self, result: Dict[str, Any], result_index: int = 0) -> Dict[str, Any]:
        """Enhance search result with document metadata"""
        content = result.get("content", "")
        
        # First, try to find document metadata using chunk-to-document mapping
        # Look for chunk IDs in the content or metadata
        chunk_id = None
        if hasattr(self, 'chunk_to_doc_mapping'):
            # Try to extract chunk ID from content or result metadata
            for chunk_id_key in self.chunk_to_doc_mapping.keys():
                if chunk_id_key in str(result) or chunk_id_key in content:
                    chunk_id = chunk_id_key
                    break
        
        if chunk_id and chunk_id in self.chunk_to_doc_mapping:
            doc_id = self.chunk_to_doc_mapping[chunk_id]
            
            # First, try to get the file path from KV store
            if hasattr(self, 'doc_id_to_file_path') and doc_id in self.doc_id_to_file_path:
                file_path = self.doc_id_to_file_path[doc_id]
                # Create metadata using the file path from KV store
                result["document_metadata"] = {
                    "document_name": file_path,
                    "document_id": doc_id,
                    "document_type": "MSME_POLICY_DOCUMENT",
                    "business_domain": "MSME_LOANS",
                    "source_file": file_path
                }
                logger.info(f"Found document metadata for chunk {chunk_id}: {file_path}")
                return result
            
            # Fallback: Find the corresponding metadata from ingestion cache
            for metadata in self.metadata_cache.values():
                if metadata.get("document_id") == doc_id:
                    result["document_metadata"] = metadata
                    logger.info(f"Found document metadata for chunk {chunk_id}: {metadata.get('document_name')}")
                    return result
        
        # Fallback: Try to find the best matching document based on content similarity
        best_match = None
        best_score = 0
        
        for doc_id, metadata in self.metadata_cache.items():
            # Check if any part of the document name appears in the content
            doc_name = metadata.get("document_name", "").lower()
            doc_id_lower = doc_id.lower()
            
            # Simple scoring based on content matching
            score = 0
            if doc_name in content.lower():
                score += 10
            if doc_id_lower in content.lower():
                score += 5
            
            # Check for common MSME terms that might indicate document relevance
            msme_terms = ["msme", "sme", "loan", "policy", "guidelines", "eligibility"]
            for term in msme_terms:
                if term in content.lower() and term in doc_name:
                    score += 2
            
            if score > best_score:
                best_score = score
                best_match = metadata
        
        # Use the best match if found, otherwise use a default
        if best_match and best_score > 0:
            result["document_metadata"] = best_match
        else:
            # Try to assign based on content keywords
            if any(term in content.lower() for term in ["loan", "eligibility", "policy"]):
                # Find the first policy document
                for metadata in self.metadata_cache.values():
                    if "policy" in metadata.get("document_type", "").lower():
                        result["document_metadata"] = metadata
                        break
                else:
                    # Fallback to first available document
                    if self.metadata_cache:
                        first_doc = next(iter(self.metadata_cache.values()))
                        result["document_metadata"] = first_doc
                    else:
                        result["document_metadata"] = {
                            "document_name": "MSME Policy Document",
                            "document_type": "MSME_POLICY_DOCUMENT",
                            "business_domain": "MSME_LOANS",
                            "content_topics": ["loan_eligibility", "application_process", "documentation_requirements"]
                        }
        
        return result
    
    async def search(self, query: str, top_k: int = 5, enable_rerank: bool = True) -> List[Dict[str, Any]]:
        """Search for relevant documents using LightRAG with optional re-ranking"""
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Searching for query: '{query}' with top_k={top_k}, rerank={enable_rerank}")
            
            # Use LightRAG's aquery method with re-ranking
            query_param = QueryParam(mode="hybrid", top_k=top_k, enable_rerank=enable_rerank)
            query_result = await self.rag.aquery(query, param=query_param)
            
            logger.info(f"Query result type: {type(query_result)}")
            
            # Parse the query result to extract relevant content
            formatted_results = []
            
            # Handle different response formats from LightRAG
            if isinstance(query_result, str):
                # If it's a string response, create a single result
                if not query_result.startswith("I'm sorry") and not query_result.startswith("I apologize"):
                    formatted_results.append({
                        "rank": 1,
                        "content": query_result,
                        "score": 1.0,
                        "metadata": {}
                    })
            elif isinstance(query_result, dict):
                # If it's a dict, extract relevant fields
                if "answer" in query_result:
                    answer = query_result["answer"]
                    if not answer.startswith("I'm sorry") and not answer.startswith("I apologize"):
                        formatted_results.append({
                            "rank": 1,
                            "content": answer,
                            "score": 1.0,
                            "metadata": query_result.get("metadata", {})
                        })
                elif "content" in query_result:
                    content = query_result["content"]
                    if not content.startswith("I'm sorry") and not content.startswith("I apologize"):
                        formatted_results.append({
                            "rank": 1,
                            "content": content,
                            "score": query_result.get("score", 1.0),
                            "metadata": query_result.get("metadata", {})
                        })
            elif isinstance(query_result, list):
                # If it's a list, process each item
                for i, item in enumerate(query_result):
                    if isinstance(item, str):
                        if not item.startswith("I'm sorry") and not item.startswith("I apologize"):
                            formatted_results.append({
                                "rank": i + 1,
                                "content": item,
                                "score": 1.0 - (i * 0.1),  # Decreasing score
                                "metadata": {}
                            })
                    elif isinstance(item, dict):
                        content = item.get("content", str(item))
                        if not content.startswith("I'm sorry") and not content.startswith("I apologize"):
                            formatted_results.append({
                                "rank": i + 1,
                                "content": content,
                                "score": item.get("score", 1.0 - (i * 0.1)),
                                "metadata": item.get("metadata", {})
                            })
            
            # Enhance with document metadata
            for i, result in enumerate(formatted_results):
                # Try to extract chunk information from the result
                chunk_id = result.get("chunk_id")  # From retriever
                
                # If no chunk_id from retriever, try from original query_result
                if not chunk_id and isinstance(query_result, list) and i < len(query_result):
                    original_item = query_result[i]
                    if isinstance(original_item, dict):
                        chunk_id = original_item.get("chunk_id") or original_item.get("id")
                
                if chunk_id and hasattr(self, 'chunk_to_doc_mapping') and chunk_id in self.chunk_to_doc_mapping:
                    doc_id = self.chunk_to_doc_mapping[chunk_id]
                    
                    # First, try to get the file path from KV store
                    if hasattr(self, 'doc_id_to_file_path') and doc_id in self.doc_id_to_file_path:
                        file_path = self.doc_id_to_file_path[doc_id]
                        result["document_metadata"] = {
                            "document_name": file_path,
                            "document_id": doc_id,
                            "document_type": "MSME_POLICY_DOCUMENT",
                            "business_domain": "MSME_LOANS",
                            "source_file": file_path
                        }
                        logger.info(f"Direct chunk mapping for result {i + 1}: {file_path}")
                        continue
                    
                    # Fallback: Find the corresponding metadata from ingestion cache
                    for metadata in self.metadata_cache.values():
                        if metadata.get("document_id") == doc_id:
                            result["document_metadata"] = metadata
                            logger.info(f"Direct chunk mapping for result {i + 1}: {metadata.get('document_name')}")
                            break
                
                # If no direct mapping found, use the enhanced metadata method
                if not result.get("document_metadata"):
                    self._enhance_result_with_metadata(result, i)
                
                # Ensure we have at least basic document metadata
                if not result.get("document_metadata", {}).get("document_name"):
                    # Try to assign using file paths from KV store first
                    if hasattr(self, 'doc_id_to_file_path') and self.doc_id_to_file_path:
                        doc_ids = list(self.doc_id_to_file_path.keys())
                        doc_index = i % len(doc_ids)
                        doc_id = doc_ids[doc_index]
                        file_path = self.doc_id_to_file_path[doc_id]
                        result["document_metadata"] = {
                            "document_name": file_path,
                            "document_id": doc_id,
                            "document_type": "MSME_POLICY_DOCUMENT",
                            "business_domain": "MSME_LOANS",
                            "source_file": file_path
                        }
                        logger.info(f"Assigned document {doc_index + 1} to result {i + 1}: {file_path}")
                    # Fallback to metadata cache
                    elif self.metadata_cache:
                        doc_list = list(self.metadata_cache.values())
                        doc_index = i % len(doc_list)
                        result["document_metadata"] = doc_list[doc_index]
                        logger.info(f"Assigned document {doc_index + 1} to result {i + 1}: {doc_list[doc_index].get('document_name')}")
                    else:
                        result["document_metadata"] = {
                            "document_name": "MSME Policy Document",
                            "document_type": "MSME_POLICY_DOCUMENT",
                            "business_domain": "MSME_LOANS"
                        }
                        logger.info(f"Assigned default document to result {i + 1}")
                
                # Log the final document metadata for debugging
                doc_name = result.get("document_metadata", {}).get("document_name", "Unknown")
                logger.info(f"Result {i + 1} assigned to document: {doc_name}")
            
            # If no results found, provide some sample content from the documents
            if not formatted_results and self.metadata_cache:
                logger.warning("No search results found, providing sample content")
                doc_list = list(self.metadata_cache.values())
                for i, doc_metadata in enumerate(doc_list[:top_k]):
                    sample_content = doc_metadata.get("content_summary", "")[:300] + "..."
                    if sample_content and not sample_content.startswith("I'm sorry"):
                        formatted_results.append({
                            "rank": i + 1,
                            "content": sample_content,
                            "score": 0.8 - (i * 0.1),
                            "metadata": {},
                            "document_metadata": doc_metadata
                        })
            
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
                query_param = QueryParam(mode="hybrid")
                result = await self.rag.aquery(query, param=query_param)
                
                if isinstance(result, str):
                    # Clean up the response to remove unknown_source references
                    cleaned_result = self._clean_generation_response(result)
                    return cleaned_result
                elif isinstance(result, dict) and "answer" in result:
                    # Clean up the response to remove unknown_source references
                    cleaned_answer = self._clean_generation_response(result["answer"])
                    return cleaned_answer
                else:
                    # Fallback: use the result as is, but clean it
                    cleaned_result = self._clean_generation_response(str(result))
                    return cleaned_result
            
        except Exception as e:
            logger.error(f"Error during answer generation: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"Sorry, I encountered an error while generating the answer: {str(e)}"
    
    def _clean_generation_response(self, response: str) -> str:
        """Clean up generation response to remove unknown_source references"""
        if not response:
            return response
        
        # Remove the References section with unknown_source
        lines = response.split('\n')
        cleaned_lines = []
        skip_references = False
        
        for line in lines:
            # Check if we're entering a References section
            if line.strip().lower().startswith('### references') or line.strip().lower().startswith('references'):
                skip_references = True
                continue
            
            # If we're in references section, check if it contains unknown_source
            if skip_references:
                if 'unknown_source' in line.lower():
                    continue
                elif line.strip() == '' or line.strip().startswith('#'):
                    # End of references section
                    skip_references = False
                    if line.strip() != '':
                        cleaned_lines.append(line)
                else:
                    # This might be a valid reference, keep it
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        # Join the lines back together
        cleaned_response = '\n'.join(cleaned_lines).strip()
        
        # Also remove any remaining unknown_source patterns
        import re
        cleaned_response = re.sub(r'\n\s*\[[^\]]*\]\s*unknown_source\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n\s*###\s*References?\s*\n.*unknown_source.*', '', cleaned_response, flags=re.IGNORECASE | re.DOTALL)
        
        return cleaned_response
    
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

async def retrieve_recommendations(query: str, top_k: int = 3, udyam_registration: bool = True) -> List[str]:
    """Retrieve recommendations based on the query using the new AI prompt format"""
    try:
        # Check if Udyam registration is mandatory
        if not udyam_registration:
            return ["""Recommendation:
Loan approval is not possible as Udyam registration is mandatory for MSME loans.

User should:

Obtain Udyam registration certificate from the official portal

Complete the registration process with required business documents

Wait for registration approval and certificate generation

Reapply for loan after obtaining Udyam registration"""]
        
        # Create the new AI prompt for cases with Udyam registration
        ai_prompt = f"""You are an expert MSME loan advisor.
Based on the provided business plan text, give a concise and clear recommendation in the following format only:

Recommendation:
[One-sentence overall assessment of loan approval and MSME category]

User should:

[Action 1]

[Action 2]

[Action 3]

[Action 4]

Do not provide any explanations, analysis, or additional commentary. Only output the recommendation in the exact bullet format shown above.

Business Plan Text:
{query}"""

        # Use LightRAG to generate the recommendation
        if not rag_store._initialized:
            await rag_store.initialize()
        
        # Use the generate_answer method with the new prompt
        recommendation = await rag_store.generate_answer(ai_prompt)
        
        # Return as a single recommendation in the expected format
        return [recommendation] if recommendation else ["Unable to generate recommendation at this time."]
        
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        return ["Unable to retrieve recommendations at this time."]

async def search_documents(query: str, top_k: int = 5, enable_rerank: bool = True) -> List[Dict[str, Any]]:
    """Search documents and return detailed results with metadata"""
    return await rag_store.search(query, top_k=top_k, enable_rerank=enable_rerank)

async def generate_answer(query: str) -> str:
    """Generate a comprehensive answer to the query"""
    return await rag_store.generate_answer(query)

def get_document_summary() -> Dict[str, Any]:
    """Get a summary of all ingested documents"""
    return rag_store.get_document_summary()