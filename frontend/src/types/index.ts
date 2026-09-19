export type UserRole = 'INSPECTOR' | 'REVIEWER';

export type OriginStatus = 'DOMESTIC' | 'IMPORTED' | 'UNKNOWN';

export type InspectionLifecycleState =
  | 'DRAFT'
  | 'EVIDENCE_UPLOADED'
  | 'EXTRACTED'
  | 'APPLICABILITY_EVALUATED'
  | 'EVALUATED'
  | 'IN_VERIFICATION'
  | 'SUBMITTED_FOR_REVIEW'
  | 'REQUIRES_REVISION'
  | 'FINALIZED';

export type ProcessingState = 'IDLE' | 'PROCESSING' | 'FAILED';

export type FinalizationStatus = 'UNFINALIZED' | 'READ_ONLY';

export type EvidenceType = 'PRIMARY' | 'DERIVED' | 'SUPPLEMENTAL';

export type ComplianceResult =
  | 'PASS'
  | 'POTENTIAL_NON_COMPLIANCE'
  | 'REQUIRES_REVIEW'
  | 'NOT_APPLICABLE'
  | 'INCOMPLETE'
  | 'PROCESSING_FAILED'
  | 'CONFIRMED_VIOLATION';

export type ImageQualityStatus = 'USABLE' | 'NEEDS_REVIEW' | 'UNUSABLE';

export type QualityReasonCode =
  | 'QUALITY_ACCEPTABLE'
  | 'IMAGE_DECODE_FAILED'
  | 'UNSUPPORTED_IMAGE_TYPE'
  | 'INVALID_DIMENSIONS'
  | 'LOW_RESOLUTION'
  | 'EXCESSIVE_BLUR'
  | 'NEAR_BLANK_IMAGE'
  | 'EXTREME_EXPOSURE';

