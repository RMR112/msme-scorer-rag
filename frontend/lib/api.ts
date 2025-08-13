import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
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
}

export interface SearchResponse {
  results: Array<{
    rank: number;
    content: string;
    score: number;
    metadata: any;
    document_metadata?: any;
  }>;
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
    const response = await api.post('/api/assess', data);
    return response.data;
  },

  // Search documents
  search: async (data: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post('/api/search', data);
    return response.data;
  },

  // Generate answer
  generate: async (data: GenerateRequest): Promise<GenerateResponse> => {
    const response = await api.post('/api/generate', data);
    return response.data;
  },

  // Health check
  health: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Get documents info
  getDocuments: async () => {
    const response = await api.get('/api/documents');
    return response.data;
  },
};
