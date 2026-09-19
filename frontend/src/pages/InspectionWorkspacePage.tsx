import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Trash2,
  ExternalLink,
  Shield,
  History,
  Edit3,
  Save,
  X,
  Crosshair,
  AlertTriangle,
  FileSpreadsheet,
  CornerUpLeft,
  ChevronDown,
  ChevronUp,
  Info,
  Lock,
  Sparkles,
  FileCheck,
  FileQuestion,
  Scale,
  Camera,
} from 'lucide-react';
import {
  InspectionCase,
  OriginStatus,
  InspectionLifecycleState,
  ExtractedDeclarationItem,
  AuditEventItem,
  ComplianceResult,
  BoundingBox,
  ImageQualityAssessment,
  OCRResult,
  StructuredDeclarationResult,
  ApplicabilityItem,
  ComplianceEvaluationSummary,
  ComplianceFinding,
  VerificationState,
  ReviewerDecision,
  EvidenceRequest,
  FinalAuditRecord,
  FinalDecision,
} from '../types';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatusBadge, OriginBadge, ComplianceBadge } from '../components/StatusBadge';
import { InspectorVerificationSection } from '../components/InspectorVerificationSection';
import { ReviewerGovernanceSection } from '../components/ReviewerGovernanceSection';
import { EvidenceRequestsSection } from '../components/EvidenceRequestsSection';
import { FinalRecordSection } from '../components/FinalRecordSection';
import {
  DeclarationCorrectionModal,
  ManualObservationModal,
  SubmitForReviewModal,
  ReviewerAdjudicationModal,
  CreateEvidenceRequestModal,
  FulfillEvidenceRequestModal,
  RequestRevisionModal,
  FinalizeInspectionModal,
} from '../components/Phase4Modals';
import { CameraCapture } from '../components/CameraCapture';

// Initial statutory declarations under Legal Metrology (Packaged Commodities) Rules, 2011
// Separates the Six Core Universal MVP Checks (Rule 6(1)(a)-(f)) from the Conditional Check (Rule 6(1)(da))
const buildUniversalDeclarations = (primaryEvidenceId?: string): ExtractedDeclarationItem[] => [
  {
    id: 'dec-1',
    rule_citation: 'Rule 6(1)(a)',
    declaration_name: 'Name & Address of Manufacturer / Packer / Importer',
    extracted_value: 'Apex Consumer Goods Ltd., Plot 42, Industrial Area Phase II, Bengaluru 560058',
    result: 'PASS',
    applicability: 'Universal — Mandatory for all pre-packaged commodities',
    is_applicable: true,
    evidence_id: primaryEvidenceId,
    bounding_box: { x: 14, y: 18, width: 72, height: 11 },
    verified_value: 'Apex Consumer Goods Ltd., Plot 42, Industrial Area Phase II, Bengaluru 560058',
    inspector_notes: 'Full manufacturer postal address verified against factory registration.',
    reviewer_override: false,
  },
  {
    id: 'dec-2',
    rule_citation: 'Rule 6(1)(b)',
    declaration_name: 'Generic or Common Name of Commodity',
    extracted_value: 'Refined Sunflower Cooking Oil',
    result: 'PASS',
    applicability: 'Universal — Mandatory for all pre-packaged commodities',
    is_applicable: true,
    evidence_id: primaryEvidenceId,
    bounding_box: { x: 20, y: 32, width: 60, height: 8 },
    verified_value: 'Refined Sunflower Cooking Oil',
    inspector_notes: 'Standard generic nomenclature used on principal display panel.',
    reviewer_override: false,
  },
  {
    id: 'dec-3',
    rule_citation: 'Rule 6(1)(c)',
    declaration_name: 'Net Quantity in Standard Units of Weight / Measure',
    extracted_value: '1 L (910 g at 30°C)',
    result: 'PASS',
    applicability: 'Universal — Mandatory for all pre-packaged commodities (Rule 11/12 compliant units)',
    is_applicable: true,
    evidence_id: primaryEvidenceId,
    bounding_box: { x: 24, y: 44, width: 52, height: 7 },
    verified_value: '1 L',
    inspector_notes: 'Unit symbol complies with Second Schedule; font height exceeds minimum 4mm.',
    reviewer_override: false,
  },
  {
    id: 'dec-4',
    rule_citation: 'Rule 6(1)(d)',
    declaration_name: 'Month & Year of Manufacture / Pre-packing / Import',
    extracted_value: 'PKD 08/2026',
    result: 'PASS',
    applicability: 'Universal — Mandatory for all pre-packaged commodities',
    is_applicable: true,
    evidence_id: primaryEvidenceId,
    bounding_box: { x: 28, y: 54, width: 44, height: 6 },
    verified_value: '08/2026',
    inspector_notes: 'Legible month and year format.',
    reviewer_override: false,
  },
  {
    id: 'dec-5',
    rule_citation: 'Rule 6(1)(e)',
    declaration_name: 'Maximum Retail Price (MRP inclusive of all taxes)',
    extracted_value: 'MRP Rs 185.00 (Incl. of all taxes)',
    result: 'POTENTIAL_NON_COMPLIANCE', // Automated warning: Rarity of Red Rule - warm ochre/amber, never red
    applicability: 'Universal — Mandatory for all retail pre-packaged commodities',
    is_applicable: true,
    evidence_id: primaryEvidenceId,
    bounding_box: { x: 22, y: 63, width: 56, height: 8 },
    verified_value: 'MRP Rs 185.00 (Incl. of all taxes)',
    inspector_notes: 'Currency symbol formatting requires inspection for mandatory Indian Rupee symbol adherence.',
    reviewer_override: false,
  },
  {
    id: 'dec-6',
    rule_citation: 'Rule 6(1)(f)',
    declaration_name: 'Consumer Care Contact Details (Name, Tel, Email)',
    extracted_value: 'Consumer Support: apexcare@apexconsumer.in | Toll-Free: 1800-425-0199',
    result: 'PASS',
    applicability: 'Universal — Mandatory for all pre-packaged commodities',
    is_applicable: true,
    evidence_id: primaryEvidenceId,
    bounding_box: { x: 16, y: 74, width: 68, height: 9 },
    verified_value: 'apexcare@apexconsumer.in | 1800-425-0199',
    inspector_notes: 'Designated helpline and electronic mail address functional.',
    reviewer_override: false,
  },
];

// Country of Origin under Rule 6(1)(da) (inserted via G.S.R. 629(E) in 2017)
// Strictly applicability-driven: applies ONLY to imported commodities.
const buildConditionalCOO = (
  originStatus: OriginStatus,
  primaryEvidenceId?: string
): ExtractedDeclarationItem => {
  if (originStatus === 'IMPORTED') {
    return {
      id: 'dec-coo',
      rule_citation: 'Rule 6(1)(da)',
      declaration_name: 'Country of Origin or Manufacture (Imported Commodities)',
      extracted_value: 'Country of Origin: Vietnam',
      result: 'PASS',
      applicability: 'Applicable — Mandatory for imported products under Rule 6(1)(da) (G.S.R. 629(E))',
      is_applicable: true,
      evidence_id: primaryEvidenceId,
      bounding_box: { x: 30, y: 85, width: 40, height: 6 },
      verified_value: 'Vietnam',
      inspector_notes: 'Country of origin explicitly declared on principal display panel for imported commodity.',
      reviewer_override: false,
    };
  }

  if (originStatus === 'DOMESTIC') {
    return {
      id: 'dec-coo',
      rule_citation: 'Rule 6(1)(da)',
      declaration_name: 'Country of Origin or Manufacture (Imported Commodities)',
      extracted_value: 'Statutory Exemption: Domestic Commodity (No physical label COO mandate)',
      result: 'NOT_APPLICABLE',
      applicability: 'Not Applicable — Domestic commodities have no statutory COO mandate on physical labels under LMPC',
      is_applicable: false,
      evidence_id: undefined,
      bounding_box: undefined,
      verified_value: undefined,
      inspector_notes: 'Statutory exemption confirmed: Manufactured and packed domestically in India.',
      reviewer_override: false,
    };
  }

  // UNKNOWN origin status
  return {
    id: 'dec-coo',
    rule_citation: 'Rule 6(1)(da)',
    declaration_name: 'Country of Origin or Manufacture (Imported Commodities)',
    extracted_value: 'Origin indeterminate — Cannot evaluate Rule 6(1)(da) applicability',
    result: 'REQUIRES_REVIEW',
    applicability: 'Indeterminate — Rule 6(1)(da) applicability requires established origin status (Imported vs Domestic)',
    is_applicable: false,
    evidence_id: undefined,
    bounding_box: undefined,
    verified_value: undefined,
    inspector_notes: 'Action Required: Inspecting officer must establish package origin to resolve Rule 6(1)(da) applicability.',
    reviewer_override: false,
  };
};

// Regulatory audit log structured detail formatter (Converts raw event payloads into human-readable regulatory records)
interface StructuredAuditDetail {
  summary: string;
  metadata: Array<{ label: string; value: string }>;
}

const formatAuditRecord = (eventType: string, details?: Record<string, any>): StructuredAuditDetail => {
  if (!details || Object.keys(details).length === 0) {
    return {
      summary: 'Regulatory lifecycle event logged in immutable system ledger.',
      metadata: [],
    };
  }

  switch (eventType) {
    case 'INSPECTION_CREATED':
      return {
        summary: `Inspection docket opened for commodity "${details.product_name || 'Pre-packaged Commodity'}".`,
        metadata: [
          { label: 'Case Number', value: details.case_number || '—' },
          { label: 'Origin Status', value: details.origin_status || 'UNKNOWN' },
        ],
      };

    case 'EVIDENCE_UPLOADED':
      return {
        summary: `Packaging evidence asset registered: ${details.original_filename || details.filename || 'Evidence File'}.`,
        metadata: [
          ...(details.evidence_id ? [{ label: 'Evidence ID', value: details.evidence_id }] : []),
          ...(details.sha256_hash ? [{ label: 'SHA-256 Digest', value: `${details.sha256_hash.slice(0, 16)}...` }] : []),
          ...(details.file_size_bytes ? [{ label: 'File Size', value: `${(details.file_size_bytes / 1024).toFixed(1)} KB` }] : []),
        ],
      };

    case 'EVIDENCE_DELETED':
      return {
        summary: `Draft packaging evidence asset purged from inspection docket.`,
        metadata: [
          ...(details.evidence_id ? [{ label: 'Evidence Asset ID', value: details.evidence_id }] : []),
        ],
      };

    case 'PRODUCT_CONTEXT_UPDATED':
      return {
        summary: `Inspection commodity metadata and origin baseline updated.`,
        metadata: [
          ...(details.product_name ? [{ label: 'Commodity', value: details.product_name }] : []),
          ...(details.origin_status ? [{ label: 'Origin Status', value: details.origin_status }] : []),
          ...(details.product_category ? [{ label: 'Category', value: details.product_category }] : []),
        ],
      };

    case 'REVIEWER_DETERMINATION':
      return {
        summary: `Reviewer statutory adjudication recorded for ${details.rule_citation || 'Statutory Requirement'}. Result modified: ${details.prior_result || 'ORIGINAL'} → ${details.new_result || 'OVERRIDDEN'}.`,
        metadata: [
          ...(details.recorded_justification ? [{ label: 'Recorded Justification', value: `"${details.recorded_justification}"` }] : []),
          ...(details.rule_citation ? [{ label: 'Rule Citation', value: details.rule_citation }] : []),
        ],
      };

    case 'STATUS_TRANSITION':
      return {
        summary: `Docket lifecycle transitioned: ${details.prior_state || 'prior'} → ${details.new_state || 'next'}.`,
        metadata: [
          ...(details.prior_state ? [{ label: 'Prior State', value: details.prior_state }] : []),
          ...(details.new_state ? [{ label: 'New State', value: details.new_state }] : []),
        ],
      };

    case 'DECLARATION_CORRECTED':
      return {
        summary: `Inspector observation value amended for ${details.rule_citation || 'Statutory Rule'}.`,
        metadata: [
          ...(details.corrected_value ? [{ label: 'Verified Value', value: details.corrected_value }] : []),
          ...(details.inspector_notes ? [{ label: 'Inspector Note', value: details.inspector_notes }] : []),
        ],
      };

    default: {
      const entries = Object.entries(details).map(([k, v]) => ({
        label: k.replace(/_/g, ' ').toUpperCase(),
        value: typeof v === 'object' && v !== null ? Object.entries(v).map(([sk, sv]) => `${sk}: ${sv}`).join(', ') : String(v),
      }));
      return {
        summary: `Regulatory event recorded for classification ${eventType.replace(/_/g, ' ')}.`,
        metadata: entries,
      };
    }
  }
};

