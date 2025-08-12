# MSME Loan Scorer with LightRAG

A FastAPI-based backend system that combines MSME loan assessment with LightRAG-powered document search and recommendations. This project uses [LightRAG](https://github.com/HKUDS/LightRAG) for efficient retrieval-augmented generation to provide intelligent loan recommendations based on uploaded PDF documents.

## 🚀 Features

- **MSME Loan Assessment**: Comprehensive scoring system for MSME loan applications
- **LightRAG Integration**: Advanced document search and retrieval using LightRAG
- **PDF Processing**: Automatic extraction and processing of PDF documents
- **AI-Powered Recommendations**: Intelligent recommendations based on business plans and document content
- **FastAPI Backend**: Modern, async API with automatic documentation
- **OpenAI Integration**: Uses GPT-4o-mini for text generation and embeddings

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- 3 PDF documents for processing (MSME-related content recommended)

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd Scorer-MSME-RAG
   ```

2. **Install dependencies**:

   ```bash
   pip install -e .
   # or using uv
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FRONTEND_ORIGIN=http://localhost:3000
   ```

4. **Place your PDFs**:
   Add your 3 PDF documents to the `backend/` folder:
   - `MSME Loan.pdf`
   - `msme_e-book_1.pdf`
   - `17032022_SME Intensive Branches.pdf`

## 🚀 Usage

### 1. Ingest PDF Documents

First, process your PDF documents into the LightRAG system:

```bash
cd backend
python ingest.py
```

This will:

- Copy PDFs to the `rag-pdf/` directory
- Extract text from all pages
- Initialize LightRAG with OpenAI embeddings
- Store processed documents for retrieval

### 2. Start the FastAPI Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📚 API Endpoints

### Core Endpoints

#### `POST /api/assess`

Assess an MSME loan application with RAG-powered recommendations.

**Request Body**:

```json
{
  "businessName": "Tech Solutions Ltd",
  "industryType": "Technology",
  "annualTurnover": 5000000,
  "netProfit": 750000,
  "loanAmount": 2000000,
  "udyamRegistration": true,
  "businessPlan": "Our business plan focuses on..."
}
```

**Response**:

```json
{
  "score": 85.5,
  "risk_level": "LOW",
  "recommendations": [
    "Based on your business plan, consider focusing on...",
    "Your industry shows strong growth potential...",
    "Consider diversifying your revenue streams..."
  ],
  "details": {
    "turnover_score": 25.0,
    "profit_score": 20.0,
    "registration_bonus": 10.0
  }
}
```

#### `POST /api/search`

Search documents using LightRAG.

**Request Body**:

```json
{
  "query": "MSME loan eligibility criteria",
  "top_k": 5
}
```

**Response**:

```json
{
  "results": [
    {
      "rank": 1,
      "content": "MSME loan eligibility requires...",
      "score": 0.95,
      "metadata": {}
    }
  ],
  "total_results": 5
}
```

#### `POST /api/generate`

Generate comprehensive answers using LightRAG.

**Request Body**:

```json
{
  "query": "What are the key requirements for MSME loan approval?"
}
```

**Response**:

```json
{
  "answer": "Based on the available documents, MSME loan approval requires..."
}
```

### Utility Endpoints

- `GET /api/health` - Health check
- `GET /api/info` - Service information
- `POST /api/assess-legacy` - Legacy assessment endpoint

## 🔧 Configuration

### Environment Variables

| Variable          | Description               | Default                 |
| ----------------- | ------------------------- | ----------------------- |
| `OPENAI_API_KEY`  | OpenAI API key (required) | -                       |
| `FRONTEND_ORIGIN` | Frontend origin for CORS  | `http://localhost:3000` |

### LightRAG Configuration

The system uses LightRAG with the following configuration:

- **Embedding Model**: OpenAI embeddings
- **LLM Model**: GPT-4o-mini
- **Working Directory**: `backend/rag-pdf/`
- **Storage**: NanoDB for efficient document storage

## 📊 Project Structure

```
Scorer-MSME-RAG/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── ingest.py            # PDF ingestion script
│   ├── rag_store.py         # LightRAG integration
│   ├── rule_engine.py       # MSME scoring logic
│   ├── rag-pdf/             # Processed PDFs and LightRAG data
│   └── *.pdf                # Your PDF documents
├── pyproject.toml           # Project dependencies
├── uv.lock                  # Dependency lock file
└── README.md               # This file
```

## 🧪 Testing

### Test the API

1. **Health Check**:

   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Search Documents**:

   ```bash
   curl -X POST http://localhost:8000/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "MSME loan requirements", "top_k": 3}'
   ```

3. **Generate Answer**:
   ```bash
   curl -X POST http://localhost:8000/api/generate \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the benefits of MSME registration?"}'
   ```

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:

   - Ensure `OPENAI_API_KEY` is set in your `.env` file
   - Verify the API key is valid and has sufficient credits

2. **PDF Processing Issues**:

   - Check that PDFs are not password-protected
   - Ensure PDFs contain extractable text (not just images)
   - Verify PDFs are placed in the `backend/` folder

3. **LightRAG Initialization Errors**:
   - Check internet connection for model downloads
   - Ensure sufficient disk space in `backend/rag-pdf/`
   - Verify Python dependencies are correctly installed

### Logs

The application provides detailed logging:

- PDF processing progress
- LightRAG initialization status
- API request/response details
- Error messages and stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [LightRAG](https://github.com/HKUDS/LightRAG) - Simple and Fast Retrieval-Augmented Generation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [OpenAI](https://openai.com/) - GPT models and embeddings

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Open an issue on GitHub

---

⭐ **Star this repository if you find it helpful!** ⭐