export interface ImageQualityAssessment {
  id: string;
  evidence_id: string;
  inspection_id: string;
  quality_status: ImageQualityStatus;
  assessment_version: string;
  width: number;
  height: number;
  total_pixels: number;
  mime_type: string;
  is_decoded: boolean;
  sharpness_score?: number;
  brightness_score?: number;
  contrast_score?: number;
  reason_codes: QualityReasonCode[];
  details?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface BoundingBox {
  x: number; // percentage 0-100
  y: number; // percentage 0-100
  width: number; // percentage 0-100
  height: number; // percentage 0-100
}

export interface ExtractedDeclarationItem {
  id: string;
  rule_citation: string;
  declaration_name: string;
  extracted_value: string;
  result: ComplianceResult;
  applicability: string;
  is_applicable: boolean;
  evidence_id?: string;
  bounding_box?: BoundingBox;
  verified_value?: string;
  inspector_notes?: string;
  reviewer_override?: boolean;
  reviewer_justification?: string;
}

export interface AuditEventItem {
  id: string;
  inspection_id?: string;
  actor_id?: string;
  actor_role: string;
  event_type: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface OCRToken {
  token_index: number;
  line_index: number;
  text: string;
  confidence: number;
  bounding_box: {
    points: number[][];
    coordinate_space: string;
  };
}

export interface OCRResult {
  id: string;
  evidence_id: string;
  inspection_id: string;
  ocr_engine: string;
  ocr_engine_version: string;
  processing_version: string;
  processing_blocked: boolean;
  block_reason?: string;
  total_tokens: number;
  full_text?: string;
  tokens: OCRToken[];
  created_at: string;
  updated_at: string;
}

export type ObservationStatus =
  | 'OBSERVED'
  | 'NOT_OBSERVED'
  | 'AMBIGUOUS'
  | 'CONFLICTING'
  | 'UNREADABLE';

export interface CandidateValue {
  raw_text: string;
  parsed_value?: Record<string, any>;
  source_token_indices: number[];
}

export interface ManufacturerIdentityField {
  status: ObservationStatus;
  declaration_type?: string;
  name?: string;
  address?: string;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface CommodityNameField {
  status: ObservationStatus;
  name?: string;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface NetQuantityField {
  status: ObservationStatus;
  quantity_value?: number;
  unit?: string;
  unit_raw?: string;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface ManufacturePackingDateField {
  status: ObservationStatus;
  date_type?: string;
  month?: number;
  year?: number;
  raw_date_string?: string;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface MaximumRetailPriceField {
  status: ObservationStatus;
  currency?: string;
  amount?: number;
  includes_all_taxes_stated?: boolean;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface ConsumerCareField {
  status: ObservationStatus;
  contact_name?: string;
  phone?: string;
  email?: string;
  address?: string;
  website?: string;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface CountryOfOriginField {
  status: ObservationStatus;
  country_name?: string;
  raw_text?: string;
  source_token_indices: number[];
  candidates: CandidateValue[];
}

export interface StructuredDeclarations {
  manufacturer_identity: ManufacturerIdentityField;
  commodity_name: CommodityNameField;
  net_quantity: NetQuantityField;
  manufacture_packing_date: ManufacturePackingDateField;
  mrp: MaximumRetailPriceField;
  consumer_care: ConsumerCareField;
  country_of_origin: CountryOfOriginField;
}

export interface StructuredDeclarationResult {
  id: string;
  evidence_id: string;
  inspection_id: string;
  ocr_result_id: string;
  provider: string;
  model_name: string;
  model_version?: string;
  prompt_version: string;
  extraction_version: string;
  extraction_status: string;
  processing_blocked: boolean;
  block_reason?: string;
  declarations: StructuredDeclarations;
  created_at: string;
  updated_at: string;
}

export interface EvidenceAsset {
  id: string;
  inspection_id: string;
  evidence_type: EvidenceType;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  storage_path: string;
  is_immutable: boolean;
  uploaded_by_id: string;
  created_at: string;
  quality_assessment?: ImageQualityAssessment;
  ocr_result?: OCRResult;
  structured_declarations?: StructuredDeclarationResult;
}


export interface InspectionCase {
  id: string;
  case_number: string;
  status: InspectionLifecycleState;
  processing_state: ProcessingState;
  finalization_status: FinalizationStatus;
  product_name: string;
  origin_status: OriginStatus;
  product_category?: string;
  reference_url?: string;
  notes?: string;
  created_by_id: string;
  reviewer_id?: string;
  created_by?: User;
  reviewer?: User;
  evidence_assets: EvidenceAsset[];
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  finalized_at?: string;
}

export interface InspectionCreatePayload {
  product_name: string;
  origin_status: OriginStatus;
  product_category?: string;
  reference_url?: string;
  notes?: string;
}

export interface InspectionListResponse {
  items: InspectionCase[];
  total: number;
}

export type ApplicabilityStatus = 'APPLICABLE' | 'NOT_APPLICABLE' | 'REQUIRES_REVIEW';

export interface ApplicabilityItem {
  id: string;
  inspection_id: string;
  requirement_name: string;
  status: ApplicabilityStatus;
  basis: string;
  rule_citation: string;
  context_used: Record<string, any>;
  rule_set_id: string;
  rule_set_version: string;
  evaluation_version: string;
  created_at: string;
  updated_at: string;
}

export interface ApplicabilityListResponse {
  inspection_id: string;
  items: ApplicabilityItem[];
  rule_set_id: string;
  rule_set_version: string;
  evaluation_version: string;
}

export interface ComplianceFinding {
  id: string;
  inspection_id: string;
  evidence_id?: string;
  ocr_result_id?: string;
  structured_declaration_result_id?: string;
  requirement_name: string;
  result: ComplianceResult;
  reason: string;
  applicability_status: ApplicabilityStatus;
  rule_citation: string;
  rule_set_id: string;
  rule_set_version: string;
  evaluation_version: string;
  source_token_indices: number[];
  metadata_payload: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ComplianceEvaluationSummary {
  inspection_id: string;
  rule_set_id: string;
  rule_set_version: string;
  evaluation_version: string;
  findings: ComplianceFinding[];
  total_findings: number;
  summary_counts: Record<string, number>;
}

export type EvidenceRequestStatus = 'OPEN' | 'FULFILLED' | 'CANCELLED';

export type ReviewerDeterminationType =
  | 'CONFIRMED'
  | 'OVERRIDDEN'
  | 'REVISION_REQUESTED'
  | 'EVIDENCE_REQUESTED';

export type FinalDecision =
  | 'COMPLIANT'
  | 'NON_COMPLIANT_CONFIRMED'
  | 'INCONCLUSIVE';

export interface DeclarationCorrection {
  id: string;
  inspection_id: string;
  evidence_id?: string;
  rule_citation?: string;
  field_name: string;
  previous_value?: any;
  corrected_value: any;
  correction_reason: string;
  created_by_id?: string;
  created_at: string;
}

export interface ManualObservation {
  id: string;
  inspection_id: string;
  requirement_domain: string;
  observation_text: string;
  created_by_id?: string;
  created_at: string;
}

export interface VerificationState {
  inspection_id: string;
  status: string;
  is_ready_for_submission: boolean;
  blocking_reasons: string[];
  corrections: DeclarationCorrection[];
  manual_observations: ManualObservation[];
}

export interface ReviewerDecision {
  id: string;
  inspection_id: string;
  finding_id?: string;
  requirement_name: string;
  reviewer_id: string;
  determination?: ReviewerDeterminationType;
  original_result?: string;
  adjudicated_result: ComplianceResult;
  is_override: boolean;
  rationale: string;
  rule_set_id: string;
  rule_set_version: string;
  evaluation_version: string;
  created_at: string;
  updated_at?: string;
}

export interface EvidenceRequest {
  id: string;
  request_id: string;
  inspection_id: string;
  reviewer_id: string;
  requirement_name: string;
  request_reason: string;
  requested_condition?: string;
  requested_evidence_type?: string;
  status: EvidenceRequestStatus;
  response_evidence_id?: string;
  response_note?: string;
  resolved_by_id?: string;
  resolved_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface FinalAuditRecord {
  id: string;
  inspection_id: string;
  finalized_by_id: string;
  finalized_at: string;
  final_decision: FinalDecision;
  final_rationale: string;
  inspection_context_snapshot: Record<string, any>;
  evidence_snapshot: Array<Record<string, any>>;
  declaration_snapshot: Record<string, any>;
  applicability_snapshot: Array<Record<string, any>>;
  compliance_findings_snapshot: Array<Record<string, any>>;
  reviewer_decisions_snapshot: Array<Record<string, any>>;
  rule_set_id: string;
  rule_set_version: string;
  evaluation_version: string;
  source_evidence_hashes: Record<string, string>;
  audit_metadata: Record<string, any>;
  created_at: string;
}

export interface ReviewQueueItem {
  id: string;
  case_number: string;
  product_name: string;
  origin_status: OriginStatus;
  product_category?: string;
  status: InspectionLifecycleState;
  finalization_status?: string;
  created_by_id: string;
  inspector_name?: string;
  created_at: string;
  submitted_at?: string;
  findings_count?: number;
  summary_counts?: Record<string, number>;
  potential_violations_count?: number;
  open_evidence_requests_count: number;
}

// ── Phase 5 Types ────────────────────────────────────────────────────────────

export interface InspectionSearchResultItem {
  id: string;
  case_number: string;
  status: InspectionLifecycleState;
  processing_state: ProcessingState;
  finalization_status: FinalizationStatus;
  product_name: string;
  origin_status: OriginStatus;
  product_category?: string;
  created_by_id: string;
  reviewer_id?: string;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  finalized_at?: string;
  final_decision?: FinalDecision;
  evidence_count: number;
}

export interface InspectionSearchResponse {
  items: InspectionSearchResultItem[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface InspectionSearchParams {
  q?: string;
  category?: string;
  status?: string;
  compliance?: string;
  origin?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface GovernanceMetrics {
  avg_review_turnaround_seconds?: number | null;
  revision_count: number;
  correction_count: number;
  override_count: number;
}

export interface DashboardMetricsResponse {
  date_range: string;
  category?: string | null;
  total_inspections: number;
  total_finalized: number;
  active_inspections: number;
  in_verification_count: number;
  submitted_for_review_count: number;
  requires_revision_count: number;
  compliance_rate_percent: number;
  status_counts: Record<string, number>;
  compliance_distribution: Record<string, number>;
  origin_distribution: Record<string, number>;
  rule_violation_counts: Record<string, number>;
  governance_metrics: GovernanceMetrics;
}
