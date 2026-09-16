import {
  AuthResponse,
  InspectionCase,
  InspectionCreatePayload,
  InspectionListResponse,
  EvidenceAsset,
  User,
} from '../types';

const API_BASE = '/api/v1';

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('compliscan_token');
  }

  private getHeaders(isMultipart = false): HeadersInit {
    const headers: HeadersInit = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const isMultipart = options.body instanceof FormData;
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        ...this.getHeaders(isMultipart),
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { error: { message: response.statusText } };
      }
      const message = errorData?.error?.message || errorData?.detail || 'Request failed';
      throw new Error(message);
    }

    if (response.status === 204) {
      return null as unknown as T;
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, full_name: string, role: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name, role }),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Inspections
  async listInspections(): Promise<InspectionListResponse> {
    return this.request<InspectionListResponse>('/inspections');
  }

  async getInspection(id: string): Promise<InspectionCase> {
    return this.request<InspectionCase>(`/inspections/${id}`);
  }

  async createInspection(payload: InspectionCreatePayload): Promise<InspectionCase> {
    return this.request<InspectionCase>('/inspections', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateInspectionContext(id: string, payload: Partial<InspectionCreatePayload>): Promise<InspectionCase> {
    return this.request<InspectionCase>(`/inspections/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  // Evidence
  async uploadEvidence(inspectionId: string, file: File, evidenceType = 'PRIMARY'): Promise<EvidenceAsset> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('evidence_type', evidenceType);

    return this.request<EvidenceAsset>(`/inspections/${inspectionId}/evidence`, {
      method: 'POST',
      body: formData,
    });
  }

  async deleteEvidence(inspectionId: string, evidenceId: string): Promise<void> {
    return this.request<void>(`/inspections/${inspectionId}/evidence/${evidenceId}`, {
      method: 'DELETE',
    });
  }

  getEvidenceDownloadUrl(evidenceId: string): string {
    return `${API_BASE}/evidence/${evidenceId}/download`;
  }
}

export const api = new ApiClient();
