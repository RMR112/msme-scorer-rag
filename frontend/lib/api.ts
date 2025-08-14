import axios from "axios";

const API_BASE_URL = "https://msme-scorer-rag-production.up.railway.app";

// Debug: Log the API URL being used
console.log("🔧 API_BASE_URL:", API_BASE_URL);
console.log("🔧 NEXT_PUBLIC_API_URL env var:", process.env.NEXT_PUBLIC_API_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface AssessRequest {
  businessName: string;
  industryType: string;
  annualTurnover: number;
  netProfit: number;
  loanAmount: number;
  udyamRegistration: boolean;
  businessPlan: string;
}

export interface AssessResponse {
  score: number;
  risk_level: string;
  recommendations: string[];
  details: {
    breakdown: Array<{
      reason: string;
      points: number;
    }>;
    derived: {
      profit_margin_pct: number;
      loan_to_turnover_pct: number;
    };
  };
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  enable_rerank?: boolean;
}

export interface SearchResult {
  rank: number;
  content: string;
  score: number;
  metadata: any;
  document_metadata?: {
    document_id?: string;
    document_name?: string;
    document_type?: string;
    source_file?: string;
    [key: string]: any;
  };
}

export interface SearchResponse {
  results: SearchResult[];
  total_results: number;
}

export interface GenerateRequest {
  query: string;
}

export interface GenerateResponse {
  answer: string;
}

export const apiClient = {
  // Assess loan application
  assess: async (data: AssessRequest): Promise<AssessResponse> => {
    const response = await api.post("/api/assess", data);
    return response.data;
  },

  // Search documents
  search: async (data: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post("/api/search", data);
    return response.data;
  },

  // Generate answer
  generate: async (data: GenerateRequest): Promise<GenerateResponse> => {
    const response = await api.post("/api/generate", data);
    return response.data;
  },

  // Health check
  health: async () => {
    const response = await api.get("/api/health");
    return response.data;
  },

  // Get documents info
  getDocuments: async () => {
    const response = await api.get("/api/documents");
    return response.data;
  },
};
