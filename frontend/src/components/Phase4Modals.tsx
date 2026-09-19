import React, { useState } from 'react';
import {
  X,
  AlertTriangle,
  Send,
  CheckCircle2,
  FileCheck,
  Shield,
  Upload,
  Lock,
} from 'lucide-react';
import {
  InspectionCase,
  ComplianceFinding,
  EvidenceRequest,
  FinalDecision,
  ComplianceResult,
} from '../types';

// ── 1. Declaration Correction Modal ──────────────────────────────────────────
export const DeclarationCorrectionModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (field_name: string, rule_citation: string, previous_value: string, corrected_value: string, reason: string) => Promise<void>;
}> = ({ isOpen, onClose, onSubmit }) => {
  const [field, setField] = useState('manufacturer_name');
  const [rule, setRule] = useState('Rule 6(1)(a)');
  const [prevVal, setPrevVal] = useState('');
  const [corrVal, setCorrVal] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFieldChange = (val: string) => {
    setField(val);
    switch (val) {
      case 'manufacturer_name':
      case 'manufacturer_address':
        setRule('Rule 6(1)(a)');
        break;
      case 'commodity_name':
        setRule('Rule 6(1)(b)');
        break;
      case 'net_quantity':
        setRule('Rule 6(1)(c)');
        break;
      case 'manufacture_date':
        setRule('Rule 6(1)(d)');
        break;
      case 'mrp':
        setRule('Rule 6(1)(e)');
        break;
      case 'consumer_care':
        setRule('Rule 6(1)(f)');
        break;
      case 'country_of_origin':
        setRule('Rule 6(1)(da)');
        break;
      default:
        setRule('Rule 6(1)');
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!corrVal.trim()) {
      setError('Corrected statutory value is required.');
      return;
    }
    if (!reason.trim() || reason.trim().length < 10) {
      setError('Audit justification is mandatory and must be at least 10 characters.');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(field, rule, prevVal.trim(), corrVal.trim(), reason.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to record declaration correction');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <FileCheck className="w-4 h-4 text-slate-800" />
            <h3 className="text-sm font-bold text-slate-900">Record Declaration Correction</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Statutory Declaration Field *</label>
            <select
              value={field}
              onChange={(e) => handleFieldChange(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            >
              <option value="manufacturer_name">Manufacturer / Packer / Importer Name (Rule 6(1)(a))</option>
              <option value="manufacturer_address">Manufacturer Postal Address (Rule 6(1)(a))</option>
              <option value="commodity_name">Generic / Common Commodity Name (Rule 6(1)(b))</option>
              <option value="net_quantity">Net Quantity & Unit (Rule 6(1)(c))</option>
              <option value="manufacture_date">Month & Year of Manufacture / Packing (Rule 6(1)(d))</option>
              <option value="mrp">Maximum Retail Price (MRP) (Rule 6(1)(e))</option>
              <option value="consumer_care">Consumer Care Details (Rule 6(1)(f))</option>
              <option value="country_of_origin">Country of Origin (Rule 6(1)(da))</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Prior / Perceived Value</label>
              <input
                type="text"
                value={prevVal}
                onChange={(e) => setPrevVal(e.target.value)}
                placeholder="Observed raw text…"
                className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-slate-900 font-mono text-[11px]"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Corrected Value *</label>
              <input
                type="text"
                value={corrVal}
                onChange={(e) => setCorrVal(e.target.value)}
                placeholder="Verified statutory text…"
                className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 font-mono text-[11px] focus:outline-none focus:border-slate-800"
                required
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Mandatory Audit Reason * (Min 10 characters)
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="Provide statutory rationale e.g. 'Corrected net quantity unit from g to kg as verified on principal display panel'…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              required
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded font-semibold"
            >
              {isSubmitting ? 'Saving…' : 'Record Correction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── 2. Manual Observation Modal ──────────────────────────────────────────────
export const ManualObservationModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (requirement_domain: string, observation_text: string) => Promise<void>;
}> = ({ isOpen, onClose, onSubmit }) => {
  const [domain, setDomain] = useState('PACKAGING_OBSERVATION');
  const [text, setText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || text.trim().length < 10) {
      setError('Observation text is mandatory and must be at least 10 characters.');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(domain, text.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to record manual observation');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">Add Manual Packaging Observation</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Requirement Domain *</label>
            <select
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            >
              <option value="PACKAGING_OBSERVATION">General Packaging Observation</option>
              <option value="MANUFACTURER_IDENTITY">Manufacturer Identity & Address</option>
              <option value="NET_QUANTITY">Net Quantity & Measurement Verification</option>
              <option value="DATE_VERIFICATION">Date of Packaging Verification</option>
              <option value="MRP_VERIFICATION">MRP & Pricing Indication</option>
              <option value="CONSUMER_CARE">Consumer Care Helpline Verification</option>
              <option value="COUNTRY_OF_ORIGIN">Country of Origin Physical Observation</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Observation Details * (Min 10 characters)
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              placeholder="Record direct physical observation, packaging side observations, or tactile verification notes…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              required
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded font-semibold"
            >
              {isSubmitting ? 'Recording…' : 'Record Observation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── 3. Submit For Review Modal ───────────────────────────────────────────────
export const SubmitForReviewModal: React.FC<{
  isOpen: boolean;
  inspection: InspectionCase;
  onClose: () => void;
  onSubmit: () => Promise<void>;
}> = ({ isOpen, inspection, onClose, onSubmit }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit inspection for review');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full p-5 space-y-4">
        <div className="flex items-center space-x-2.5 text-slate-900 pb-2 border-b border-slate-100">
          <Send className="w-5 h-5 text-slate-800" />
          <h3 className="text-sm font-bold">Submit Inspection for Review</h3>
        </div>

        <p className="text-xs text-slate-600 leading-relaxed">
          You are submitting Case <strong className="text-slate-900">{inspection.case_number}</strong> ({inspection.product_name}) for formal Reviewer adjudication under the Legal Metrology Rules, 2011.
        </p>

        <div className="bg-slate-50 p-3 rounded border border-slate-200 text-xs space-y-1 text-slate-600">
          <div className="flex items-center space-x-1.5 text-emerald-700 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Pre-submission Checks Verified</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Lifecycle state will transition to <span className="font-mono font-bold text-slate-800">SUBMITTED_FOR_REVIEW</span>. An immutable audit event will be logged.
          </p>
        </div>

        {error && (
          <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100 text-xs">
          <button
            onClick={onClose}
            className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={isSubmitting}
            className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded font-semibold flex items-center space-x-1.5"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSubmitting ? 'Submitting…' : 'Confirm Submission'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// ── 4. Reviewer Adjudication Drawer / Modal ──────────────────────────────────
export const ReviewerAdjudicationModal: React.FC<{
  isOpen: boolean;
  finding: ComplianceFinding | null;
  onClose: () => void;
  onSubmit: (requirement_name: string, adjudicated_result: ComplianceResult, is_override: boolean, rationale: string) => Promise<void>;
}> = ({ isOpen, finding, onClose, onSubmit }) => {
  const [result, setResult] = useState<ComplianceResult>('PASS');
  const [rationale, setRationale] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !finding) return null;

  const isOverride = result !== finding.result;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rationale.trim() || rationale.trim().length < 10) {
      setError('Mandatory statutory justification is required (minimum 10 characters).');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(finding.requirement_name, result, isOverride, rationale.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to record reviewer decision');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-slate-800" />
            <h3 className="text-sm font-bold text-slate-900">
              Reviewer Adjudication — {finding.rule_citation}
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-3.5 text-xs">
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200 space-y-1">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
              Automated Compliance Finding (Frozen)
            </span>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-slate-800">{finding.requirement_name}</span>
              <span className="text-slate-600">→ Result: <strong className="text-slate-900">{finding.result}</strong></span>
            </div>
            <p className="text-[11px] text-slate-500 leading-snug">{finding.reason}</p>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Reviewer Statutory Determination *
            </label>
            <select
              value={result}
              onChange={(e) => setResult(e.target.value as ComplianceResult)}
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            >
              <option value="PASS">PASS (Verified Statutory Compliance)</option>
              <option value="POTENTIAL_NON_COMPLIANCE">POTENTIAL NON-COMPLIANCE (Adjudicated Deviation)</option>
              <option value="REQUIRES_REVIEW">REQUIRES REVIEW (Ambiguous Context)</option>
              <option value="NOT_APPLICABLE">NOT APPLICABLE (Statutory Exemption)</option>
            </select>
          </div>

          {isOverride && (
            <div className="p-2 bg-amber-50 border border-amber-200 rounded text-amber-900 text-[11px] flex items-center space-x-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-700 shrink-0" />
              <span>
                <strong>Statutory Override Detected:</strong> Your decision differs from the automated finding. A formal override audit event will be logged.
              </span>
            </div>
          )}

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Mandatory Recorded Rationale * (Min 10 characters)
            </label>
            <textarea
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              rows={3}
              placeholder="State legal rationale, physical verification findings, or compounding order reference…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              required
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded font-semibold"
            >
              {isSubmitting ? 'Saving…' : 'Record Adjudication'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── 5. Evidence Request Modal ────────────────────────────────────────────────
export const CreateEvidenceRequestModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (requirement_name: string, request_reason: string, requested_condition?: string, requested_evidence_type?: string) => Promise<void>;
}> = ({ isOpen, onClose, onSubmit }) => {
  const [reqName, setReqName] = useState('consumer_care_contact');
  const [reason, setReason] = useState('');
  const [condition, setCondition] = useState('');
  const [evidenceType, setEvidenceType] = useState('IMAGE');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim() || reason.trim().length < 10) {
      setError('Request reason must specify what fact/condition needs to be established (minimum 10 characters).');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(reqName, reason.trim(), condition.trim() || undefined, evidenceType);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create evidence request');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">Create Supplemental Evidence Request</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Target Requirement *</label>
            <select
              value={reqName}
              onChange={(e) => setReqName(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            >
              <option value="consumer_care_contact">Consumer Care Contact Details (Rule 6(1)(f))</option>
              <option value="net_quantity_declaration">Net Quantity Declaration (Rule 6(1)(c))</option>
              <option value="mrp_declaration">Maximum Retail Price (MRP) (Rule 6(1)(e))</option>
              <option value="date_of_manufacture">Month & Year of Manufacture (Rule 6(1)(d))</option>
              <option value="manufacturer_name_and_address">Manufacturer Name & Address (Rule 6(1)(a))</option>
              <option value="commodity_name">Generic / Common Commodity Name (Rule 6(1)(b))</option>
              <option value="country_of_origin">Country of Origin (Rule 6(1)(da))</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              What Fact or Condition Needs to be Established? * (Min 10 chars)
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="e.g. 'Provide clear high-resolution photo showing consumer-care helpline and email on rear panel'…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Requested Condition</label>
              <input
                type="text"
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                placeholder="e.g. 'Legible consumer-care email and toll-free telephone number'"
                className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Evidence Type</label>
              <select
                value={evidenceType}
                onChange={(e) => setEvidenceType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              >
                <option value="IMAGE">Image / High-Resolution Photograph</option>
                <option value="DOCUMENT">Statutory Document / Order</option>
                <option value="LABEL_CROP">Packaging Label Crop</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded font-semibold"
            >
              {isSubmitting ? 'Creating…' : 'Issue Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── 6. Fulfill Evidence Request Modal ────────────────────────────────────────
export const FulfillEvidenceRequestModal: React.FC<{
  isOpen: boolean;
  request: EvidenceRequest | null;
  inspection: InspectionCase;
  onClose: () => void;
  onSubmit: (erId: string, evidenceAssetId?: string, responseNote?: string) => Promise<void>;
}> = ({ isOpen, request, inspection, onClose, onSubmit }) => {
  const [assetId, setAssetId] = useState<string>('');
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !request) return null;

  const handleFulfill = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(request.id, assetId || undefined, note.trim() || undefined);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to fulfill evidence request');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-md w-full p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <Upload className="w-4 h-4 text-emerald-700" />
            <h3 className="text-sm font-bold text-slate-900">Fulfill Evidence Request {request.request_id}</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleFulfill} className="space-y-3.5 text-xs">
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200 space-y-1">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
              Requested Requirement
            </span>
            <p className="font-semibold text-slate-900">{request.requirement_name}</p>
            <p className="text-[11px] text-slate-600 leading-snug">{request.request_reason}</p>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Select Responding Evidence Asset</label>
            <select
              value={assetId}
              onChange={(e) => setAssetId(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            >
              <option value="">Select an uploaded asset…</option>
              {inspection.evidence_assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.original_filename} (SHA: {asset.sha256_hash.slice(0, 8)}…)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Response Note</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
              placeholder="e.g. 'Uploaded high-res crop of rear panel showing customer care telephone and email address'…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white rounded font-semibold"
            >
              {isSubmitting ? 'Fulfilling…' : 'Complete Fulfillment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── 7. Request Revision Modal ────────────────────────────────────────────────
export const RequestRevisionModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (reason: string, requested_changes?: string) => Promise<void>;
}> = ({ isOpen, onClose, onSubmit }) => {
  const [reason, setReason] = useState('');
  const [changes, setChanges] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason.trim() || reason.trim().length < 10) {
      setError('Revision reason is mandatory (minimum 10 characters).');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(reason.trim(), changes.trim() || undefined);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to request revision');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-700" />
            <h3 className="text-sm font-bold text-slate-900">Request Docket Revision</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-3.5 text-xs">
          <p className="text-slate-600 leading-relaxed">
            Transition docket back to <strong className="text-slate-900">REQUIRES_REVISION</strong> so the inspecting officer can correct data, supply supplemental evidence, or update observations.
          </p>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Revision Reason * (Min 10 characters)
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="State what needs revision e.g. 'Consumer care phone number is truncated in OCR, please supply crop of full contact box'…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              required
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Specific Requested Changes</label>
            <textarea
              value={changes}
              onChange={(e) => setChanges(e.target.value)}
              rows={2}
              placeholder="Specific action items for inspecting officer…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-amber-700 hover:bg-amber-800 disabled:opacity-50 text-white rounded font-semibold"
            >
              {isSubmitting ? 'Submitting…' : 'Issue Revision Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── 8. Finalize Inspection Modal ─────────────────────────────────────────────
export const FinalizeInspectionModal: React.FC<{
  isOpen: boolean;
  inspection: InspectionCase;
  onClose: () => void;
  onSubmit: (final_decision: FinalDecision, final_rationale: string) => Promise<void>;
}> = ({ isOpen, inspection, onClose, onSubmit }) => {
  const [decision, setDecision] = useState<FinalDecision>('COMPLIANT');
  const [rationale, setRationale] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFinalize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rationale.trim() || rationale.trim().length < 10) {
      setError('Master final rationale is mandatory (minimum 10 characters).');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(decision, rationale.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to finalize inspection');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-lg border border-slate-200 shadow-xl max-w-lg w-full p-5 space-y-4">
        <div className="flex items-center space-x-2.5 text-slate-900 pb-3 border-b border-slate-100">
          <Lock className="w-5 h-5 text-emerald-700" />
          <div>
            <h3 className="text-sm font-bold">
              Finalize Inspection {inspection.case_number}: {inspection.product_name}
            </h3>
            <span className="text-[11px] text-slate-500 font-normal">
              Irreversible legal record creation under Legal Metrology Rules, 2011
            </span>
          </div>
        </div>

        <form onSubmit={handleFinalize} className="space-y-3.5 text-xs">
          <div className="p-3 bg-amber-50 border border-amber-200 rounded text-amber-900 text-[11px] space-y-1">
            <span className="font-bold block">IMPORTANT LEGAL NOTICE:</span>
            <p className="leading-relaxed">
              Finalizing will create an immutable <span className="font-mono font-semibold">FinalAuditRecord</span> and lock this docket to <span className="font-mono font-semibold">READ_ONLY</span>. No further edits, overrides, or evidence uploads will be permitted.
            </p>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Final Statutory Determination *
            </label>
            <select
              value={decision}
              onChange={(e) => setDecision(e.target.value as FinalDecision)}
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 font-semibold focus:outline-none focus:border-slate-800"
            >
              <option value="COMPLIANT">COMPLIANT — All statutory declarations satisfied</option>
              <option value="NON_COMPLIANT_CONFIRMED">NON_COMPLIANT_CONFIRMED — Statutory violations confirmed</option>
              <option value="INCONCLUSIVE">INCONCLUSIVE — Evidence insufficient for definitive adjudication</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Master Reviewer Rationale * (Min 10 characters)
            </label>
            <textarea
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              rows={3}
              placeholder="State comprehensive legal rationale and statutory finding for the official inspection report…"
              className="w-full bg-white border border-slate-300 rounded p-2 text-slate-900 focus:outline-none focus:border-slate-800"
              required
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-700 text-xs flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 border border-slate-300 rounded text-slate-700 hover:bg-slate-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white rounded font-semibold flex items-center space-x-1.5"
            >
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>{isSubmitting ? 'Finalizing…' : 'Finalize & Freeze Docket'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
