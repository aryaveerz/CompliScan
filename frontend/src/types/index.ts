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
