import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiResponse, AgentRequest, AgentResponse, Research, Strategy, GraphData } from '@/types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available (for future use)
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async checkHealth(): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get('/health/detailed');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Agent endpoints
  async executeAgent(request: AgentRequest): Promise<ApiResponse<AgentResponse>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/agents/execute`,
        request
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getAvailableAgents(): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/agents/available`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Research endpoints
  async createResearch(query: string, sources: string[]): Promise<ApiResponse<Research>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/research/analyze`,
        { query, sources }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getResearchStatus(researchId: string): Promise<ApiResponse<Research>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/research/analyze/${researchId}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getResearchHistory(limit = 10, offset = 0): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/research/history`,
        { params: { limit, offset } }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Strategy endpoints
  async getStrategies(limit = 10, offset = 0): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/strategies/list`,
        { params: { limit, offset } }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async generateStrategy(request: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/strategies/generate`,
        request
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getStrategyTypes(): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/strategies/types/available`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // NEW: Delete strategy method
  async deleteStrategy(strategyId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.delete(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/strategies/${strategyId}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // NEW: Update strategy method
  async updateStrategy(strategyData: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.patch(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/strategies/${strategyData.id}`,
        strategyData
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Backtest endpoints
  async runBacktest(request: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/backtest/run`,
        request
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getBacktestResult(backtestId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/backtest/${backtestId}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getBacktestReport(backtestId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/backtest/${backtestId}/report`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Knowledge Graph endpoints
  async getGraphStats(): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/knowledge-graph/stats`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async queryGraph(query: any): Promise<ApiResponse<GraphData>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/knowledge-graph/query`,
        query
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // NEW: Knowledge Graph specific methods for the visualization
  async getKnowledgeGraphStats(): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/knowledge-graph/stats`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getKnowledgeGraphVisualization(limit: number = 100): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/knowledge-graph/visualization?limit=${limit}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async searchKnowledgeEntities(query: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/knowledge-graph/search?q=${encodeURIComponent(query)}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getNodeDetails(nodeId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/knowledge-graph/node/${nodeId}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Report endpoints
  async generateReport(request: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/reports/generate`,
        request
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getReports(limit: number = 10, offset: number = 0): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/reports/list`,
        { params: { limit, offset } }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getReport(reportId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/reports/${reportId}`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async getReportTemplates(): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/reports/templates/list`
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  async previewReport(request: any): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.post(
        `${process.env.NEXT_PUBLIC_API_PREFIX}/reports/preview`,
        request
      );
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: this.getErrorMessage(error) };
    }
  }

  // Helper method to extract error messages
  private getErrorMessage(error: any): string {
    if (axios.isAxiosError(error)) {
      return error.response?.data?.detail || error.message || 'An error occurred';
    }
    return String(error);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();