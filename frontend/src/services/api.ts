import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Dashboard endpoints
  async getDashboardStats() {
    const response = await this.api.get('/dashboard/stats');
    return response.data;
  }

  async getTrendsData(days: number = 30) {
    const response = await this.api.get(`/dashboard/trends?days=${days}`);
    return response.data;
  }

  // Repository endpoints
  async getRepositories() {
    const response = await this.api.get('/reviews/repositories');
    return response.data;
  }

  async getRepositoryAnalytics(repoId: number) {
    const response = await this.api.get(`/dashboard/repositories/${repoId}/analytics`);
    return response.data;
  }

  async getPullRequests(repoId: number) {
    const response = await this.api.get(`/reviews/repositories/${repoId}/pull-requests`);
    return response.data;
  }

  // Review endpoints
  async analyzeCodeManually(code: string, filePath: string, language: string) {
    const response = await this.api.post('/reviews/manual', {
      code,
      file_path: filePath,
      language,
    });
    return response.data;
  }

  async getReviewSession(sessionId: string) {
    const response = await this.api.get(`/reviews/session/${sessionId}`);
    return response.data;
  }

  async getReviewResults(sessionId: string) {
    const response = await this.api.get(`/reviews/session/${sessionId}/results`);
    return response.data;
  }

  async getRecentSessions(limit: number = 20) {
    const response = await this.api.get(`/dashboard/sessions?limit=${limit}`);
    return response.data;
  }

  // Webhook endpoints
  async triggerWebhook(payload: any) {
    const response = await this.api.post('/webhooks/github', payload);
    return response.data;
  }
}

export const apiService = new ApiService();
