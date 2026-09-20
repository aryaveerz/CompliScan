import {
  AuthResponse,
  InspectionCase,
  InspectionCreatePayload,
  InspectionListResponse,
  InspectionSearchParams,
  InspectionSearchResponse,
  AuditEventItem,
  DashboardMetricsResponse,
  EvidenceAsset,
  ImageQualityAssessment,
  OCRResult,
  StructuredDeclarationResult,
  ApplicabilityListResponse,
  ComplianceEvaluationSummary,
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

    if (response.status === 401) {
      localStorage.removeItem('compliscan_token');
      localStorage.removeItem('compliscan_user');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(errorData.detail || errorData.message || `Request failed (${response.status})`);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
      throw new Error(errorData.detail || errorData.message || 'Invalid credentials');
    }
    return response.json();
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Inspections
  async listInspections(): Promise<InspectionListResponse> {
    return this.request<InspectionListResponse>('/inspections');
  }

  async getInspections(): Promise<InspectionListResponse> {
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

  async getEvidenceQuality(evidenceId: string): Promise<ImageQualityAssessment> {
    return this.request<ImageQualityAssessment>(`/evidence/${evidenceId}/quality`);
  }

  async triggerQualityAssessment(evidenceId: string): Promise<any> {
    return this.request<any>(`/evidence/${evidenceId}/assess-quality`, {
      method: 'POST',
    });
  }

  async getEvidenceOCR(evidenceId: string): Promise<OCRResult> {
    return this.request<OCRResult>(`/evidence/${evidenceId}/ocr`);
  }

  async triggerOCRProcessing(evidenceId: string): Promise<any> {
    return this.request<any>(`/evidence/${evidenceId}/process-ocr`, {
      method: 'POST',
    });
  }

  async getEvidenceDeclarations(evidenceId: string): Promise<StructuredDeclarationResult> {
    return this.request<StructuredDeclarationResult>(`/evidence/${evidenceId}/declarations`);
  }

  async triggerDeclarationExtraction(evidenceId: string): Promise<any> {
    return this.request<any>(`/evidence/${evidenceId}/extract-declarations`, {
      method: 'POST',
    });
  }

  // Phase 3 — Compliance & Applicability
  async getInspectionApplicability(inspectionId: string): Promise<ApplicabilityListResponse> {
    return this.request<ApplicabilityListResponse>(`/inspections/${inspectionId}/applicability`);
  }

  async evaluateInspectionCompliance(inspectionId: string, asyncJob = false): Promise<ComplianceEvaluationSummary> {
    return this.request<ComplianceEvaluationSummary>(`/inspections/${inspectionId}/evaluate?async_job=${asyncJob}`, {
      method: 'POST',
    });
  }

  async getInspectionFindings(inspectionId: string): Promise<ComplianceEvaluationSummary> {
    return this.request<ComplianceEvaluationSummary>(`/inspections/${inspectionId}/findings`);
  }

  getEvidenceDownloadUrl(evidenceId: string): string {
    const token = this.getToken();
    return `${API_BASE}/evidence/${evidenceId}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  }

  // Phase 4 — Verification, Reviewer Governance & Finalization
  async getVerificationState(inspectionId: string): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/verification-state`);
  }

  async recordDeclarationCorrection(inspectionId: string, payload: any): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/corrections`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async addDeclarationCorrection(inspectionId: string, payload: any): Promise<any> {
    return this.recordDeclarationCorrection(inspectionId, payload);
  }

  async recordManualObservation(inspectionId: string, payload: any): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/manual-observations`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async addManualObservation(inspectionId: string, payload: any): Promise<any> {
    return this.recordManualObservation(inspectionId, payload);
  }

  async submitInspectionForReview(inspectionId: string, payload?: { notes?: string }): Promise<InspectionCase> {
    return this.request<InspectionCase>(`/inspections/${inspectionId}/submit-for-review`, {
      method: 'POST',
      body: JSON.stringify(payload || {}),
    });
  }

  async submitForReview(inspectionId: string, payload?: { notes?: string }): Promise<InspectionCase> {
    return this.submitInspectionForReview(inspectionId, payload);
  }

  async getReviewQueue(): Promise<any[]> {
    return this.request<any[]>('/reviews/queue');
  }

  async recordReviewerDecision(inspectionId: string, payload: any): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/reviewer-decisions`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getReviewerDecisions(inspectionId: string): Promise<any[]> {
    return this.request<any[]>(`/inspections/${inspectionId}/reviewer-decisions`);
  }

  async requestInspectionRevision(inspectionId: string, payload: { reason: string; requested_changes?: string }): Promise<InspectionCase> {
    return this.request<InspectionCase>(`/inspections/${inspectionId}/request-revision`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async requestRevision(inspectionId: string, payload: { reason: string; requested_changes: string }): Promise<InspectionCase> {
    return this.requestInspectionRevision(inspectionId, payload);
  }

  async createEvidenceRequest(inspectionId: string, payload: any): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/evidence-requests`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getEvidenceRequests(inspectionId: string): Promise<any[]> {
    return this.request<any[]>(`/inspections/${inspectionId}/evidence-requests`);
  }

  async fulfillEvidenceRequest(erId: string, evidenceIdOrPayload: any, responseNote?: string): Promise<any> {
    const body =
      typeof evidenceIdOrPayload === 'string'
        ? { evidence_id: evidenceIdOrPayload, response_note: responseNote }
        : evidenceIdOrPayload;
    return this.request<any>(`/evidence-requests/${erId}/fulfill`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async finalizeInspection(inspectionId: string, payload: { final_decision: string; final_rationale: string }): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/finalize`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getFinalRecord(inspectionId: string): Promise<any> {
    return this.request<any>(`/inspections/${inspectionId}/final-record`);
  }

  async getFinalAuditRecord(inspectionId: string): Promise<any> {
    return this.getFinalRecord(inspectionId);
  }

  getFinalReportPdfUrl(inspectionId: string): string {
    return `${API_BASE}/inspections/${inspectionId}/final-report`;
  }

  async downloadFinalPdfReport(inspectionId: string, caseNumber?: string): Promise<void> {
    const token = this.getToken();
    const res = await fetch(`${API_BASE}/inspections/${inspectionId}/final-report`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to download report' }));
      throw new Error(err.detail || 'Failed to download PDF report');
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CompliScan_Report_${caseNumber || inspectionId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // ── Phase 5 Methods ────────────────────────────────────────────────────────

  async searchInspections(params: InspectionSearchParams = {}): Promise<InspectionSearchResponse> {
    const query = new URLSearchParams();
    if (params.q) query.append('q', params.q);
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    if (params.compliance) query.append('compliance', params.compliance);
    if (params.origin) query.append('origin', params.origin);
    if (params.start_date) query.append('start_date', params.start_date);
    if (params.end_date) query.append('end_date', params.end_date);
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.sort_order) query.append('sort_order', params.sort_order);

    const qs = query.toString();
    return this.request<InspectionSearchResponse>(`/inspections/search${qs ? `?${qs}` : ''}`);
  }

  async getAuditTrail(inspectionId: string): Promise<AuditEventItem[]> {
    return this.request<AuditEventItem[]>(`/inspections/${inspectionId}/audit-trail`);
  }

  async getDashboardMetrics(params: { date_range?: string; category?: string } = {}): Promise<DashboardMetricsResponse> {
    const query = new URLSearchParams();
    if (params.date_range) query.append('date_range', params.date_range);
    if (params.category) query.append('category', params.category);
    const qs = query.toString();
    return this.request<DashboardMetricsResponse>(`/dashboard/metrics${qs ? `?${qs}` : ''}`);
  }

  async downloadFinalDocxReport(inspectionId: string, caseNumber?: string): Promise<void> {
    const token = this.getToken();
    const res = await fetch(`${API_BASE}/inspections/${inspectionId}/report/docx`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to download report' }));
      throw new Error(err.detail || 'Failed to download DOCX report');
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CompliScan_Report_${caseNumber || inspectionId}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}

export const api = new ApiClient();
