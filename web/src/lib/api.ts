const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://work-1-rvvbmdvsfidltqxj.prod-runtime.all-hands.dev';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      if (typeof window !== 'undefined') {
        localStorage.setItem('token', token);
      }
    } else {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'An error occurred');
    }

    return response.json();
  }

  // Auth
  async signup(email: string, password: string, fullName?: string) {
    return this.request<{ access_token: string; user: any }>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
  }

  async login(email: string, password: string) {
    return this.request<{ access_token: string; user: any }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async getMe() {
    return this.request<any>('/api/auth/me');
  }

  async updateMe(data: { full_name?: string; business_type?: string; onboarding_completed?: boolean }) {
    return this.request<any>('/api/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Workflows
  async getWorkflows() {
    return this.request<any[]>('/api/workflows/');
  }

  async getWorkflow(id: string) {
    return this.request<any>(`/api/workflows/${id}`);
  }

  async createWorkflow(data: any) {
    return this.request<any>('/api/workflows/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateWorkflow(id: string, data: any) {
    return this.request<any>(`/api/workflows/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteWorkflow(id: string) {
    return this.request<any>(`/api/workflows/${id}`, {
      method: 'DELETE',
    });
  }

  // Executions
  async getExecutions(workflowId?: string) {
    const params = workflowId ? `?workflow_id=${workflowId}` : '';
    return this.request<any[]>(`/api/executions/${params}`);
  }

  async getExecution(id: string) {
    return this.request<any>(`/api/executions/${id}`);
  }

  async createExecution(workflowId: string, isTest: boolean = false, triggerData?: any) {
    return this.request<any>('/api/executions/', {
      method: 'POST',
      body: JSON.stringify({
        workflow_id: workflowId,
        is_test: isTest,
        trigger_data: triggerData,
      }),
    });
  }

  // Approvals
  async getApprovals(status?: string) {
    const params = status ? `?status_filter=${status}` : '';
    return this.request<any[]>(`/api/approvals/${params}`);
  }

  async getApproval(id: string) {
    return this.request<any>(`/api/approvals/${id}`);
  }

  async actionApproval(id: string, action: 'approve' | 'reject', rejectionReason?: string) {
    return this.request<any>(`/api/approvals/${id}/action`, {
      method: 'POST',
      body: JSON.stringify({ action, rejection_reason: rejectionReason }),
    });
  }

  async approveAction(id: string) {
    return this.actionApproval(id, 'approve');
  }

  async rejectAction(id: string, reason?: string) {
    return this.actionApproval(id, 'reject', reason);
  }

  async runWorkflow(id: string, isTest: boolean = false, triggerData?: any) {
    return this.createExecution(id, isTest, triggerData);
  }

  async createWorkflowFromTemplate(templateId: string) {
    return this.useTemplate(templateId);
  }

  // Templates aliases for cleaner API
  templates = {
    list: (category?: string, businessType?: string) => this.getTemplates(category, businessType),
    get: (id: string) => this.getTemplate(id),
    use: (id: string) => this.useTemplate(id),
  };

  // Connections
  async getConnections() {
    return this.request<any[]>('/api/connections/');
  }

  async createConnection(data: { name: string; type: string; credentials?: any }) {
    return this.request<any>('/api/connections/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteConnection(id: string) {
    return this.request<any>(`/api/connections/${id}`, {
      method: 'DELETE',
    });
  }

  async authorizeConnection(provider: string): Promise<{ authorization_url?: string; demo_mode?: boolean }> {
    return this.request<{ authorization_url?: string; demo_mode?: boolean }>(
      `/api/connections/${provider}/authorize`
    );
  }

  async refreshConnection(connectionId: string) {
    return this.request<any>(`/api/connections/refresh/${connectionId}`, {
      method: 'POST',
    });
  }

  // Templates
  async getTemplates(category?: string, businessType?: string) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (businessType) params.append('business_type', businessType);
    const queryString = params.toString();
    return this.request<any[]>(`/api/templates/${queryString ? `?${queryString}` : ''}`);
  }

  async getTemplate(id: string) {
    return this.request<any>(`/api/templates/${id}`);
  }

  async useTemplate(id: string) {
    return this.request<any>(`/api/templates/${id}/use`, {
      method: 'POST',
    });
  }

  // AI
  async generateWorkflow(prompt: string) {
    return this.request<any>('/api/ai/generate-workflow', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async suggestNodeParams(nodeType: string, userGoal: string, sampleData?: any) {
    return this.request<any>('/api/ai/suggest-node-params', {
      method: 'POST',
      body: JSON.stringify({
        node_type: nodeType,
        user_goal: userGoal,
        sample_data: sampleData,
      }),
    });
  }

  // Chat APIs
  async chatExecution(executionId: string, message: string, history?: Array<{role: string, content: string}>) {
    return this.request<{response: string, context_type: string}>(`/api/chat/execution/${executionId}`, {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    });
  }

  async chatAssistant(message: string, history?: Array<{role: string, content: string}>) {
    return this.request<{response: string, context_type: string}>('/api/chat/assistant', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    });
  }

  async getAssistantContext() {
    return this.request<{
      context_summary: {
        workflows_count: number;
        executions_count: number;
        user_name: string;
        business_type?: string;
      };
      capabilities: string[];
    }>('/api/chat/assistant/context');
  }
}

export const api = new ApiClient();
