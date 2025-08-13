#!/usr/bin/env python3
"""
Simple Re-ranking Function for LightRAG
Follows LightRAG's rerank_model_func pattern
"""

import asyncio
import logging
from typing import List, Dict, Any
import numpy as np
from lightrag.llm.openai import openai_embed

logger = logging.getLogger(__name__)

async def simple_rerank_func(
    query: str, 
    documents: List[str], 
    top_n: int = None, 
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Simple re-ranking function using semantic similarity
    
    Args:
        query: The search query
        documents: List of document contents to re-rank
        top_n: Number of top results to return
        **kwargs: Additional arguments
        
    Returns:
        List of re-ranked documents with scores
    """
    if not documents:
        return []
    
    # Validate query
    if not isinstance(query, str) or not query.strip():
        logger.error("Invalid query: must be a non-empty string")
        return []
    
    query = query.strip()
    
    try:
        logger.info(f"Re-ranking {len(documents)} documents for query: '{query}'")
        
        # Filter out non-string documents and ensure they're strings
        valid_documents = []
        for doc in documents:
            if isinstance(doc, str) and doc.strip():
                valid_documents.append(doc.strip())
            else:
                logger.warning(f"Skipping non-string or empty document: {type(doc)}")
        
        if not valid_documents:
            logger.warning("No valid documents to re-rank")
            return []
        
        # Get embeddings for query and documents
        try:
            query_embedding = await openai_embed([query])
            query_vector = query_embedding[0] if isinstance(query_embedding, list) else query_embedding
        except Exception as e:
            logger.error(f"Error getting query embedding: {e}")
            return []
        
        try:
            doc_embeddings = await openai_embed(valid_documents)
        except Exception as e:
            logger.error(f"Error getting document embeddings: {e}")
            return []
        
        # Calculate similarity scores
        results = []
        for i, doc in enumerate(valid_documents):
            doc_vector = doc_embeddings[i] if isinstance(doc_embeddings, list) else doc_embeddings[i]
            
            # Calculate cosine similarity
            similarity = cosine_similarity(query_vector, doc_vector)
            
            results.append({
                "content": doc,
                "score": float(similarity),
                "rank": i + 1
            })
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Update ranks
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        # Return top_n results if specified
        if top_n is not None:
            results = results[:top_n]
        
        logger.info(f"Re-ranking completed. Top result score: {float(results[0]['score']):.3f}")
        return results
        
    except Exception as e:
        logger.error(f"Error during re-ranking: {e}")
        # Return original documents with default scores if re-ranking fails
        return [
            {
                "content": doc,
                "score": 1.0 - (i * 0.1),
                "rank": i + 1
            }
            for i, doc in enumerate(documents[:top_n] if top_n else documents)
        ]

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = float(dot_product / (norm1 * norm2))
        return similarity
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0
