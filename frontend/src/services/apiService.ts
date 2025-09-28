/**
 * API Service Layer
 * Centralized API communication for the Medical Platform
 */

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

export interface SearchQuery {
  query_text: string;
  content_types?: string[];
  specialty_filter?: string;
  max_results?: number;
  expand_medical_terms?: boolean;
  use_ai_expansion?: boolean;
  include_related?: boolean;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  content_type: string;
  relevance_score: number;
  medical_concepts: string[];
  source: string;
  metadata: Record<string, any>;
}

export interface SearchResponse {
  results: SearchResult[];
  total_found: number;
  processing_time_ms: number;
  clusters: Array<{
    name: string;
    count: number;
    results: string[];
  }>;
  suggestions: string[];
}

export interface Chapter {
  id: string;
  title: string;
  content: string;
  is_alive: boolean;
  active_users: Array<{
    user_id: string;
    username: string;
    connected_at: string;
  }>;
  last_updated: string;
  confidence_score: number;
  conflicts: any[];
  cross_references: any[];
}

export interface SynthesisRequest {
  topic: string;
  sources?: string[];
  specialty?: string;
  ai_model?: string;
  include_research?: boolean;
}

export interface SynthesisTask {
  task_id: string;
  status: string;
  progress: number;
  current_step: string;
  estimated_remaining: string;
  result?: {
    chapter_id: string;
    title: string;
    word_count: number;
    confidence_score: number;
    sources_used: number;
    citations_generated: number;
  };
}

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('auth_token') || 'dev_token'; // Default for development
  }

  /**
   * Set authentication token
   */
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  /**
   * Get authentication headers
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Make API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Search API methods

  /**
   * Perform search
   */
  async search(query: string, specialty?: string, contentType?: string, limit: number = 20): Promise<ApiResponse<any>> {
    return this.request('/api/search/', {
      method: 'POST',
      body: JSON.stringify({
        query,
        specialty,
        content_type: contentType,
        limit
      }),
    });
  }

  /**
   * Get search suggestions
   */
  async getSearchSuggestions(query: string): Promise<ApiResponse<any>> {
    return this.request(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
  }

  // Chapter API methods

  /**
   * Get chapter by ID
   */
  async getChapter(chapterId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/chapters/${chapterId}`);
  }

  /**
   * Update chapter
   */
  async updateChapter(chapterId: string, updateData: { title?: string; content?: string; specialty?: string }): Promise<ApiResponse<any>> {
    return this.request(`/api/chapters/${chapterId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  /**
   * List chapters
   */
  async listChapters(params: {
    limit?: number;
    offset?: number;
    specialty?: string;
    status?: string;
  } = {}): Promise<ApiResponse<any>> {
    const searchParams = new URLSearchParams();

    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.offset) searchParams.append('offset', params.offset.toString());
    if (params.specialty) searchParams.append('specialty', params.specialty);
    if (params.status) searchParams.append('status', params.status);

    return this.request(`/api/chapters?${searchParams.toString()}`);
  }

  /**
   * Create new chapter
   */
  async createChapter(chapterData: {
    title: string;
    content?: string;
    specialty?: string;
    auto_enhance?: boolean;
  }): Promise<ApiResponse<any>> {
    return this.request('/api/chapters/', {
      method: 'POST',
      body: JSON.stringify(chapterData),
    });
  }

  /**
   * Delete chapter
   */
  async deleteChapter(chapterId: string): Promise<ApiResponse<any>> {
    return this.request(`/api/chapters/${chapterId}`, {
      method: 'DELETE',
    });
  }

  // AI API methods

  /**
   * Generate AI content
   */
  async generateContent(prompt: string, contextType: string = 'medical', maxTokens: number = 1000, temperature: number = 0.7): Promise<ApiResponse<any>> {
    return this.request('/api/ai/generate', {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        context_type: contextType,
        max_tokens: maxTokens,
        temperature,
      }),
    });
  }

  /**
   * Enhance content with AI
   */
  async enhanceContent(content: string, maxTokens: number = 1000, temperature: number = 0.7): Promise<ApiResponse<any>> {
    return this.request('/api/ai/enhance', {
      method: 'POST',
      body: JSON.stringify({
        prompt: content,
        max_tokens: maxTokens,
        temperature,
      }),
    });
  }

  /**
   * Summarize content with AI
   */
  async summarizeContent(content: string, maxTokens: number = 500): Promise<ApiResponse<any>> {
    return this.request('/api/ai/summarize', {
      method: 'POST',
      body: JSON.stringify({
        prompt: content,
        max_tokens: maxTokens,
      }),
    });
  }

  // Health API methods

  /**
   * Basic health check
   */
  async healthCheck(): Promise<ApiResponse<any>> {
    return this.request('/api/health/');
  }

  /**
   * Detailed status check
   */
  async getSystemStatus(): Promise<ApiResponse<any>> {
    return this.request('/api/health/status');
  }
}

// Singleton instance
export const apiService = new ApiService();

// React hooks for API calls
export const useApi = () => {
  return {
    search: {
      search: apiService.search.bind(apiService),
      suggestions: apiService.getSearchSuggestions.bind(apiService),
    },
    chapters: {
      get: apiService.getChapter.bind(apiService),
      update: apiService.updateChapter.bind(apiService),
      list: apiService.listChapters.bind(apiService),
      create: apiService.createChapter.bind(apiService),
      delete: apiService.deleteChapter.bind(apiService),
    },
    ai: {
      generate: apiService.generateContent.bind(apiService),
      enhance: apiService.enhanceContent.bind(apiService),
      summarize: apiService.summarizeContent.bind(apiService),
    },
    health: {
      check: apiService.healthCheck.bind(apiService),
      status: apiService.getSystemStatus.bind(apiService),
    },
  };
};
