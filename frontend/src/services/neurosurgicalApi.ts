/**
 * Neurosurgical API Service
 * Frontend service for interacting with the neurosurgical encyclopedia backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Types
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface ChapterSearchParams {
  query?: string;
  specialty?: string;
  subspecialty?: string;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  status?: 'draft' | 'review' | 'published';
  limit?: number;
  offset?: number;
}

interface AnatomicalStructureParams {
  region?: string;
  tissueType?: string;
  eloquentOnly?: boolean;
  includeVasculature?: boolean;
}

interface ContentGenerationRequest {
  prompt: string;
  context: string;
  maxTokens?: number;
  temperature?: number;
  provider?: string;
}

interface LiteratureSearchParams {
  query: string;
  sources?: string[];
  maxResults?: number;
  yearFrom?: number;
  yearTo?: number;
}

class NeurosurgicalApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Chapter Management
  async getChapters(params: ChapterSearchParams = {}): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/chapters', { params });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getChapter(id: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get(`/api/chapters/${id}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async createChapter(chapterData: any): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/api/chapters', chapterData);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async updateChapter(id: string, chapterData: any): Promise<ApiResponse> {
    try {
      const response = await this.api.put(`/api/chapters/${id}`, chapterData);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async publishChapter(id: string): Promise<ApiResponse> {
    try {
      const response = await this.api.post(`/api/chapters/${id}/publish`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteChapter(id: string): Promise<ApiResponse> {
    try {
      const response = await this.api.delete(`/api/chapters/${id}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Anatomical Structures
  async getAnatomicalStructures(params: AnatomicalStructureParams = {}): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/anatomy/structures', { params });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAnatomicalStructure(id: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get(`/api/anatomy/structures/${id}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAnatomicalHierarchy(): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/anatomy/hierarchy');
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Surgical Procedures
  async getSurgicalProcedures(params: any = {}): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/procedures', { params });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getSurgicalProcedure(id: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get(`/api/procedures/${id}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Content Updates
  async getPendingUpdates(chapterId?: string): Promise<ApiResponse> {
    try {
      const params = chapterId ? { chapter_id: chapterId } : {};
      const response = await this.api.get('/api/updates/pending', { params });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async approveUpdate(updateId: string, reviewNotes?: string): Promise<ApiResponse> {
    try {
      const response = await this.api.post(`/api/updates/${updateId}/approve`, {
        review_notes: reviewNotes,
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async rejectUpdate(updateId: string, reason: string): Promise<ApiResponse> {
    try {
      const response = await this.api.post(`/api/updates/${updateId}/reject`, {
        reason,
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // AI Content Generation
  async generateContent(request: ContentGenerationRequest): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/api/ai/generate', request);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async validateContent(content: string, sources?: string[]): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/api/ai/validate', {
        content,
        sources,
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async synthesizeChapter(topic: string, sources: string[]): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/api/ai/synthesize', {
        topic,
        sources,
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Literature Search
  async searchLiterature(params: LiteratureSearchParams): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/api/literature/search', params);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getPublicationDetails(pmid: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get(`/api/literature/publication/${pmid}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // PDF Processing
  async uploadPDF(file: File, documentType?: string): Promise<ApiResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (documentType) {
        formData.append('document_type', documentType);
      }

      const response = await this.api.post('/api/pdf/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getPDFProcessingStatus(taskId: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get(`/api/pdf/status/${taskId}`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Dashboard Analytics
  async getDashboardMetrics(): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/dashboard/metrics');
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getChapterAnalytics(chapterId?: string): Promise<ApiResponse> {
    try {
      const params = chapterId ? { chapter_id: chapterId } : {};
      const response = await this.api.get('/api/dashboard/analytics', { params });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getSystemHealth(): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/dashboard/health');
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getRecentActivity(limit: number = 20): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/dashboard/activity', {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // User Management
  async getCurrentUser(): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/users/me');
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async updateUserProfile(profileData: any): Promise<ApiResponse> {
    try {
      const response = await this.api.put('/api/users/me', profileData);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Search
  async searchContent(query: string, filters: any = {}): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/api/search', {
        query,
        filters,
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getSearchSuggestions(query: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get('/api/search/suggestions', {
        params: { q: query },
      });
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Alive Chapter System
  async triggerChapterUpdate(chapterId: string): Promise<ApiResponse> {
    try {
      const response = await this.api.post(`/api/chapters/${chapterId}/update`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getUpdateHistory(chapterId: string): Promise<ApiResponse> {
    try {
      const response = await this.api.get(`/api/chapters/${chapterId}/history`);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  async configureMonitoring(chapterId: string, config: any): Promise<ApiResponse> {
    try {
      const response = await this.api.put(`/api/chapters/${chapterId}/monitoring`, config);
      return response.data;
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Utility Methods
  private handleError(error: any): ApiResponse {
    console.error('API Error:', error);
    
    if (error.response) {
      return {
        success: false,
        error: error.response.data?.message || error.response.statusText,
        data: error.response.data,
      };
    } else if (error.request) {
      return {
        success: false,
        error: 'Network error - please check your connection',
      };
    } else {
      return {
        success: false,
        error: error.message || 'An unexpected error occurred',
      };
    }
  }

  // WebSocket connection for real-time updates
  connectWebSocket(onMessage: (data: any) => void): WebSocket | null {
    try {
      const wsUrl = this.baseURL.replace('http', 'ws') + '/ws';
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('WebSocket message parsing error:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      return ws;
    } catch (error) {
      console.error('WebSocket connection error:', error);
      return null;
    }
  }
}

// Create and export singleton instance
export const neurosurgicalApi = new NeurosurgicalApiService();
export default neurosurgicalApi;
