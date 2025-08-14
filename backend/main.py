from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os
import asyncio
import logging
from datetime import datetime

from rule_engine import compute_score, sanitize_text
from rag_store import retrieve_recommendations, search_documents, generate_answer, get_document_summary

# Setup logging
logger = logging.getLogger(__name__)

load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# Add your Railway frontend URL to allowed origins
ALLOWED_ORIGINS = [
    FRONTEND_ORIGIN,
    "https://frontend-production-1e18.up.railway.app",  # Your specific frontend URL
    "https://msme-scorer-rag-frontend-production.up.railway.app",  # Alternative frontend URL
]
BUSINESS_PLAN_CHAR_LIMIT = 2000

app = FastAPI(
    title="MSME Loan Scorer with LightRAG",
    description="A FastAPI backend for MSME loan scoring with LightRAG-powered document search and recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    enable_rerank: Optional[bool] = True

class GenerateRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    rank: int
    content: str
    score: float
    metadata: Dict[str, Any] = {}
    document_metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int

class GenerateResponse(BaseModel):
    answer: str

class AssessRequest(BaseModel):
    businessName: str
    industryType: str
    annualTurnover: float
    netProfit: float
    loanAmount: float
    udyamRegistration: bool
    businessPlan: str

class AssessResponse(BaseModel):
    score: float
    risk_level: str
    recommendations: List[str]
    details: Dict[str, Any]

@app.post("/api/assess", response_model=AssessResponse)
async def assess(request: AssessRequest):
    """Assess MSME loan application with RAG-powered recommendations"""
    if len(request.businessPlan) > BUSINESS_PLAN_CHAR_LIMIT:
        raise HTTPException(
            status_code=400, 
            detail=f"businessPlan exceeds {BUSINESS_PLAN_CHAR_LIMIT} characters"
        )

    # Sanitize inputs
    sanitized_name = sanitize_text(request.businessName)
    sanitized_plan = sanitize_text(request.businessPlan)

    # Compute score
    payload = {
        "businessName": sanitized_name,
        "industryType": request.industryType,
        "annualTurnover": request.annualTurnover,
        "netProfit": request.netProfit,
        "loanAmount": request.loanAmount,
        "udyamRegistration": request.udyamRegistration,
        "businessPlan": sanitized_plan
    }
    
    score_result = await compute_score(payload)
    
    # Check if there's a validation error in the business plan
    if "error" in score_result:
        return {
            "score": score_result["score0to10"],
            "risk_level": score_result["band"],
            "recommendations": [score_result["error"]],  # Return the error message as recommendation
            "details": {
                "breakdown": score_result["breakdown"],
                "derived": score_result["derived"],
                "validation_error": score_result.get("validation_error", "Invalid business plan")
            }
        }
    
    # Get RAG-powered recommendations based on business plan and Udyam registration
    try:
        recs = await retrieve_recommendations(sanitized_plan, top_k=3, udyam_registration=request.udyamRegistration)
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        recs = ["Unable to generate recommendations at this time."]

    # Map the score result to match AssessResponse model
    return {
        "score": score_result["score0to10"],
        "risk_level": score_result["band"],
        "recommendations": recs,
        "details": {
            "breakdown": score_result["breakdown"],
            "derived": score_result["derived"]
        }
    }

@app.post("/api/search", response_model=SearchResponse)
async def search_docs(request: SearchRequest):
    """Search documents using LightRAG"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = await search_documents(request.query, top_k=request.top_k, enable_rerank=request.enable_rerank)
        return SearchResponse(
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_rag_answer(request: GenerateRequest):
    """Generate comprehensive answer using LightRAG"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        answer = await generate_answer(request.query)
        return GenerateResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MSME Loan Scorer with LightRAG",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def get_info():
    """Get service information"""
    return {
        "name": "MSME Loan Scorer with LightRAG",
        "description": "FastAPI backend for MSME loan scoring with LightRAG-powered document search",
        "version": "1.0.0",
        "features": [
            "MSME loan assessment",
            "LightRAG document search",
            "AI-powered recommendations",
            "Document generation",
            "Document metadata tracking"
        ],
        "endpoints": [
            "POST /api/assess - Assess loan application",
            "POST /api/search - Search documents",
            "POST /api/generate - Generate answers",
            "GET /api/health - Health check",
            "GET /api/info - Service information",
            "GET /api/documents - Document summary"
        ]
    }

@app.get("/api/documents")
async def get_documents():
    """Get summary of all ingested documents with metadata"""
    return get_document_summary()

@app.post("/api/ingest-pdfs")
async def ingest_pdfs():
    """One-time endpoint to ingest PDFs into LightRAG"""
    try:
        # Import the ingestion function
        from ingest import main as ingest_main
        
        # Run the ingestion
        await ingest_main()
        
        return {
            "status": "success",
            "message": "PDFs ingested successfully into LightRAG",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error during PDF ingestion: {e}")
        return {
            "status": "error",
            "message": f"Failed to ingest PDFs: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/check-files")
async def check_files():
    """Check what PDF files are available in the backend directory"""
    import os
    
    backend_dir = os.path.dirname(__file__)
    pdf_files = []
    
    try:
        for file in os.listdir(backend_dir):
            if file.lower().endswith('.pdf'):
                pdf_files.append(file)
        
        return {
            "status": "success",
            "pdf_files": pdf_files,
            "total_pdfs": len(pdf_files),
            "backend_directory": backend_dir
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check files: {str(e)}",
            "pdf_files": [],
            "total_pdfs": 0
        }

@app.get("/api/test-connection")
async def test_connection():
    """Test endpoint to verify frontend-backend connection"""
    return {
        "status": "success",
        "message": "Backend is connected and working!",
        "rag_status": "LightRAG files are present and loaded",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/debug-cors")
async def debug_cors():
    """Debug endpoint to check CORS configuration"""
    return {
        "status": "success",
        "allowed_origins": ALLOWED_ORIGINS,
        "frontend_origin": FRONTEND_ORIGIN,
        "message": "CORS configuration loaded"
    }

# Legacy endpoint for backward compatibility
@app.post("/api/assess-legacy")
async def assess_legacy(request: Request):
    """Legacy assessment endpoint for backward compatibility"""
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Expected JSON object")

    required = ["businessName", "industryType", "annualTurnover", "netProfit", "loanAmount", "udyamRegistration", "businessPlan"]
    for r in required:
        if r not in payload:
            raise HTTPException(status_code=400, detail=f"Missing field: {r}")

    if len(payload["businessPlan"]) > BUSINESS_PLAN_CHAR_LIMIT:
        raise HTTPException(status_code=400, detail=f"businessPlan exceeds {BUSINESS_PLAN_CHAR_LIMIT} chars")

    payload["businessName"] = sanitize_text(payload["businessName"])
    payload["businessPlan"] = sanitize_text(payload["businessPlan"])

    score_result = await compute_score(payload)
    recs = await retrieve_recommendations(payload["businessPlan"], top_k=3)

    return {**score_result, "recommendations": recs}

