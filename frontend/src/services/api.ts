import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '300000');
const MAX_RETRIES = 3;

const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: API_TIMEOUT,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config) => {
    const timestamp = new Date().toISOString();
    config.headers['X-Request-ID'] = `${timestamp}-${Math.random().toString(36).substr(2, 9)}`;
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = MAX_RETRIES,
  delay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      const isLastAttempt = i === maxRetries - 1;
      const isRetryableError =
        axios.isAxiosError(error) &&
        (error.code === 'ECONNABORTED' ||
         error.code === 'ENOTFOUND' ||
         error.response?.status === 503 ||
         error.response?.status === 429);
      if (isLastAttempt || !isRetryableError) throw error;
      await new Promise((resolve) => setTimeout(resolve, delay));
      delay *= 2;
    }
  }
  throw new Error('Max retries exceeded');
}

// ============ TYPE DEFINITIONS ============

export interface VerificationResult {
  original_text: string;
  original_language: string;
  darija_latin: string;
  darija_arabic: string;
  claim: string;
  claim_type: string;
  verification_label: 'true' | 'false' | 'partially_true' | 'unverifiable';
  explanation: string;
  confidence_score: number;
  source_url?: string;
  medical_domain: string;
  processing_time_ms?: number;
}

export interface VerifyResponse {
  success: boolean;
  data: VerificationResult;
  claim_id: number;
  timestamp: string;
  message?: string;
}

export interface VideoProcessingResponse {
  success: boolean;
  job_id: string;
  status: string;
  transcription?: string;
  english_translation?: string;
  verification_results?: VerificationResult[];
  error?: string;
}

export interface AnalyticsData {
  total_verified: number;
  true_count: number;
  false_count: number;
  partial_count: number;
  unverifiable_count: number;
  avg_confidence_score: number;
  domain_distribution: Record<string, number>;
  daily_trend: Array<{ date: string; true: number; false: number; partial: number; unverifiable: number }>;
  misinformation_rate: number;
  avg_processing_time_ms: number;
  timestamp: string;
}

export interface TrendingClaim {
  id: number;
  claim: string;
  label: string;
  confidence: number;
  domain: string;
  created_at: string;
}

export interface ClaimDataResponse {
  total_count: number;
  page: number;
  per_page: number;
  claims: VerificationResult[];
  filters_applied: Record<string, any>;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  database: string;
  redis: string;
  ml_service: string;
  version: string;
}

export interface ConfidenceDistribution {
  confidence_distribution: Record<string, number>;
  period_days: number;
}

export interface DomainStats {
  domain_distribution: Record<string, number>;
  period_days: number;
}

export interface RecentVerification {
  id: number;
  claim: string;
  verification_label: string;
  confidence_score: number;
  created_at: string;
}

// ============ API CLIENT ============

export const apiClient = {
  // --- Verification ---
  verify: async (text: string, language = 'ar'): Promise<VerifyResponse> =>
    retryWithBackoff(() =>
      api.post('/verify/', { text, language }).then((r) => r.data)
    ),

  verifyVideoUrl: async (url: string, language = 'ar'): Promise<VideoProcessingResponse> =>
    retryWithBackoff(
      () => api.post('/verify/video-url', { url, language }).then((r) => r.data),
      1, // no retries for long video ops
      0
    ),

  verifyBatch: async (texts: string[], language = 'ar'): Promise<any> =>
    retryWithBackoff(() =>
      api.post('/verify/batch', texts, { params: { language } }).then((r) => r.data)
    ),

  getRecentVerifications: async (userId: string, limit = 10): Promise<{ success: boolean; claims: RecentVerification[]; count: number }> =>
    retryWithBackoff(() =>
      api.get(`/verify/recent/${userId}`, { params: { limit } }).then((r) => r.data)
    ),

  getVerificationStats: async (days = 7): Promise<any> =>
    retryWithBackoff(() =>
      api.get('/verify/stats', { params: { days } }).then((r) => r.data)
    ),

  // --- Analytics ---
  getDashboardAnalytics: async (days = 7): Promise<AnalyticsData> =>
    retryWithBackoff(() =>
      api.get('/analytics/dashboard', { params: { days } }).then((r) => r.data)
    ),

  getTrendingClaims: async (limit = 10): Promise<TrendingClaim[]> =>
    retryWithBackoff(() =>
      api.get('/analytics/trending', { params: { limit } }).then((r) => r.data)
    ),

  getConfidenceDistribution: async (days = 7, bins = 10): Promise<ConfidenceDistribution> =>
    retryWithBackoff(() =>
      api.get('/analytics/confidence-distribution', { params: { days, bins } }).then((r) => r.data)
    ),

  // --- Dataset ---
  getDataset: async (page = 1, perPage = 20, filters?: { domain?: string; label?: string; min_confidence?: number }): Promise<ClaimDataResponse> =>
    retryWithBackoff(() =>
      api.get('/dataset/claims', { params: { page, per_page: perPage, ...filters } }).then((r) => r.data)
    ),

  getDomainDistribution: async (days = 7): Promise<DomainStats> =>
    retryWithBackoff(() =>
      api.get('/dataset/stats/domains', { params: { days } }).then((r) => r.data)
    ),

  // --- Health ---
  healthCheck: async (): Promise<HealthStatus> => {
    try {
      const response = await api.get('/health/').then((r) => r.data);
      return response;
    } catch {
      return { status: 'unhealthy', database: 'unknown', redis: 'unknown', ml_service: 'unknown', version: 'N/A' };
    }
  },

  readinessCheck: async (): Promise<{ ready: boolean; timestamp: string }> => {
    try {
      return await api.get('/health/ready').then((r) => r.data);
    } catch {
      return { ready: false, timestamp: new Date().toISOString() };
    }
  },

  getApiLatency: async (): Promise<{ latency_ms: number; status: string }> => {
    const t = performance.now();
    try {
      await api.get('/health/');
      return { latency_ms: Math.round(performance.now() - t), status: 'healthy' };
    } catch {
      return { latency_ms: Math.round(performance.now() - t), status: 'unhealthy' };
    }
  },
};

export default api;