export const InspectionWorkspacePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [inspection, setInspection] = useState<InspectionCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Authorization check: Reviewer role has statutory override rights
  const isReviewer = user?.role === 'REVIEWER';

  // Active evidence asset for canvas viewport
  const [activeAssetId, setActiveAssetId] = useState<string | null>(null);

  // Declarations state: 6 universal checks + 1 conditional COO check
  const [universalDeclarations, setUniversalDeclarations] = useState<ExtractedDeclarationItem[]>([]);
  const [cooDeclaration, setCooDeclaration] = useState<ExtractedDeclarationItem | null>(null);
  const [selectedDeclarationId, setSelectedDeclarationId] = useState<string | null>(null);
  const [expandedDeclarationId, setExpandedDeclarationId] = useState<string | null>(null);

  // Active view tab in right pane
  const [activeTab, setActiveTab] = useState<
    'findings' | 'verification' | 'reviewer' | 'evidence_requests' | 'applicability' | 'final_record' | 'audit'
  >('findings');

  // Phase 4 — Governance & Verification states
  const [verificationState, setVerificationState] = useState<VerificationState | null>(null);
  const [reviewerDecisions, setReviewerDecisions] = useState<ReviewerDecision[]>([]);
  const [evidenceRequests, setEvidenceRequests] = useState<EvidenceRequest[]>([]);
  const [finalRecord, setFinalRecord] = useState<FinalAuditRecord | null>(null);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [isDownloadingDocx, setIsDownloadingDocx] = useState(false);

  // Modals state
  const [showCorrectionModal, setShowCorrectionModal] = useState(false);
  const [showObservationModal, setShowObservationModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showAdjudicationModal, setShowAdjudicationModal] = useState(false);
  const [adjudicationFinding, setAdjudicationFinding] = useState<ComplianceFinding | null>(null);
  const [showCreateERModal, setShowCreateERModal] = useState(false);
  const [showFulfillERModal, setShowFulfillERModal] = useState(false);
  const [targetER, setTargetER] = useState<EvidenceRequest | null>(null);
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [showFinalizeModal, setShowFinalizeModal] = useState(false);

  // Canvas zoom & pan state
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const viewportRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Clipboard copy state for SHA-256 hash
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Progressive disclosure states for reduced cognitive load
  const [showDocketDetails, setShowDocketDetails] = useState(false);
  const [showFullLifecycle, setShowFullLifecycle] = useState(false);
  const [showEvidenceMetadata, setShowEvidenceMetadata] = useState(false);
  const [expandedAuditIds, setExpandedAuditIds] = useState<Record<string, boolean>>({});

  // Inline context editing state
  const [isEditingContext, setIsEditingContext] = useState(false);
  const [editProductName, setEditProductName] = useState('');
  const [editOriginStatus, setEditOriginStatus] = useState<OriginStatus>('UNKNOWN');
  const [editProductCategory, setEditProductCategory] = useState('');
  const [editReferenceUrl, setEditReferenceUrl] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [isSavingContext, setIsSavingContext] = useState(false);

  // Uploading state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [cameraSupported, setCameraSupported] = useState(false);

  // Docked Reviewer Adjudication Drawer state
  const [adjudicationTarget, setAdjudicationTarget] = useState<ExtractedDeclarationItem | null>(null);
  const [overrideNewResult, setOverrideNewResult] = useState<ComplianceResult>('PASS');
  const [overrideJustification, setOverrideJustification] = useState('');
  const [overrideError, setOverrideError] = useState<string | null>(null);

  // Audit trail state
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);

  // Technical Image Quality Screening state
  const [qualityAssessment, setQualityAssessment] = useState<ImageQualityAssessment | null>(null);
  const [isReassessingQuality, setIsReassessingQuality] = useState(false);

  // Technical OCR Perception state
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null);
  const [isProcessingOCR, setIsProcessingOCR] = useState(false);
  const [showTokensList, setShowTokensList] = useState(false);

  // Semantic Declaration Extraction state (Gemini 2.5 Flash)
  const [structuredDeclarations, setStructuredDeclarations] = useState<StructuredDeclarationResult | null>(null);
  const [isExtractingDeclarations, setIsExtractingDeclarations] = useState(false);

  // Phase 3 — Applicability & Deterministic Compliance state
  const [applicabilityList, setApplicabilityList] = useState<ApplicabilityItem[]>([]);
  const [complianceSummary, setComplianceSummary] = useState<ComplianceEvaluationSummary | null>(null);
  const [isEvaluatingCompliance, setIsEvaluatingCompliance] = useState(false);

  // Fetch compliance data
  const fetchComplianceData = async (inspectionId: string) => {
    try {
      const [appData, findData] = await Promise.all([
        api.getInspectionApplicability(inspectionId).catch(() => null),
        api.getInspectionFindings(inspectionId).catch(() => null),
      ]);
      if (appData) setApplicabilityList(appData.items);
      if (findData) setComplianceSummary(findData);
    } catch {
      // Ignored
    }
  };

  // Fetch Phase 4 data
  const fetchPhase4Data = async (inspectionId: string) => {
    try {
      const [vState, rDecs, evReqs, fRec] = await Promise.all([
        api.getVerificationState(inspectionId).catch(() => null),
        api.getReviewerDecisions(inspectionId).catch(() => []),
        api.getEvidenceRequests(inspectionId).catch(() => []),
        api.getFinalAuditRecord(inspectionId).catch(() => null),
      ]);
      if (vState) setVerificationState(vState);
      if (rDecs) setReviewerDecisions(rDecs);
      if (evReqs) setEvidenceRequests(evReqs);
      if (fRec) setFinalRecord(fRec);
    } catch {
      // Ignored
    }
  };

  const handleSaveCorrection = async (
    field_name: string,
    rule_citation: string,
    previous_value: string,
    corrected_value: string,
    reason: string
  ) => {
    if (!inspection) return;
    await api.recordDeclarationCorrection(inspection.id, {
      field_name,
      rule_citation,
      previous_value,
      corrected_value,
      correction_reason: reason,
    });
    await fetchPhase4Data(inspection.id);
  };

  const handleSaveObservation = async (requirement_domain: string, observation_text: string) => {
    if (!inspection) return;
    await api.recordManualObservation(inspection.id, {
      requirement_domain,
      observation_text,
    });
    await fetchPhase4Data(inspection.id);
  };

  const handleSubmitForReview = async () => {
    if (!inspection) return;
    const updated = await api.submitInspectionForReview(inspection.id);
    setInspection(updated);
    await fetchPhase4Data(inspection.id);
  };

  const handleRecordReviewerDecision = async (
    requirement_name: string,
    adjudicated_result: ComplianceResult,
    is_override: boolean,
    rationale: string
  ) => {
    if (!inspection) return;
    await api.recordReviewerDecision(inspection.id, {
      requirement_name,
      adjudicated_result,
      is_override,
      rationale,
    });
    await fetchPhase4Data(inspection.id);
  };

  const handleCreateEvidenceRequest = async (
    requirement_name: string,
    request_reason: string,
    requested_condition?: string,
    requested_evidence_type?: string
  ) => {
    if (!inspection) return;
    await api.createEvidenceRequest(inspection.id, {
      requirement_name,
      request_reason,
      requested_condition,
      requested_evidence_type,
    });
    await fetchPhase4Data(inspection.id);
  };

  const handleFulfillEvidenceRequest = async (
    erId: string,
    evidenceAssetId?: string,
    responseNote?: string
  ) => {
    if (!inspection) return;
    await api.fulfillEvidenceRequest(erId, evidenceAssetId, responseNote);
    await fetchPhase4Data(inspection.id);
  };

  const handleRequestRevision = async (reason: string, requested_changes?: string) => {
    if (!inspection) return;
    const updated = await api.requestInspectionRevision(inspection.id, {
      reason,
      requested_changes,
    });
    setInspection(updated);
    await fetchPhase4Data(inspection.id);
  };

  const handleFinalizeInspection = async (final_decision: FinalDecision, final_rationale: string) => {
    if (!inspection) return;
    const rec = await api.finalizeInspection(inspection.id, {
      final_decision,
      final_rationale,
    });
    setFinalRecord(rec);
    setInspection((prev) => (prev ? { ...prev, status: 'FINALIZED', finalization_status: 'READ_ONLY' } : null));
    await fetchPhase4Data(inspection.id);
    setActiveTab('final_record');
  };

  const handleDownloadPdfReport = async () => {
    if (!inspection) return;
    try {
      setIsDownloadingPdf(true);
      await api.downloadFinalPdfReport(inspection.id, inspection.case_number);
    } catch (err: any) {
      alert(err.message || 'Failed to download PDF report');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const handleDownloadDocxReport = async () => {
    if (!inspection) return;
    try {
      setIsDownloadingDocx(true);
      await api.downloadFinalDocxReport(inspection.id, inspection.case_number);
    } catch (err: any) {
      alert(err.message || 'Failed to download DOCX report');
    } finally {
      setIsDownloadingDocx(false);
    }
  };

  const handleEvaluateCompliance = async () => {
    if (!inspection) return;
    try {
      setIsEvaluatingCompliance(true);
      const res = await api.evaluateInspectionCompliance(inspection.id, false);
      setComplianceSummary(res);
      await fetchComplianceData(inspection.id);
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate compliance');
    } finally {
      setIsEvaluatingCompliance(false);
    }
  };

  // Fetch initial inspection data
  const fetchInspection = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await api.getInspection(id);
      setInspection(data);
      fetchComplianceData(data.id);
      fetchPhase4Data(data.id);

      // Set initial active asset
      if (data.evidence_assets.length > 0) {
        setActiveAssetId(data.evidence_assets[0].id);
      }

      // Initialize the Six Core Universal Declarations
      const primaryAsset = data.evidence_assets[0];
      setUniversalDeclarations(buildUniversalDeclarations(primaryAsset?.id));

      // Initialize the Applicability-Driven Conditional Rule 6(1)(da) Country of Origin
      setCooDeclaration(buildConditionalCOO(data.origin_status, primaryAsset?.id));

      // Build initial audit events log
      const initialAuditLogs: AuditEventItem[] = [
        {
          id: `AUD-INIT-${data.id.slice(-6)}`,
          inspection_id: data.id,
          actor_id: data.created_by_id,
          actor_role: 'Inspecting Officer',
          event_type: 'INSPECTION_CREATED',
          details: {
            case_number: data.case_number,
            product_name: data.product_name,
            origin_status: data.origin_status,
          },
          created_at: data.created_at,
        },
      ];

      data.evidence_assets.forEach((asset, idx) => {
        initialAuditLogs.push({
          id: `AUD-EV-${asset.id.slice(-6)}-${idx}`,
          inspection_id: data.id,
          actor_id: asset.uploaded_by_id,
          actor_role: 'Inspecting Officer',
          event_type: 'EVIDENCE_UPLOADED',
          details: {
            evidence_id: asset.id,
            original_filename: asset.original_filename,
            sha256_hash: asset.sha256_hash,
            file_size_bytes: asset.file_size_bytes,
          },
          created_at: asset.created_at,
        });
      });

      setAuditEvents(initialAuditLogs);

      // Initialize edit fields
      setEditProductName(data.product_name);
      setEditOriginStatus(data.origin_status);
      setEditProductCategory(data.product_category || '');
      setEditReferenceUrl(data.reference_url || '');
      setEditNotes(data.notes || '');
    } catch (err: any) {
      setError(err.message || 'Failed to load inspection case');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspection();
  }, [id]);

  // Detect camera hardware / getUserMedia support
  useEffect(() => {
    setCameraSupported(Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
  }, []);

  // Global Keyboard Accelerators for power-user inspection ergonomics
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (adjudicationTarget) {
          setAdjudicationTarget(null);
        } else if (showDocketDetails) {
          setShowDocketDetails(false);
        } else if (expandedDeclarationId) {
          setExpandedDeclarationId(null);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [adjudicationTarget, showDocketDetails, expandedDeclarationId]);

  // Combined list of all current declarations (6 core + 1 conditional COO)
  const allDeclarations = useMemo(() => {
    if (!cooDeclaration) return universalDeclarations;
    return [...universalDeclarations, cooDeclaration];
  }, [universalDeclarations, cooDeclaration]);

  // Consolidated findings summary dynamically derived from live declarations
  const findingsSummary = useMemo(() => {
    const counts = {
      pass: 0,
      potentialNonCompliance: 0,
      requiresReview: 0,
      notApplicable: 0,
      incomplete: 0,
      processingFailed: 0,
      confirmedViolation: 0,
    };
    allDeclarations.forEach((d) => {
      switch (d.result) {
        case 'PASS':
          counts.pass++;
          break;
        case 'POTENTIAL_NON_COMPLIANCE':
          counts.potentialNonCompliance++;
          break;
        case 'REQUIRES_REVIEW':
          counts.requiresReview++;
          break;
        case 'NOT_APPLICABLE':
          counts.notApplicable++;
          break;
        case 'INCOMPLETE':
          counts.incomplete++;
          break;
        case 'PROCESSING_FAILED':
          counts.processingFailed++;
          break;
        case 'CONFIRMED_VIOLATION':
          counts.confirmedViolation++;
          break;
      }
    });
    return counts;
  }, [allDeclarations]);

  // Active asset object
  const activeAsset = useMemo(() => {
    if (!inspection || !activeAssetId) return null;
    return inspection.evidence_assets.find((a) => a.id === activeAssetId) || inspection.evidence_assets[0] || null;
  }, [inspection, activeAssetId]);

  // Fetch or sync Image Quality Assessment, OCR Result, and Declarations when active asset changes
  useEffect(() => {
    if (!activeAsset?.id) {
      setQualityAssessment(null);
      setOcrResult(null);
      setStructuredDeclarations(null);
      return;
    }
    if (activeAsset.quality_assessment) {
      setQualityAssessment(activeAsset.quality_assessment);
    } else {
      api.getEvidenceQuality(activeAsset.id)
        .then((qa) => setQualityAssessment(qa))
        .catch(() => setQualityAssessment(null));
    }

    if (activeAsset.ocr_result) {
      setOcrResult(activeAsset.ocr_result);
    } else {
      api.getEvidenceOCR(activeAsset.id)
        .then((ocr) => setOcrResult(ocr))
        .catch(() => setOcrResult(null));
    }

    if (activeAsset.structured_declarations) {
      setStructuredDeclarations(activeAsset.structured_declarations);
    } else {
      api.getEvidenceDeclarations(activeAsset.id)
        .then((dec) => setStructuredDeclarations(dec))
        .catch(() => setStructuredDeclarations(null));
    }
  }, [activeAsset?.id]);

  // Trigger manual quality re-screening asynchronously
  const handleTriggerQualityAssessment = async () => {
    if (!activeAsset) return;
    try {
      setIsReassessingQuality(true);
      await api.triggerQualityAssessment(activeAsset.id);
      setTimeout(async () => {
        try {
          const qa = await api.getEvidenceQuality(activeAsset.id);
          setQualityAssessment(qa);
        } catch {
          // Keep prior state
        }
        setIsReassessingQuality(false);
      }, 1500);
    } catch {
      setIsReassessingQuality(false);
    }
  };

  // Trigger manual OCR perception asynchronously
  const handleTriggerOCR = async () => {
    if (!activeAsset) return;
    try {
      setIsProcessingOCR(true);
      await api.triggerOCRProcessing(activeAsset.id);
      setTimeout(async () => {
        try {
          const ocr = await api.getEvidenceOCR(activeAsset.id);
          setOcrResult(ocr);
        } catch {
          // Keep prior state
        }
        setIsProcessingOCR(false);
      }, 1500);
    } catch {
      setIsProcessingOCR(false);
    }
  };

  // Trigger manual semantic declaration extraction asynchronously
  const handleTriggerExtraction = async () => {
    if (!activeAsset) return;
    try {
      setIsExtractingDeclarations(true);
      await api.triggerDeclarationExtraction(activeAsset.id);
      setTimeout(async () => {
        try {
          const dec = await api.getEvidenceDeclarations(activeAsset.id);
          setStructuredDeclarations(dec);
        } catch {
          // Keep prior state
        }
        setIsExtractingDeclarations(false);
      }, 1500);
    } catch {
      setIsExtractingDeclarations(false);
    }
  };


  // Evidence upload handler (accepts FileList from file input or File[] from camera capture)
  const handleUploadFiles = async (files: FileList | null | File[]) => {
    if (!files || (Array.isArray(files) ? files.length === 0 : files.length === 0) || !inspection) return;
    setUploadError(null);
    setIsUploading(true);

    const fileList = Array.isArray(files) ? files : Array.from(files);
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      try {
        const newAsset = await api.uploadEvidence(inspection.id, file, 'PRIMARY');
        setInspection((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            status: 'EVIDENCE_UPLOADED',
            evidence_assets: [...prev.evidence_assets, newAsset],
          };
        });
        setActiveAssetId(newAsset.id);

        // Record audit event
        const newAuditItem: AuditEventItem = {
          id: `AUD-EV-${newAsset.id.slice(-6)}`,
          inspection_id: inspection.id,
          actor_role: 'Inspecting Officer',
          event_type: 'EVIDENCE_UPLOADED',
          details: {
            evidence_id: newAsset.id,
            original_filename: newAsset.original_filename,
            sha256_hash: newAsset.sha256_hash,
            file_size_bytes: newAsset.file_size_bytes,
          },
          created_at: new Date().toISOString(),
        };
        setAuditEvents((prev) => [newAuditItem, ...prev]);
      } catch (err: any) {
        setUploadError(err.message || `Failed to upload ${file.name}`);
      }
    }
    setIsUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Evidence delete handler
  const handleDeleteEvidence = async (evidenceId: string) => {
    if (!inspection) return;
    if (!window.confirm('Are you sure you want to remove this draft evidence asset from formal inspection records?')) return;

    try {
      await api.deleteEvidence(inspection.id, evidenceId);
      setInspection((prev) => {
        if (!prev) return prev;
        const updated = prev.evidence_assets.filter((a) => a.id !== evidenceId);
        return { ...prev, evidence_assets: updated };
      });
      if (activeAssetId === evidenceId) {
        const remaining = inspection.evidence_assets.filter((a) => a.id !== evidenceId);
        setActiveAssetId(remaining.length > 0 ? remaining[0].id : null);
      }

      // Record audit event
      const newAuditItem: AuditEventItem = {
        id: `AUD-DEL-${evidenceId.slice(-6)}`,
        inspection_id: inspection.id,
        actor_role: 'Inspecting Officer',
        event_type: 'EVIDENCE_DELETED',
        details: { evidence_id: evidenceId },
        created_at: new Date().toISOString(),
      };
      setAuditEvents((prev) => [newAuditItem, ...prev]);
    } catch (err: any) {
      alert(err.message || 'Failed to delete evidence');
    }
  };

  // Save product context
  const handleSaveContext = async () => {
    if (!inspection) return;
    if (!editProductName.trim()) {
      alert('Product Name is mandatory and cannot be blank.');
      return;
    }
    try {
      setIsSavingContext(true);
      const updated = await api.updateInspectionContext(inspection.id, {
        product_name: editProductName.trim(),
        origin_status: editOriginStatus,
        product_category: editProductCategory.trim() || undefined,
        reference_url: editReferenceUrl.trim() || undefined,
        notes: editNotes.trim() || undefined,
      });
      setInspection(updated);
      setIsEditingContext(false);

      // Re-evaluate Country of Origin applicability dynamically based on updated origin_status
      setCooDeclaration(buildConditionalCOO(updated.origin_status, activeAsset?.id));

      // Record audit event
      const auditItem: AuditEventItem = {
        id: `AUD-CTX-${Date.now().toString().slice(-6)}`,
        inspection_id: inspection.id,
        actor_role: 'Inspecting Officer',
        event_type: 'PRODUCT_CONTEXT_UPDATED',
        details: {
          product_name: updated.product_name,
          origin_status: updated.origin_status,
          product_category: updated.product_category,
        },
        created_at: new Date().toISOString(),
      };
      setAuditEvents((prev) => [auditItem, ...prev]);
    } catch (err: any) {
      alert(err.message || 'Failed to update product context');
    } finally {
      setIsSavingContext(false);
    }
  };

  // Open Docked Adjudication Drawer
  const handleOpenAdjudicationDrawer = (declaration: ExtractedDeclarationItem) => {
    setAdjudicationTarget(declaration);
    setSelectedDeclarationId(declaration.id);
    setOverrideNewResult(declaration.result === 'PASS' ? 'POTENTIAL_NON_COMPLIANCE' : 'PASS');
    setOverrideJustification('');
    setOverrideError(null);
  };

  // Submit Reviewer Decision / Assessment Override with mandatory recorded justification
  const handleSubmitReviewerOverride = () => {
    if (!adjudicationTarget || !inspection) return;

    if (!overrideJustification.trim() || overrideJustification.trim().length < 10) {
      setOverrideError('Mandatory recorded justification is required (minimum 10 characters) to record statutory override.');
      return;
    }

    if (adjudicationTarget.id === 'dec-coo') {
      setCooDeclaration((prev) =>
        prev
          ? {
              ...prev,
              result: overrideNewResult,
              reviewer_override: true,
              reviewer_justification: overrideJustification.trim(),
            }
          : null
      );
    } else {
      setUniversalDeclarations((prev) =>
        prev.map((item) => {
          if (item.id === adjudicationTarget.id) {
            return {
              ...item,
              result: overrideNewResult,
              reviewer_override: true,
              reviewer_justification: overrideJustification.trim(),
            };
          }
          return item;
        })
      );
    }

    // Record formal audit event
    const auditItem: AuditEventItem = {
      id: `AUD-REV-${Date.now().toString().slice(-6)}`,
      inspection_id: inspection.id,
      actor_role: 'Reviewing Officer',
      event_type: 'REVIEWER_DETERMINATION',
      details: {
        rule_citation: adjudicationTarget.rule_citation,
        declaration_name: adjudicationTarget.declaration_name,
        prior_result: adjudicationTarget.result,
        new_result: overrideNewResult,
        recorded_justification: overrideJustification.trim(),
      },
      created_at: new Date().toISOString(),
    };
    setAuditEvents((prev) => [auditItem, ...prev]);

    setAdjudicationTarget(null);
  };

  // Cross-reference handler: click declaration row -> focus & synchronize bounding box on left
  const handleSelectDeclaration = (decId: string) => {
    setSelectedDeclarationId((prev) => {
      const next = prev === decId ? null : decId;
      if (next) {
        const target = allDeclarations.find((d) => d.id === next);
        if (target?.bounding_box) {
          if (zoomLevel <= 1) {
            setZoomLevel(1.25);
          }
        }
      }
      return next;
    });
  };

  // Toggle single row expansion (Only 1 row expanded at a time to prevent visual maze)
  const handleToggleRowExpand = (decId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    handleSelectDeclaration(decId);
    setExpandedDeclarationId((prev) => (prev === decId ? null : decId));
  };

  // Pan and zoom canvas handlers
  const handleZoomIn = () => setZoomLevel((z) => Math.min(z + 0.25, 4));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(z - 0.25, 0.5));
  const handleResetZoom = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    setPanStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning) return;
    setPanOffset({
      x: e.clientX - panStart.x,
      y: e.clientY - panStart.y,
    });
  };

  const handleMouseUp = () => setIsPanning(false);

  const copyHashToClipboard = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  // Ordered statutory lifecycle states
  const lifecycleOrderedStates: InspectionLifecycleState[] = [
    'DRAFT',
    'EVIDENCE_UPLOADED',
    'EXTRACTED',
    'APPLICABILITY_EVALUATED',
    'EVALUATED',
    'IN_VERIFICATION',
    'SUBMITTED_FOR_REVIEW',
    'FINALIZED',
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-8">
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-xs flex items-center space-x-3 text-slate-700 text-sm font-medium">
          <div className="w-4 h-4 border-2 border-slate-400 border-t-emerald-600 rounded-full animate-spin"></div>
          <span>Loading Legal Metrology Inspection Workspace...</span>
        </div>
      </div>
    );
  }

  if (error || !inspection) {
    return (
      <div className="min-h-screen bg-slate-50 p-8 flex items-center justify-center">
        <div className="max-w-md w-full bg-white border border-slate-200 rounded-lg p-6 shadow-xs space-y-4">
          <div className="flex items-center space-x-2 text-rose-700 font-semibold text-sm">
            <AlertCircle className="w-5 h-5" />
            <span>Inspection Docket Unavailable</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">{error || 'Inspection case could not be located.'}</p>
          <Link
            to="/inspections"
            className="inline-flex items-center space-x-1 text-xs font-semibold text-emerald-700 hover:text-emerald-800 hover:underline"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to Inspection List</span>
          </Link>
        </div>
      </div>
    );
  }

  const isFinalized = inspection.finalization_status === 'READ_ONLY';
  const isRequiresRevision = inspection.status === 'REQUIRES_REVISION';
  const currentLifecycleIndex = lifecycleOrderedStates.indexOf(inspection.status);

  // Helper row renderer for 5-column statutory matrix table (Target: rapid scanning, progressive disclosure)
  const renderTableRow = (dec: ExtractedDeclarationItem, isConditional = false) => {
    const isSelected = selectedDeclarationId === dec.id;
    const isExpanded = expandedDeclarationId === dec.id;
    const hasBoundingBox = Boolean(dec.bounding_box);

    return (
      <React.Fragment key={dec.id}>
        <tr
          onClick={() => handleSelectDeclaration(dec.id)}
          className={`cursor-pointer transition-colors border-b border-slate-200 h-10 ${
            isSelected
              ? 'bg-sky-50 font-medium'
              : isConditional
              ? 'bg-amber-50/20 hover:bg-amber-50/40'
              : 'hover:bg-slate-50/70'
          }`}
        >
          {/* 1. Rule Citation */}
          <td className="py-2.5 px-3 whitespace-nowrap">
            <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-300">
              {dec.rule_citation}
            </span>
          </td>

          {/* 2. Statutory Requirement */}
          <td className="py-2.5 px-3 min-w-[170px]">
            <div className="text-xs font-semibold text-slate-900 leading-tight">
              {dec.declaration_name}
            </div>
          </td>

          {/* 3. Observed / Extracted Value */}
          <td className="py-2.5 px-3 min-w-[170px]">
            <div className="text-xs font-mono text-slate-800 line-clamp-1 leading-tight" title={dec.extracted_value}>
              {dec.extracted_value}
            </div>
          </td>

          {/* 4. Result */}
          <td className="py-2.5 px-3 whitespace-nowrap">
            <div className="flex items-center space-x-1.5">
              <ComplianceBadge result={dec.result} />
              {dec.reviewer_override && (
                <span className="text-[9px] font-mono px-1 py-0.2 bg-amber-50 text-amber-900 border border-amber-300 rounded font-bold">
                  OVERRIDDEN
                </span>
              )}
            </div>
          </td>

          {/* 5. Action / Expand */}
          <td className="py-2.5 px-3 whitespace-nowrap text-right">
            <div className="flex items-center justify-end space-x-1.5">
              {/* Evidence Coordinate Shortcut */}
              {hasBoundingBox && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSelectDeclaration(dec.id);
                  }}
                  className={`text-[10px] font-mono px-1.5 py-0.5 rounded flex items-center space-x-0.5 transition-colors ${
                    isSelected
                      ? 'bg-blue-700 text-white font-semibold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
                  }`}
                  title="Target coordinate on evidence canvas"
                >
                  <Crosshair className="w-2.5 h-2.5" />
                  <span>[{dec.bounding_box?.x}%, {dec.bounding_box?.y}%]</span>
                </button>
              )}

              {/* Reviewer Override Trigger */}
              {!isFinalized && (
                <>
                  {isReviewer || !user ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenAdjudicationDrawer(dec);
                      }}
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded border transition-colors flex items-center space-x-1 shadow-2xs ${
                        adjudicationTarget?.id === dec.id
                          ? 'bg-slate-900 text-white border-slate-900'
                          : 'bg-white hover:bg-slate-100 text-slate-800 border-slate-300'
                      }`}
                      title="Open Reviewer Adjudication Drawer"
                    >
                      <Edit3 className="w-3 h-3 text-slate-500" />
                      <span>Override</span>
                    </button>
                  ) : (
                    <span
                      className="text-[10px] text-slate-500 flex items-center space-x-0.5"
                      title="Reviewer authorization required under Legal Metrology rules"
                    >
                      <Lock className="w-2.5 h-2.5" />
                      <span>Reviewer</span>
                    </span>
                  )}
                </>
              )}

              {/* Progressive Disclosure Expand Button */}
              <button
                onClick={(e) => handleToggleRowExpand(dec.id, e)}
                aria-expanded={isExpanded}
                aria-label={isExpanded ? `Collapse inspection observation notes for ${dec.rule_citation}` : `Expand inspection observation notes for ${dec.rule_citation}`}
                className="p-1 text-slate-500 hover:text-slate-800 rounded hover:bg-slate-100 transition-colors flex items-center space-x-0.5"
                title={isExpanded ? 'Collapse inline details' : 'Expand inline verification area'}
              >
                <span className="text-[11px] font-medium hidden sm:inline">{isExpanded ? 'Hide' : 'Inspect'}</span>
                {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>
          </td>
        </tr>

        {/* Detailed Inspection Surface via Progressive Disclosure (Single-row expansion) */}
        {isExpanded && (
          <tr className="bg-slate-50/90 border-b border-slate-200 text-xs">
            <td colSpan={5} className="px-4 py-3">
              <div className="bg-white rounded-lg border border-slate-200 p-3.5 space-y-3 shadow-xs">
                {/* Statutory Requirement Header */}
                <div className="flex flex-wrap items-start justify-between gap-2 pb-2.5 border-b border-slate-100">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-slate-800 px-1.5 py-0.5 bg-slate-100 rounded border border-slate-300">
                        {dec.rule_citation}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900 font-sans">
                        {dec.declaration_name}
                      </h4>
                    </div>
                    <p className="text-[11px] text-slate-600 mt-1 font-sans">
                      <strong className="text-slate-500 font-medium">Statutory Scope: </strong>
                      {dec.applicability}
                    </p>
                  </div>

                  {hasBoundingBox && (
                    <button
                      onClick={() => handleSelectDeclaration(dec.id)}
                      className="text-[11px] px-2.5 py-1 rounded bg-blue-50 text-blue-800 border border-blue-200 hover:bg-blue-100 transition-colors flex items-center space-x-1.5 font-sans font-medium"
                      title="Synchronize and focus evidence bounding box on canvas"
                    >
                      <Crosshair className="w-3.5 h-3.5 text-blue-600" />
                      <span>Focus on Evidence Canvas</span>
                    </button>
                  )}
                </div>

                {/* Role-Aware Inspection & Review Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-sans">
                  {/* Left: Inspector Observations & Extraction Evidence */}
                  <div className="space-y-2 p-2.5 bg-slate-50 rounded-md border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block">
                      INSPECTOR VERIFICATION DETAILS
                    </span>
                    <div>
                      <span className="text-slate-500 text-[11px] block">Extracted Observed Value:</span>
                      <p className="text-slate-900 font-mono text-xs font-semibold mt-0.5">{dec.extracted_value}</p>
                    </div>
                    <div>
                      <span className="text-slate-500 text-[11px] block">Verified Value:</span>
                      <p className="text-slate-800 font-medium text-xs mt-0.5">
                        {dec.verified_value || 'Pending affirmative inspector sign-off'}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-500 text-[11px] block">Inspector Statutory Notes:</span>
                      <p className="text-slate-700 text-xs mt-0.5 leading-relaxed">
                        {dec.inspector_notes || 'No inspector observation notes recorded.'}
                      </p>
                    </div>
                  </div>

                  {/* Right: Regulatory Assessment & Reviewer Determination */}
                  <div className="space-y-2 p-2.5 bg-slate-50 rounded-md border border-slate-200">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                        REGULATORY COMPLIANCE STATUS
                      </span>
                      <ComplianceBadge result={dec.result} />
                    </div>

                    {dec.reviewer_justification ? (
                      <div className="mt-2 p-2 bg-white rounded border border-amber-200 text-xs">
                        <span className="text-[10px] uppercase font-bold text-amber-900 block">
                          Recorded Reviewer Justification (Statutory Override)
                        </span>
                        <p className="text-slate-900 text-xs mt-0.5 leading-relaxed">
                          {dec.reviewer_justification}
                        </p>
                      </div>
                    ) : (
                      <p className="text-slate-600 text-xs mt-1 leading-relaxed">
                        {dec.result === 'PASS'
                          ? 'Automated inspection model identified complete statutory declaration in compliance with Rule parameters.'
                          : dec.result === 'POTENTIAL_NON_COMPLIANCE'
                          ? 'Declaration observed with deviations from legal metrology specifications requiring officer adjudication.'
                          : 'Applicability or declaration completeness requires manual verification.'}
                      </p>
                    )}

                    {!isFinalized && (
                      <div className="pt-2 border-t border-slate-200 flex items-center justify-end">
                        {isReviewer || !user ? (
                          <button
                            onClick={() => handleOpenAdjudicationDrawer(dec)}
                            className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-semibold shadow-xs flex items-center space-x-1.5 transition-colors"
                          >
                            <Edit3 className="w-3 h-3 text-slate-400" />
                            <span>Adjudicate / Override</span>
                          </button>
                        ) : (
                          <span className="text-[11px] text-slate-500 flex items-center space-x-1" title="Reviewer authorization required under Legal Metrology rules">
                            <Lock className="w-3 h-3 text-slate-400" />
                            <span>Reviewing Officer Determination Required</span>
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </td>
          </tr>
        )}
      </React.Fragment>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Header & Context Docket Bar: Reduced Cognitive Load */}
      <header className="bg-white border-b border-slate-200 px-4 sm:px-6 py-2.5 sticky top-0 z-30 shadow-xs">
        <div className="max-w-full mx-auto flex flex-col md:flex-row md:items-center justify-between gap-2.5">
          {/* Primary Case Visual Anchor */}
          <div className="flex items-center space-x-3 min-w-0">
            <Link
              to="/inspections"
              className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors shrink-0"
              title="Return to Inspection Docket"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>

            <div className="h-6 w-px bg-slate-200 shrink-0"></div>

            <div className="min-w-0">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-300 shrink-0">
                  {inspection.case_number}
                </span>
                <StatusBadge status={inspection.status} />
                {isFinalized && (
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-300">
                    READ-ONLY RECORD
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2 mt-0.5">
                <h1 className="text-sm sm:text-base font-bold text-slate-900 truncate tracking-tight">
                  {inspection.product_name}
                </h1>
                {/* Secondary Docket Details Trigger */}
                <button
                  onClick={() => setShowDocketDetails(!showDocketDetails)}
                  aria-expanded={showDocketDetails}
                  aria-controls="docket-details-panel"
                  className="text-xs text-slate-500 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded px-1.5 py-0.5 flex items-center space-x-1 font-medium transition-colors"
                  title="Toggle docket metadata details"
                >
                  <Info className="w-3 h-3" />
                  <span>Details</span>
                  {showDocketDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
                {!isFinalized && (
                  <button
                    onClick={() => setIsEditingContext(!isEditingContext)}
                    className="text-xs text-slate-400 hover:text-slate-700 transition-colors p-1"
                    title="Edit Product Context"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Subordinate Secondary Metadata: Plain Typography (No competing badges) */}
          <div className="hidden lg:flex items-center space-x-4 text-xs text-slate-500 shrink-0">
            <div className="flex items-center space-x-1.5">
              <OriginBadge origin={inspection.origin_status} />
              <span className="text-slate-700 font-medium">
                {inspection.product_category || 'General Package'}
              </span>
            </div>
            <div className="h-4 w-px bg-slate-200" />
            <div>
              <span className="text-slate-400">Inspector: </span>
              <strong className="text-slate-700 font-medium">
                {inspection.created_by?.full_name ? 'Assigned Officer' : 'Inspecting Officer'}
              </strong>
            </div>
            <div>
              <span className="text-slate-400">Reviewer: </span>
              <strong className="text-slate-700 font-medium">
                {inspection.reviewer?.full_name ? 'Assigned Reviewer' : 'Reviewing Officer'}
              </strong>
            </div>
            <div className="flex items-center space-x-1 text-slate-400">
              <Calendar className="w-3 h-3" />
              <span>{new Date(inspection.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        {/* Compact Docket Details Panel */}
        {showDocketDetails && (
          <div
            id="docket-details-panel"
            className="mt-2.5 py-2 px-3 bg-slate-50 border border-slate-200 rounded-md text-xs grid grid-cols-1 sm:grid-cols-3 gap-3"
          >
            <div>
              <span className="text-slate-500 font-medium text-[11px] block">REFERENCE URL</span>
              {inspection.reference_url ? (
                <a
                  href={inspection.reference_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-emerald-700 hover:underline inline-flex items-center space-x-0.5 truncate max-w-full font-mono text-[11px]"
                >
                  <span className="truncate">{inspection.reference_url}</span>
                  <ExternalLink className="w-3 h-3 shrink-0 ml-0.5" />
                </a>
              ) : (
                <span className="text-slate-400">None recorded</span>
              )}
            </div>
            <div>
              <span className="text-slate-500 font-medium text-[11px] block">COMMODITY NOTES</span>
              <span className="text-slate-700">{inspection.notes || 'None recorded'}</span>
            </div>
            <div>
              <span className="text-slate-500 font-medium text-[11px] block">EVIDENCE REGISTRY</span>
              <span className="text-slate-700">
                {inspection.evidence_assets.length} file(s) registered
              </span>
            </div>
          </div>
        )}

        {/* Quiet, Compact Dynamic Lifecycle Representation */}
        <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-3 min-w-0">
            {/* Dynamic Current State Indicator */}
            {isRequiresRevision ? (
              <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-bold bg-orange-50 text-orange-800 border border-orange-300">
                <CornerUpLeft className="w-3 h-3" />
                <span>ACTION REQUIRED: REQUIRES REVISION</span>
              </span>
            ) : (
              <div className="flex items-center space-x-1.5 shrink-0">
                <span className="text-[11px] text-slate-500 font-medium">
                  {currentLifecycleIndex >= 0 ? `Stage ${currentLifecycleIndex + 1} of ${lifecycleOrderedStates.length}:` : 'Status:'}
                </span>
                <span className="text-[11px] font-bold text-slate-900 uppercase">
                  {inspection.status.replace(/_/g, ' ')}
                </span>
              </div>
            )}

            {/* Segmented Progress Track (8 subtle indicators) */}
            <div className="hidden sm:flex items-center space-x-1 w-44">
              {lifecycleOrderedStates.map((st, i) => {
                const isDone = currentLifecycleIndex > i && !isRequiresRevision;
                const isNow = inspection.status === st;
                return (
                  <div
                    key={st}
                    title={`${i + 1}. ${st.replace(/_/g, ' ')}`}
                    className={`h-1.5 flex-1 rounded-full transition-colors ${
                      isNow
                        ? 'bg-slate-900'
                        : isDone
                        ? 'bg-emerald-600'
                        : 'bg-slate-200'
                    }`}
                  />
                );
              })}
            </div>

            <button
              onClick={() => setShowFullLifecycle(!showFullLifecycle)}
              className="text-[11px] text-slate-400 hover:text-slate-700 transition-colors underline font-sans"
            >
              {showFullLifecycle ? 'Hide Lifecycle Steps' : 'View All Steps'}
            </button>
          </div>

          <div className="text-[11px] text-slate-500 shrink-0">
            {isFinalized ? (
              <span className="text-slate-600 font-medium flex items-center space-x-1">
                <Lock className="w-3 h-3" />
                <span>Finalized Read-Only Record</span>
              </span>
            ) : isReviewer ? (
              <span className="text-slate-700 font-medium">
                Reviewer Adjudication Surface
              </span>
            ) : (
              <span className="text-slate-600">
                Inspector Verification Surface
              </span>
            )}
          </div>
        </div>

        {/* Full Lifecycle Steps (When explicitly requested) */}
        {showFullLifecycle && (
          <div className="mt-2 py-1.5 px-2 bg-slate-50 border border-slate-200 rounded text-xs flex items-center space-x-1 overflow-x-auto cleanroom-scrollbar">
            {lifecycleOrderedStates.map((st, idx) => {
              const isCurrent = inspection.status === st;
              const isPast = currentLifecycleIndex > idx && !isRequiresRevision;

              return (
                <React.Fragment key={st}>
                  <div
                    className={`flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono whitespace-nowrap ${
                      isCurrent
                        ? 'bg-slate-900 text-white font-bold'
                        : isPast
                        ? 'text-emerald-800 bg-emerald-50 border border-emerald-200 font-medium'
                        : 'text-slate-400 bg-white border border-slate-200'
                    }`}
                  >
                    {isPast ? <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" /> : null}
                    <span>{st.replace(/_/g, ' ')}</span>
                  </div>
                  {idx < lifecycleOrderedStates.length - 1 && (
                    <span className="text-slate-300 text-[9px]">→</span>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        )}

        {/* Inline Context Edit Drawer */}
        {isEditingContext && (
          <div className="mt-3 p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider font-sans">
                Update Inspection Product Context
              </h2>
              <button
                onClick={() => setIsEditingContext(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-sans">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Product Name *</label>
                <input
                  type="text"
                  value={editProductName}
                  onChange={(e) => setEditProductName(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-emerald-600"
                />
              </div>
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Origin Status</label>
                <select
                  value={editOriginStatus}
                  onChange={(e) => setEditOriginStatus(e.target.value as OriginStatus)}
                  className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-emerald-600"
                >
                  <option value="DOMESTIC">DOMESTIC (Indian Manufacture)</option>
                  <option value="IMPORTED">IMPORTED (Foreign Import)</option>
                  <option value="UNKNOWN">UNKNOWN</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Category</label>
                <input
                  type="text"
                  value={editProductCategory}
                  onChange={(e) => setEditProductCategory(e.target.value)}
                  placeholder="e.g. Edible Oils, Cosmetics"
                  className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-emerald-600"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-slate-700 font-semibold mb-1">E-Commerce / Reference URL</label>
                <input
                  type="url"
                  value={editReferenceUrl}
                  onChange={(e) => setEditReferenceUrl(e.target.value)}
                  placeholder="https://example.com/product/..."
                  className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-emerald-600 font-mono text-[11px]"
                />
              </div>
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Inspector Notes</label>
                <input
                  type="text"
                  value={editNotes}
                  onChange={(e) => setEditNotes(e.target.value)}
                  placeholder="Batch, MRP stamp observation"
                  className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-emerald-600"
                />
              </div>
            </div>
            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                onClick={() => setIsEditingContext(false)}
                className="px-3 py-1 text-xs border border-slate-300 rounded-md text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveContext}
                disabled={isSavingContext}
                className="px-3 py-1 text-xs bg-emerald-700 hover:bg-emerald-800 text-white rounded-md font-medium flex items-center space-x-1 disabled:opacity-50 shadow-xs"
              >
                <Save className="w-3.5 h-3.5" />
                <span>{isSavingContext ? 'Saving...' : 'Save Context'}</span>
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Main Workspace Split: Left (Forensic Evidence) / Right (Declaration Matrix & Ledger) */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 min-h-0 bg-slate-100 gap-px">
        {/* Left Pane (5 Columns): Focused Forensic Evidence Viewport */}
        <section
          aria-label="Forensic Evidence Workspace"
          className="lg:col-span-5 bg-white flex flex-col border-r border-slate-200 overflow-hidden"
        >
          {/* Evidence Canvas Header */}
          <div className="px-4 py-2 bg-slate-50 border-b border-slate-200 flex items-center justify-between shrink-0">
            <div className="flex items-center space-x-2">
              <Crosshair className="w-4 h-4 text-slate-700" />
              <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wide font-sans">
                Primary Visual Evidence
              </h2>
            </div>

            {/* Compact Viewport Pan/Zoom Controls */}
            <div className="flex items-center space-x-1">
              <button
                onClick={handleZoomIn}
                className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 border border-slate-300 transition-colors"
                title="Zoom In (+25%)"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 border border-slate-300 transition-colors"
                title="Zoom Out (-25%)"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleResetZoom}
                className="p-1 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 border border-slate-300 transition-colors"
                title="Reset Zoom (1:1)"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <span className="text-[11px] font-mono text-slate-500 px-1">
                {Math.round(zoomLevel * 100)}%
              </span>
            </div>
          </div>

          {/* Interactive Evidence Canvas Viewport */}
          <div
            ref={viewportRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            className={`flex-1 relative bg-slate-900 overflow-hidden flex items-center justify-center select-none ${
              isPanning ? 'cursor-grabbing' : 'cursor-grab'
            }`}
            style={{ minHeight: '380px' }}
          >
            {activeAsset ? (
              <div
                className="relative transition-transform duration-75"
                style={{
                  transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                  transformOrigin: 'center center',
                }}
              >
                <img
                  src={api.getEvidenceDownloadUrl(activeAsset.id)}
                  alt={activeAsset.original_filename}
                  className="max-h-[520px] max-w-full object-contain pointer-events-none rounded border border-slate-800 shadow-md"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />

                {/* Vector Bounding Box Overlay for Extracted Declarations */}
                <svg
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  viewBox="0 0 100 100"
                  preserveAspectRatio="none"
                >
                  {allDeclarations
                    .filter((dec) => dec.bounding_box && (!dec.evidence_id || dec.evidence_id === activeAsset.id))
                    .map((dec) => {
                      const box = dec.bounding_box as BoundingBox;
                      const isSelected = selectedDeclarationId === dec.id;
                      const isWarning = dec.result === 'POTENTIAL_NON_COMPLIANCE';
                      const strokeColor = isSelected
                        ? '#2563eb' // Sovereign Blue when selected
                        : isWarning
                        ? '#ea580c' // Warm ochre for potential non-compliance
                        : '#16a34a'; // Restrained green for pass

                      return (
                        <g key={dec.id} className="pointer-events-auto cursor-pointer">
                          <rect
                            x={`${box.x}%`}
                            y={`${box.y}%`}
                            width={`${box.width}%`}
                            height={`${box.height}%`}
                            fill={isSelected ? 'rgba(37, 99, 235, 0.15)' : 'rgba(22, 163, 74, 0.05)'}
                            stroke={strokeColor}
                            strokeWidth={isSelected ? '0.8' : '0.5'}
                            strokeDasharray={isSelected ? 'none' : '1.5 0.5'}
                            onClick={() => handleSelectDeclaration(dec.id)}
                          />
                          <text
                            x={`${box.x + 1}%`}
                            y={`${box.y - 1.5}%`}
                            fill={strokeColor}
                            fontSize="2.5"
                            fontFamily="JetBrains Mono, monospace"
                            fontWeight="bold"
                            onClick={() => handleSelectDeclaration(dec.id)}
                          >
                            {dec.rule_citation}
                          </text>
                        </g>
                      );
                    })}
                </svg>
              </div>
            ) : (
              /* Calm, Institutional Empty State (No AI illustrations) */
              <div className="text-center p-8 bg-slate-100/60 max-w-sm rounded-lg border border-slate-200">
                <Crosshair className="w-10 h-10 mx-auto mb-2 text-slate-400" />
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide font-sans">
                  No Packaging Evidence Registered
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Upload packaging photographs or scans of the principal display panel to begin statutory extraction.
                </p>
                {!isFinalized && (
                  <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-600 text-white rounded-md text-xs font-semibold shadow-xs transition-colors"
                    >
                      Upload Packaging Evidence
                    </button>
                    {cameraSupported && (
                      <button
                        onClick={() => setShowCamera(true)}
                        className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-semibold shadow-xs flex items-center space-x-1.5 transition-colors border border-slate-700"
                        title="Capture photograph using mobile / device camera"
                      >
                        <Camera className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Capture Photo</span>
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Evidence Asset Carousel / Strip */}
          <div className="px-3 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-2 shrink-0">
            <div className="flex items-center space-x-2 overflow-x-auto py-1">
              {inspection.evidence_assets.map((asset, idx) => (
                <button
                  key={asset.id}
                  onClick={() => setActiveAssetId(asset.id)}
                  className={`px-2.5 py-1 text-xs rounded border transition-colors shrink-0 flex items-center space-x-1.5 ${
                    activeAssetId === asset.id
                      ? 'bg-white border-slate-900 text-slate-900 font-bold shadow-xs'
                      : 'bg-white border-slate-200 text-slate-600 hover:border-slate-400'
                  }`}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                  <span>
                    Asset #{idx + 1} ({asset.evidence_type})
                  </span>
                </button>
              ))}

              {!isFinalized && (
                <div className="flex items-center space-x-1.5 shrink-0">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="px-2.5 py-1 text-xs border border-dashed border-slate-300 rounded text-slate-600 hover:text-slate-900 hover:border-slate-500 font-medium shrink-0 flex items-center space-x-1"
                  >
                    <span>+ Add Image</span>
                  </button>
                  {cameraSupported && (
                    <button
                      onClick={() => setShowCamera(true)}
                      disabled={isUploading}
                      className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-white rounded font-medium shrink-0 flex items-center space-x-1 transition-colors"
                      title="Capture photo using device camera"
                    >
                      <Camera className="w-3 h-3 text-emerald-400" />
                      <span>Capture</span>
                    </button>
                  )}
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => handleUploadFiles(e.target.files)}
              className="hidden"
            />
          </div>

          {uploadError && (
            <div className="px-3 py-1.5 bg-rose-50 border-t border-rose-200 text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          {/* Progressive Disclosure for SHA-256 and Technical Metadata */}
          {activeAsset && (
            <div className="border-t border-slate-200 bg-white shrink-0">
              <button
                onClick={() => setShowEvidenceMetadata(!showEvidenceMetadata)}
                className="w-full px-3 py-1.5 text-[11px] text-slate-500 hover:text-slate-800 bg-slate-50 flex items-center justify-between transition-colors border-b border-slate-200"
              >
                <span className="font-medium flex items-center space-x-1.5">
                  <Shield className="w-3.5 h-3.5 text-slate-400" />
                  <span>Technical Evidence Integrity & SHA-256</span>
                </span>
                <span className="flex items-center space-x-1 text-slate-400 font-sans">
                  <span>{showEvidenceMetadata ? 'Hide Details' : 'Show Details'}</span>
                  {showEvidenceMetadata ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </span>
              </button>

              {showEvidenceMetadata && (
                <div className="p-3 text-xs space-y-2 bg-slate-50/50">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-500">Asset: <strong className="font-mono text-slate-800">{activeAsset.id}</strong></span>
                    <span className="text-slate-500">{activeAsset.mime_type} • {formatBytes(activeAsset.file_size_bytes)}</span>
                    {!isFinalized && (
                      <button
                        onClick={() => handleDeleteEvidence(activeAsset.id)}
                        className="text-rose-700 hover:text-rose-800 text-[11px] font-semibold flex items-center space-x-0.5"
                        title="Remove unfinalized evidence draft"
                      >
                        <Trash2 className="w-3 h-3" />
                        <span>Remove</span>
                      </button>
                    )}
                  </div>

                  <div className="p-2 bg-white rounded border border-slate-200 text-[11px]">
                    <div className="flex items-center justify-between text-slate-500 text-[10px] mb-0.5">
                      <span className="font-semibold">SHA-256 INTEGRITY DIGEST</span>
                      <button
                        onClick={() => copyHashToClipboard(activeAsset.sha256_hash)}
                        className="text-emerald-700 hover:underline flex items-center space-x-1 font-sans"
                      >
                        {copiedHash === activeAsset.sha256_hash ? (
                          <>
                            <Check className="w-3 h-3" />
                            <span>Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy Hash</span>
                          </>
                        )}
                      </button>
                    </div>
                    <div className="font-mono text-[10px] text-slate-800 break-all select-all leading-tight">
                      {activeAsset.sha256_hash}
                    </div>
                  </div>

                  {/* Technical Evidence Quality Screening */}
                  <div className="p-2.5 bg-white rounded border border-slate-200 text-[11px] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700 text-[10px] tracking-wider uppercase">
                        Technical Quality Screening
                      </span>
                      {qualityAssessment ? (
                        <span
                          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border ${
                            qualityAssessment.quality_status === 'USABLE'
                              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                              : qualityAssessment.quality_status === 'NEEDS_REVIEW'
                              ? 'bg-amber-50 text-amber-800 border-amber-300'
                              : 'bg-rose-50 text-rose-800 border-rose-300'
                          }`}
                        >
                          <span className="w-1.5 h-1.5 mr-1 rounded-full bg-current opacity-75" />
                          {qualityAssessment.quality_status.replace(/_/g, ' ')}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Screening pending…</span>
                      )}
                    </div>

                    {qualityAssessment && (
                      <div className="space-y-1.5 text-slate-600">
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[10px] font-mono bg-slate-50 p-2 rounded border border-slate-100">
                          <div>
                            <span className="text-slate-400 block font-sans">Resolution</span>
                            <span className="font-semibold text-slate-800">{qualityAssessment.width} × {qualityAssessment.height}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans">Sharpness</span>
                            <span className="font-semibold text-slate-800">{qualityAssessment.sharpness_score ?? '—'}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans">Brightness</span>
                            <span className="font-semibold text-slate-800">{qualityAssessment.brightness_score ?? '—'}</span>
                          </div>
                        </div>

                        {qualityAssessment.reason_codes.length > 0 && qualityAssessment.reason_codes[0] !== 'QUALITY_ACCEPTABLE' && (
                          <div className="flex flex-wrap gap-1 pt-1">
                            {qualityAssessment.reason_codes.map((code) => (
                              <span
                                key={code}
                                className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-amber-50 text-amber-800 border border-amber-200"
                              >
                                {code.replace(/_/g, ' ')}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px]">
                      <p className="text-slate-400 italic leading-snug">
                        Engineering screening signal for perception usability — not a compliance finding.
                      </p>
                      {!isFinalized && (
                        <button
                          onClick={handleTriggerQualityAssessment}
                          disabled={isReassessingQuality}
                          className="text-slate-600 hover:text-slate-900 font-medium underline shrink-0 ml-2 disabled:opacity-50"
                        >
                          {isReassessingQuality ? 'Screening…' : 'Re-screen'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Technical Perception — OCR */}
                  <div className="p-2.5 bg-white rounded border border-slate-200 text-[11px] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700 text-[10px] tracking-wider uppercase">
                        Technical Perception — OCR
                      </span>
                      {ocrResult ? (
                        <span
                          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border ${
                            ocrResult.processing_blocked
                              ? 'bg-amber-50 text-amber-800 border-amber-300'
                              : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          }`}
                        >
                          <span className="w-1.5 h-1.5 mr-1 rounded-full bg-current opacity-75" />
                          {ocrResult.processing_blocked ? `BLOCKED (${ocrResult.block_reason})` : 'COMPLETED'}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">OCR not run / pending…</span>
                      )}
                    </div>

                    {ocrResult && (
                      <div className="space-y-1.5 text-slate-600">
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[10px] font-mono bg-slate-50 p-2 rounded border border-slate-100">
                          <div>
                            <span className="text-slate-400 block font-sans">Engine</span>
                            <span className="font-semibold text-slate-800 truncate block" title={ocrResult.ocr_engine_version}>
                              {ocrResult.ocr_engine}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans">Tokens</span>
                            <span className="font-semibold text-slate-800">{ocrResult.total_tokens}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans">Pipeline</span>
                            <span className="font-semibold text-slate-800">PP-OCRv4 (ONNX)</span>
                          </div>
                        </div>

                        {ocrResult.tokens.length > 0 && (
                          <div className="pt-1">
                            <button
                              type="button"
                              onClick={() => setShowTokensList(!showTokensList)}
                              className="text-[10px] text-indigo-600 hover:text-indigo-800 font-medium flex items-center space-x-1"
                            >
                              <span>{showTokensList ? 'Hide Detected Tokens' : `View ${ocrResult.tokens.length} Detected Tokens`}</span>
                              <span>{showTokensList ? '▲' : '▼'}</span>
                            </button>
                            {showTokensList && (
                              <div className="mt-1.5 max-h-40 overflow-y-auto space-y-1 p-1.5 bg-slate-50 rounded border border-slate-100 font-mono text-[10px]">
                                {ocrResult.tokens.map((token) => (
                                  <div key={token.token_index} className="flex justify-between items-center py-0.5 border-b border-slate-200/50 last:border-0">
                                    <span className="text-slate-800 select-all">{token.text}</span>
                                    <span className="text-slate-400 text-[9px] ml-2 shrink-0">conf: {(token.confidence * 100).toFixed(1)}%</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px]">
                      <p className="text-slate-400 italic leading-snug">
                        Raw perception tokens for downstream extraction — not a compliance finding.
                      </p>
                      {!isFinalized && (
                        <button
                          onClick={handleTriggerOCR}
                          disabled={isProcessingOCR}
                          className="text-slate-600 hover:text-slate-900 font-medium underline shrink-0 ml-2 disabled:opacity-50"
                        >
                          {isProcessingOCR ? 'Running…' : 'Run OCR'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Semantic Extraction — Structured Declarations (Gemini 2.5 Flash) */}
                  <div className="p-2.5 bg-white rounded border border-slate-200 text-[11px] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700 text-[10px] tracking-wider uppercase flex items-center space-x-1">
                        <Sparkles className="w-3 h-3 text-indigo-500" />
                        <span>Semantic Extraction — Declarations</span>
                      </span>
                      {structuredDeclarations ? (
                        <span
                          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border ${
                            structuredDeclarations.processing_blocked
                              ? 'bg-amber-50 text-amber-800 border-amber-300'
                              : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          }`}
                        >
                          <span className="w-1.5 h-1.5 mr-1 rounded-full bg-current opacity-75" />
                          {structuredDeclarations.processing_blocked
                            ? `BLOCKED (${structuredDeclarations.block_reason || 'NO TOKENS'})`
                            : structuredDeclarations.extraction_status}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Extraction pending / not run…</span>
                      )}
                    </div>

                    {structuredDeclarations && (
                      <div className="space-y-2 text-slate-600">
                        {/* Model & Version Provenance */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-[10px] font-mono bg-slate-50 p-2 rounded border border-slate-100">
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Provider</span>
                            <span className="font-semibold text-slate-800">{structuredDeclarations.provider}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Model</span>
                            <span className="font-semibold text-slate-800">{structuredDeclarations.model_name}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Prompt Ver</span>
                            <span className="font-semibold text-slate-800">{structuredDeclarations.prompt_version}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Extraction Ver</span>
                            <span className="font-semibold text-slate-800">{structuredDeclarations.extraction_version}</span>
                          </div>
                        </div>

                        {/* Domain Field Breakdown */}
                        <div className="space-y-1.5 pt-1">
                          {[
                            { label: 'Manufacturer / Packer / Importer', field: structuredDeclarations.declarations.manufacturer_identity, desc: structuredDeclarations.declarations.manufacturer_identity.name || structuredDeclarations.declarations.manufacturer_identity.raw_text },
                            { label: 'Generic / Common Commodity Name', field: structuredDeclarations.declarations.commodity_name, desc: structuredDeclarations.declarations.commodity_name.name || structuredDeclarations.declarations.commodity_name.raw_text },
                            { label: 'Net Quantity', field: structuredDeclarations.declarations.net_quantity, desc: structuredDeclarations.declarations.net_quantity.quantity_value ? `${structuredDeclarations.declarations.net_quantity.quantity_value} ${structuredDeclarations.declarations.net_quantity.unit || ''}` : structuredDeclarations.declarations.net_quantity.raw_text },
                            { label: 'Month & Year of Mfg / Pkg / Import', field: structuredDeclarations.declarations.manufacture_packing_date, desc: structuredDeclarations.declarations.manufacture_packing_date.raw_date_string || (structuredDeclarations.declarations.manufacture_packing_date.month && structuredDeclarations.declarations.manufacture_packing_date.year ? `${structuredDeclarations.declarations.manufacture_packing_date.month}/${structuredDeclarations.declarations.manufacture_packing_date.year}` : structuredDeclarations.declarations.manufacture_packing_date.raw_text) },
                            { label: 'Maximum Retail Price (MRP)', field: structuredDeclarations.declarations.mrp, desc: structuredDeclarations.declarations.mrp.amount ? `₹${structuredDeclarations.declarations.mrp.amount}` : structuredDeclarations.declarations.mrp.raw_text },
                            { label: 'Consumer Care Contact Details', field: structuredDeclarations.declarations.consumer_care, desc: [structuredDeclarations.declarations.consumer_care.phone, structuredDeclarations.declarations.consumer_care.email, structuredDeclarations.declarations.consumer_care.website].filter(Boolean).join(' • ') || structuredDeclarations.declarations.consumer_care.raw_text },
                            { label: 'Country of Origin (Physical Label)', field: structuredDeclarations.declarations.country_of_origin, desc: structuredDeclarations.declarations.country_of_origin.country_name || structuredDeclarations.declarations.country_of_origin.raw_text },
                          ].map((item, idx) => {
                            const status = item.field.status;
                            const statusColor =
                              status === 'OBSERVED'
                                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                                : status === 'CONFLICTING'
                                ? 'bg-orange-50 text-orange-800 border-orange-200'
                                : status === 'AMBIGUOUS'
                                ? 'bg-amber-50 text-amber-800 border-amber-200'
                                : status === 'UNREADABLE'
                                ? 'bg-rose-50 text-rose-800 border-rose-200'
                                : 'bg-slate-100 text-slate-500 border-slate-200';

                            return (
                              <div key={idx} className="p-1.5 bg-slate-50/70 rounded border border-slate-100 text-[10px]">
                                <div className="flex items-center justify-between gap-1">
                                  <span className="font-semibold text-slate-800 truncate">{item.label}</span>
                                  <span className={`px-1.5 py-0.2 rounded font-mono text-[9px] border ${statusColor} shrink-0`}>
                                    {status}
                                  </span>
                                </div>
                                {item.desc ? (
                                  <div className="font-mono text-slate-700 mt-0.5 select-all truncate text-[10px]">
                                    {item.desc}
                                  </div>
                                ) : (
                                  <div className="text-slate-400 italic mt-0.5 text-[9px]">
                                    {status === 'NOT_OBSERVED' ? 'Not observed on packaging' : 'No value extracted'}
                                  </div>
                                )}
                                {item.field.source_token_indices && item.field.source_token_indices.length > 0 && (
                                  <div className="flex items-center space-x-1 mt-1">
                                    <span className="text-[9px] text-slate-400">Tokens:</span>
                                    {item.field.source_token_indices.map((tIdx: number) => (
                                      <span key={tIdx} className="px-1 py-0.2 bg-indigo-50 text-indigo-700 rounded text-[8px] font-mono border border-indigo-200">
                                        #{tIdx}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px]">
                      <p className="text-slate-400 italic leading-snug">
                        Semantic structuring of observed packaging text — not a legal compliance determination.
                      </p>
                      {!isFinalized && (
                        <button
                          onClick={handleTriggerExtraction}
                          disabled={isExtractingDeclarations}
                          className="text-indigo-600 hover:text-indigo-900 font-medium underline shrink-0 ml-2 disabled:opacity-50"
                        >
                          {isExtractingDeclarations ? 'Extracting…' : structuredDeclarations ? 'Re-extract' : 'Extract Declarations'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Phase 3 — Deterministic Compliance Engine */}
                  <div className="p-2.5 bg-white rounded border border-slate-200 text-[11px] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-700 text-[10px] tracking-wider uppercase flex items-center space-x-1">
                        <Shield className="w-3 h-3 text-emerald-600" />
                        <span>Deterministic Compliance Engine</span>
                      </span>
                      {complianceSummary ? (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border bg-emerald-50 text-emerald-800 border-emerald-200">
                          <span className="w-1.5 h-1.5 mr-1 rounded-full bg-current opacity-75" />
                          EVALUATED ({complianceSummary.total_findings} Findings)
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-400">Not evaluated yet</span>
                      )}
                    </div>

                    {complianceSummary && (
                      <div className="space-y-1.5 text-slate-600">
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-[10px] font-mono bg-slate-50 p-2 rounded border border-slate-100">
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Rule Set</span>
                            <span className="font-semibold text-slate-800">{complianceSummary.rule_set_id}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Rule Version</span>
                            <span className="font-semibold text-slate-800">{complianceSummary.rule_set_version}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block font-sans text-[9px]">Eval Version</span>
                            <span className="font-semibold text-slate-800">{complianceSummary.evaluation_version}</span>
                          </div>
                        </div>

                        {/* Summary breakdown badges */}
                        <div className="flex flex-wrap gap-1 pt-1">
                          {Object.entries(complianceSummary.summary_counts).map(([res, cnt]) => (
                            <span
                              key={res}
                              className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-medium border ${
                                res === 'PASS'
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                  : res === 'POTENTIAL_NON_COMPLIANCE'
                                  ? 'bg-orange-50 text-orange-700 border-orange-200'
                                  : res === 'REQUIRES_REVIEW'
                                  ? 'bg-amber-50 text-amber-700 border-amber-200'
                                  : res === 'NOT_APPLICABLE'
                                  ? 'bg-slate-50 text-slate-600 border-slate-200'
                                  : res === 'INCOMPLETE'
                                  ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
                                  : 'bg-rose-50 text-rose-700 border-rose-200'
                              }`}
                            >
                              {cnt} {res.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px]">
                      <p className="text-slate-400 italic leading-snug">
                        Deterministic rule engine execution. AI perception never makes final legal determination.
                      </p>
                      {!isFinalized && (
                        <button
                          onClick={handleEvaluateCompliance}
                          disabled={isEvaluatingCompliance}
                          className="text-emerald-700 hover:text-emerald-900 font-medium underline shrink-0 ml-2 disabled:opacity-50"
                        >
                          {isEvaluatingCompliance ? 'Evaluating…' : complianceSummary ? 'Re-evaluate' : 'Evaluate Rules'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}


            </div>
          )}
        </section>

        {/* Right Pane (7 Columns): Structured Inspection & Adjudication Workspace */}
        <section
          aria-label="Structured Inspection and Adjudication Workspace"
          className="lg:col-span-7 bg-white flex flex-col overflow-y-auto"
        >
          {/* Navigation Tabs: Declarations Matrix vs Formal Audit Ledger */}
          <div className="px-4 border-b border-slate-200 bg-white sticky top-0 z-20 flex items-center justify-between">
            <nav className="flex space-x-6 overflow-x-auto cleanroom-scrollbar">
              <button
                onClick={() => setActiveTab('findings')}
                className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                  activeTab === 'findings'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <FileSpreadsheet className="w-4 h-4" />
                <span>DECLARATION MATRIX</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 border border-slate-200">
                  {allDeclarations.length} Rules
                </span>
              </button>

              <button
                onClick={() => setActiveTab('verification')}
                className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                  activeTab === 'verification'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <FileCheck className="w-4 h-4" />
                <span>INSPECTOR VERIFICATION</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 border border-slate-200">
                  {(verificationState?.corrections.length || 0) + (verificationState?.manual_observations.length || 0)}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('reviewer')}
                className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                  activeTab === 'reviewer'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Scale className="w-4 h-4" />
                <span>REVIEWER GOVERNANCE</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 border border-slate-200">
                  {reviewerDecisions.length} Decs
                </span>
              </button>

              <button
                onClick={() => setActiveTab('evidence_requests')}
                className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                  activeTab === 'evidence_requests'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <FileQuestion className="w-4 h-4" />
                <span>EVIDENCE REQUESTS</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 border border-slate-200">
                  {evidenceRequests.length}
                </span>
              </button>

              <button
                onClick={() => setActiveTab('applicability')}
                className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                  activeTab === 'applicability'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Shield className="w-4 h-4" />
                <span>APPLICABILITY</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 border border-slate-200">
                  {applicabilityList.length > 0 ? `${applicabilityList.length} Reqs` : '7 Reqs'}
                </span>
              </button>

              {finalRecord && (
                <button
                  onClick={() => setActiveTab('final_record')}
                  className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                    activeTab === 'final_record'
                      ? 'border-slate-900 text-slate-900'
                      : 'border-transparent text-emerald-700 hover:text-emerald-900'
                  }`}
                >
                  <Lock className="w-4 h-4" />
                  <span>FINAL RECORD</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 bg-emerald-50 text-emerald-800 rounded border border-emerald-300 font-bold">
                    IMMUTABLE
                  </span>
                </button>
              )}

              <button
                onClick={() => setActiveTab('audit')}
                className={`py-3 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors whitespace-nowrap ${
                  activeTab === 'audit'
                    ? 'border-slate-900 text-slate-900'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <History className="w-4 h-4" />
                <span>FORMAL AUDIT LEDGER</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 bg-slate-100 rounded text-slate-700 border border-slate-200">
                  {auditEvents.length}
                </span>
              </button>
            </nav>

            <div className="hidden sm:flex items-center space-x-1.5 text-[11px] text-slate-500 shrink-0 ml-4">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Evidence Traceability Synchronized</span>
            </div>
          </div>

          {/* Tab 1: High-Density Statutory Matrix & Docked Adjudication Drawer */}
          {activeTab === 'findings' && (
            <div className="p-4 space-y-3.5">
              {/* Consolidated Findings Summary Bar (Answers "What requires attention?") */}
              <div className="py-2.5 px-3 bg-slate-50 border border-slate-200 rounded-md flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center space-x-3">
                  <span className="font-semibold text-slate-800">Compliance Assessment:</span>
                  <div className="flex items-center space-x-3 text-[11px]">
                    <span className="flex items-center space-x-1 text-emerald-700 font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                      <span>{findingsSummary.pass} Compliant</span>
                    </span>

                    {findingsSummary.potentialNonCompliance > 0 && (
                      <span className="flex items-center space-x-1 text-orange-700 font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-orange-600" />
                        <span>{findingsSummary.potentialNonCompliance} Potential Non-Compliance</span>
                      </span>
                    )}

                    {findingsSummary.requiresReview > 0 && (
                      <span className="flex items-center space-x-1 text-amber-700 font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-600" />
                        <span>{findingsSummary.requiresReview} Requires Review</span>
                      </span>
                    )}

                    {findingsSummary.notApplicable > 0 && (
                      <span className="flex items-center space-x-1 text-slate-500">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                        <span>{findingsSummary.notApplicable} Not Applicable</span>
                      </span>
                    )}
                  </div>
                </div>

                <span className="text-[11px] text-slate-500">
                  {universalDeclarations.filter((d) => d.result === 'PASS').length}/6 Universal Core Passed
                </span>
              </div>

              {/* Five-Column Statutory Matrix Table */}
              <div className="border border-slate-200 rounded-lg overflow-x-auto cleanroom-scrollbar bg-white shadow-xs">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-50 text-slate-700 font-sans font-semibold text-[11px] border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3 uppercase w-24">Rule Citation</th>
                      <th className="py-2.5 px-3 uppercase min-w-[170px]">Statutory Requirement</th>
                      <th className="py-2.5 px-3 uppercase min-w-[170px]">Observed Value</th>
                      <th className="py-2.5 px-3 uppercase w-28">Result</th>
                      <th className="py-2.5 px-3 uppercase text-right w-28">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {/* Section 1: Six Core Universal Declarations */}
                    {universalDeclarations.map((dec) => renderTableRow(dec, false))}

                    {/* Section 2: Applicability-Driven Conditional Requirement (Rule 6(1)(da)) */}
                    {cooDeclaration && (
                      <>
                        <tr className="bg-slate-100/60 border-t border-b border-slate-200 text-[11px] text-slate-600 font-sans">
                          <td colSpan={5} className="py-1.5 px-3">
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-slate-700">
                                Conditional Rule: Country of Origin (Rule 6(1)(da))
                              </span>
                              <span className="text-[10px] font-mono text-slate-500">
                                {inspection.origin_status === 'IMPORTED'
                                   ? 'Origin: IMPORTED (Mandatory Declaration)'
                                  : inspection.origin_status === 'DOMESTIC'
                                  ? 'Origin: DOMESTIC (Statutorily Exempt)'
                                  : 'Origin: UNKNOWN (Verification Required)'}
                              </span>
                            </div>
                          </td>
                        </tr>
                        {renderTableRow(cooDeclaration, true)}
                      </>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Docked Reviewer Adjudication Drawer */}
              {adjudicationTarget && (
                <div className="border border-slate-300 bg-slate-50 rounded-lg p-3.5 space-y-3 shadow-xs transition-all">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                    <div className="flex items-center space-x-2">
                      <Shield className="w-4 h-4 text-slate-700" />
                      <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide font-sans">
                        REVIEWER ADJUDICATION DRAWER — {adjudicationTarget.rule_citation}: {adjudicationTarget.declaration_name}
                      </h3>
                    </div>
                    <button
                      onClick={() => setAdjudicationTarget(null)}
                      className="text-slate-400 hover:text-slate-700 p-1 rounded hover:bg-slate-200 transition-colors"
                      title="Close adjudication drawer"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-sans">
                    <div className="bg-white p-2.5 rounded-md border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase block font-semibold">
                        CURRENT AUTOMATED ASSESSMENT
                      </span>
                      <div className="mt-1 flex items-center space-x-2">
                        <ComplianceBadge result={adjudicationTarget.result} />
                        <span className="text-slate-700 text-xs truncate">
                          Observed: {adjudicationTarget.extracted_value}
                        </span>
                      </div>
                    </div>

                    <div>
                      <label className="block text-[10px] uppercase font-bold text-slate-800 mb-1">
                        OVERRIDDEN REGULATORY DETERMINATION *
                      </label>
                      <select
                        value={overrideNewResult}
                        onChange={(e) => setOverrideNewResult(e.target.value as ComplianceResult)}
                        className="w-full bg-white border border-slate-300 rounded-md px-2.5 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-slate-700"
                      >
                        <option value="PASS">PASS (Verified Statutory Compliance)</option>
                        <option value="POTENTIAL_NON_COMPLIANCE">POTENTIAL NON-COMPLIANCE (Attention Flag)</option>
                        <option value="REQUIRES_REVIEW">REQUIRES REVIEW (Ambiguous Evidence)</option>
                        <option value="CONFIRMED_VIOLATION">CONFIRMED VIOLATION (Adjudicated Breach)</option>
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <div className="flex items-center justify-between mb-1">
                        <label className="text-[10px] uppercase font-bold text-slate-800">
                          MANDATORY RECORDED JUSTIFICATION * (Minimum 10 characters)
                        </label>
                        <span className="text-[10px] font-mono text-slate-500">
                          {overrideJustification.length} / 10 min chars
                        </span>
                      </div>
                      <textarea
                        value={overrideJustification}
                        onChange={(e) => {
                          setOverrideJustification(e.target.value);
                          if (overrideError) setOverrideError(null);
                        }}
                        rows={2}
                        placeholder="State statutory legal rationale, compounding order reference, or physical inspection verification..."
                        className="w-full bg-white border border-slate-300 rounded-md p-2 text-xs text-slate-900 focus:outline-none focus:border-slate-700 font-sans"
                      />
                    </div>
                  </div>

                  {overrideError && (
                    <div className="p-2 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <span>{overrideError}</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2 border-t border-slate-200">
                    <span className="text-[11px] text-slate-500">
                      Left evidence viewport remains continuously visible for cross-examination.
                    </span>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setAdjudicationTarget(null)}
                        className="px-3 py-1.5 text-xs border border-slate-300 rounded-md text-slate-700 bg-white hover:bg-slate-100 font-medium transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleSubmitReviewerOverride}
                        className="px-3.5 py-1.5 text-xs bg-slate-900 hover:bg-slate-800 text-white rounded-md font-semibold shadow-xs transition-colors"
                      >
                        Record Adjudication
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Inspector Verification */}
          {activeTab === 'verification' && (
            <InspectorVerificationSection
              inspection={inspection}
              verificationState={verificationState}
              complianceSummary={complianceSummary}
              isReadOnly={isFinalized}
              isInspector={user?.role === 'INSPECTOR'}
              onOpenCorrectionModal={() => setShowCorrectionModal(true)}
              onOpenObservationModal={() => setShowObservationModal(true)}
              onOpenSubmitModal={() => setShowSubmitModal(true)}
            />
          )}

          {/* Tab 3: Reviewer Governance */}
          {activeTab === 'reviewer' && (
            <ReviewerGovernanceSection
              inspection={inspection}
              reviewerDecisions={reviewerDecisions}
              complianceSummary={complianceSummary}
              isReadOnly={isFinalized}
              isReviewer={user?.role === 'REVIEWER'}
              onOpenAdjudicationDrawer={(finding) => {
                setAdjudicationFinding(finding);
                setShowAdjudicationModal(true);
              }}
              onOpenFinalizeModal={() => setShowFinalizeModal(true)}
              onOpenRevisionModal={() => setShowRevisionModal(true)}
            />
          )}

          {/* Tab 4: Supplemental Evidence Requests */}
          {activeTab === 'evidence_requests' && (
            <EvidenceRequestsSection
              inspection={inspection}
              evidenceRequests={evidenceRequests}
              isReadOnly={isFinalized}
              isReviewer={user?.role === 'REVIEWER'}
              isInspector={user?.role === 'INSPECTOR'}
              onOpenCreateRequestModal={() => setShowCreateERModal(true)}
              onOpenFulfillModal={(er) => {
                setTargetER(er);
                setShowFulfillERModal(true);
              }}
            />
          )}

          {/* Tab 5: Statutory Applicability Baseline */}
          {activeTab === 'applicability' && (
            <div className="p-4 space-y-3.5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 font-sans flex items-center space-x-1.5">
                    <Shield className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Statutory Applicability Baseline (Legal Metrology Rules, 2011)</span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Deterministic evaluation of statutory requirement applicability derived from inspection product context.
                  </p>
                </div>
                <span className="text-xs font-mono text-slate-500 px-2 py-0.5 bg-slate-100 rounded border border-slate-200">
                  Snapshot: LMPC-2011-MVP-RULES v1.0
                </span>
              </div>

              {/* Applicability Table */}
              <div className="border border-slate-200 rounded-lg overflow-x-auto cleanroom-scrollbar bg-white shadow-xs">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-50 text-slate-700 font-sans font-semibold text-[11px] border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3 uppercase w-28">Rule Citation</th>
                      <th className="py-2.5 px-3 uppercase w-48">Requirement</th>
                      <th className="py-2.5 px-3 uppercase w-32">Status</th>
                      <th className="py-2.5 px-3 uppercase min-w-[260px]">Statutory Basis & Context</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-sans">
                    {applicabilityList.map((app) => {
                      const statusBadgeColor =
                        app.status === 'APPLICABLE'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : app.status === 'NOT_APPLICABLE'
                          ? 'bg-slate-100 text-slate-600 border-slate-200'
                          : 'bg-amber-50 text-amber-800 border-amber-200';

                      return (
                        <tr key={app.id || app.requirement_name} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 font-semibold align-top whitespace-nowrap">
                            {app.rule_citation}
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-slate-900 align-top">
                            {app.requirement_name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                          </td>
                          <td className="py-2.5 px-3 align-top whitespace-nowrap">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium border ${statusBadgeColor}`}>
                              <span className="w-1.5 h-1.5 mr-1 rounded-full bg-current opacity-75" />
                              {app.status.replace(/_/g, ' ')}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-slate-600 align-top space-y-1">
                            <div className="leading-snug">{app.basis}</div>
                            {app.context_used && Object.keys(app.context_used).length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1 text-[10px] font-mono text-slate-500">
                                {Object.entries(app.context_used).map(([k, v]) => (
                                  <span key={k} className="px-1.5 py-0.2 bg-slate-50 rounded border border-slate-200">
                                    {k}: <span className="text-slate-800 font-semibold">{String(v)}</span>
                                  </span>
                                ))}
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 6: Final Audit Record (Immutable Snapshot) */}
          {activeTab === 'final_record' && (
            <FinalRecordSection
              inspection={inspection}
              finalRecord={finalRecord}
              onDownloadPdf={handleDownloadPdfReport}
              isDownloadingPdf={isDownloadingPdf}
              onDownloadDocx={handleDownloadDocxReport}
              isDownloadingDocx={isDownloadingDocx}
            />
          )}

          {/* Tab 7: Structured Regulatory Audit Ledger */}
          {activeTab === 'audit' && (
            <div className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 font-sans">
                    Formal Inspection Records & Cryptographic Audit Ledger
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Chronological chain-of-custody records with legal event descriptions and cryptographic digests.
                  </p>
                </div>
                <span className="text-xs text-emerald-700 font-semibold flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Chain of Custody Intact</span>
                </span>
              </div>

              {/* Chronological Table with Progressive Disclosure for Technical Details */}
              <div className="border border-slate-200 rounded-lg overflow-x-auto cleanroom-scrollbar bg-white shadow-xs">
                <table className="w-full min-w-[620px] text-left text-xs border-collapse">
                  <thead className="bg-slate-50 text-slate-700 font-sans font-semibold text-[11px] border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3 uppercase w-36">Timestamp</th>
                      <th className="py-2.5 px-3 uppercase w-32">Officer Role</th>
                      <th className="py-2.5 px-3 uppercase w-36">Event</th>
                      <th className="py-2.5 px-3 uppercase min-w-[240px]">Recorded Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-sans">
                    {auditEvents.map((evt) => {
                      const record = formatAuditRecord(evt.event_type, evt.details);
                      const isEventExpanded = Boolean(expandedAuditIds[evt.id]);

                      return (
                        <tr key={evt.id} className="hover:bg-slate-50/80 transition-colors">
                          {/* Timestamp */}
                          <td className="py-2.5 px-3 text-[11px] text-slate-600 whitespace-nowrap align-top font-mono">
                            {new Date(evt.created_at).toLocaleString()}
                          </td>

                          {/* Officer / Actor Role */}
                          <td className="py-2.5 px-3 whitespace-nowrap align-top">
                            <span className="font-semibold text-slate-800">{evt.actor_role}</span>
                          </td>

                          {/* Event Classification */}
                          <td className="py-2.5 px-3 whitespace-nowrap align-top">
                            <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 font-medium">
                              {evt.event_type}
                            </span>
                          </td>

                          {/* Action Summary with Expandable Metadata */}
                          <td className="py-2.5 px-3 text-slate-800 text-xs leading-relaxed align-top">
                            <div className="font-medium text-slate-900">{record.summary}</div>
                            {record.metadata.length > 0 && (
                              <div className="mt-1">
                                <button
                                  onClick={() =>
                                    setExpandedAuditIds((prev) => ({
                                      ...prev,
                                      [evt.id]: !prev[evt.id],
                                    }))
                                  }
                                  className="text-[10px] text-slate-500 hover:text-slate-800 underline font-sans flex items-center space-x-1"
                                >
                                  <span>{isEventExpanded ? 'Hide Parameters' : 'Show Parameters'}</span>
                                  {isEventExpanded ? <ChevronUp className="w-2.5 h-2.5" /> : <ChevronDown className="w-2.5 h-2.5" />}
                                </button>

                                {isEventExpanded && (
                                  <div className="flex flex-wrap gap-1.5 mt-1.5 pt-1.5 border-t border-slate-100">
                                    {record.metadata.map((item, idx) => (
                                      <span
                                        key={idx}
                                        className="bg-slate-50 border border-slate-200 text-slate-700 text-[10px] px-1.5 py-0.5 rounded font-mono inline-flex items-center space-x-1"
                                      >
                                        <span className="text-slate-400 font-semibold">{item.label}:</span>
                                        <span className="text-slate-900 font-medium">{item.value}</span>
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Phase 4 Action Modals */}
      <DeclarationCorrectionModal
        isOpen={showCorrectionModal}
        onClose={() => setShowCorrectionModal(false)}
        onSubmit={handleSaveCorrection}
      />

      <ManualObservationModal
        isOpen={showObservationModal}
        onClose={() => setShowObservationModal(false)}
        onSubmit={handleSaveObservation}
      />

      <SubmitForReviewModal
        isOpen={showSubmitModal}
        inspection={inspection}
        onClose={() => setShowSubmitModal(false)}
        onSubmit={handleSubmitForReview}
      />

      <ReviewerAdjudicationModal
        isOpen={showAdjudicationModal}
        finding={adjudicationFinding}
        onClose={() => {
          setShowAdjudicationModal(false);
          setAdjudicationFinding(null);
        }}
        onSubmit={handleRecordReviewerDecision}
      />

      <CreateEvidenceRequestModal
        isOpen={showCreateERModal}
        onClose={() => setShowCreateERModal(false)}
        onSubmit={handleCreateEvidenceRequest}
      />

      <FulfillEvidenceRequestModal
        isOpen={showFulfillERModal}
        request={targetER}
        inspection={inspection}
        onClose={() => {
          setShowFulfillERModal(false);
          setTargetER(null);
        }}
        onSubmit={handleFulfillEvidenceRequest}
      />

      <RequestRevisionModal
        isOpen={showRevisionModal}
        onClose={() => setShowRevisionModal(false)}
        onSubmit={handleRequestRevision}
      />

      <FinalizeInspectionModal
        isOpen={showFinalizeModal}
        inspection={inspection}
        onClose={() => setShowFinalizeModal(false)}
        onSubmit={handleFinalizeInspection}
      />

      {/* Camera Capture Modal */}
      {showCamera && (
        <CameraCapture
          onCapture={(file) => {
            setShowCamera(false);
            handleUploadFiles([file]);
          }}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
};

export default InspectionWorkspacePage;
