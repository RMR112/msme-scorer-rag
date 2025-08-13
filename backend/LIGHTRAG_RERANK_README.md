# LightRAG Built-in Re-ranking Implementation

## Overview

This implementation uses LightRAG's built-in re-ranking functionality as documented in their official documentation. It's much simpler and more efficient than custom re-ranking implementations.

## Features

### 🔄 LightRAG Native Re-ranking
- **Built-in Integration**: Uses LightRAG's `rerank_model_func` parameter
- **QueryParam Control**: Enable/disable re-ranking per query using `QueryParam(enable_rerank=True/False)`
- **Semantic Similarity**: Uses cosine similarity between query and document embeddings
- **Automatic Fallback**: Returns original results if re-ranking fails

## Implementation Details

### Files
- `backend/rerank_func.py` - Simple re-ranking function following LightRAG's pattern
- `backend/rag_store.py` - Updated to use LightRAG's built-in re-ranking
- `backend/main.py` - API endpoint with `enable_rerank` parameter
- `backend/test_lightrag_rerank.py` - Test script for demonstration

### Dependencies
- **numpy** - Vector operations and cosine similarity
- **openai** - Embedding generation (already included)
- **lightrag** - Base RAG functionality with re-ranking support

## API Usage

### Search with Re-ranking (Default)
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MSME loan eligibility criteria",
    "top_k": 5,
    "enable_rerank": true
  }'
```

### Search without Re-ranking
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MSME loan eligibility criteria",
    "top_k": 5,
    "enable_rerank": false
  }'
```

## LightRAG Configuration

The re-ranking is configured in the LightRAG initialization:

```python
self.rag = LightRAG(
    working_dir=WORKING_DIR,
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
    rerank_model_func=simple_rerank_func  # Our custom re-ranking function
)
```

## Re-ranking Function

The `simple_rerank_func` follows LightRAG's documented pattern:

```python
async def simple_rerank_func(
    query: str, 
    documents: List[str], 
    top_n: int = None, 
    **kwargs
) -> List[Dict[str, Any]]:
    # 1. Get embeddings for query and documents
    # 2. Calculate cosine similarity
    # 3. Sort by similarity score
    # 4. Return re-ranked results
```

## QueryParam Usage

Re-ranking is controlled using LightRAG's `QueryParam`:

```python
# With re-ranking
query_param = QueryParam(mode="local", top_k=5, enable_rerank=True)

# Without re-ranking
query_param = QueryParam(mode="local", top_k=5, enable_rerank=False)
```

## Testing

Run the test script to see LightRAG re-ranking in action:

```bash
cd backend
python test_lightrag_rerank.py
```

This will demonstrate:
1. Search results with and without re-ranking
2. Direct re-ranking function testing
3. Score improvements and result ordering

## Advantages

### ✅ Benefits
- **Native Integration**: Uses LightRAG's built-in re-ranking architecture
- **Simple Implementation**: Follows LightRAG's documented pattern
- **Efficient**: No custom embedding calls or complex logic
- **Configurable**: Enable/disable per query
- **Fallback Safe**: Returns original results if re-ranking fails

### 🔧 Technical Benefits
- **No Additional API Keys**: Uses existing OpenAI API key
- **Lightweight**: Minimal code overhead
- **Maintainable**: Follows LightRAG's conventions
- **Extensible**: Easy to modify or replace re-ranking function

## Comparison with Custom Implementation

| Aspect | LightRAG Built-in | Custom Implementation |
|--------|------------------|---------------------|
| **Complexity** | Simple | Complex |
| **Integration** | Native | Custom |
| **Performance** | Optimized | Additional overhead |
| **Maintenance** | Low | High |
| **Flexibility** | High | High |
| **Documentation** | Official | Custom |

## No Additional API Keys Required

This implementation uses the existing **OpenAI API key** for:
- Query embeddings
- Document embeddings
- Semantic similarity calculations

No additional API keys or services are needed.

## Future Enhancements

Potential improvements:
- **Cross-encoder Models**: Replace with more sophisticated re-ranking models
- **Caching**: Cache embeddings for better performance
- **Batch Processing**: Process multiple queries efficiently
- **Custom Weights**: Add configurable scoring weights

## Integration with Existing Features

The re-ranking works seamlessly with:
- **Citation System**: Source tracing continues to work
- **Query Validation**: Content filtering remains active
- **File Paths**: Document metadata is preserved
- **Chat Interface**: Frontend supports re-ranking toggle

## Usage in Frontend

The frontend API client supports the `enable_rerank` parameter:

```typescript
const results = await apiClient.search({
  query: "MSME loan eligibility",
  top_k: 5,
  enable_rerank: true  // or false
});
```

This provides a clean, simple, and efficient re-ranking solution that follows LightRAG's best practices!
