import React from 'react';
import {
  CheckCircle2,
  AlertCircle,
  PlusCircle,
  FileCheck,
  Edit2,
  MessageSquare,
  Send,
  Clock,
  Info,
} from 'lucide-react';
import {
  VerificationState,
  InspectionCase,
  ComplianceEvaluationSummary,
} from '../types';

interface InspectorVerificationSectionProps {
  inspection: InspectionCase;
  verificationState: VerificationState | null;
  complianceSummary: ComplianceEvaluationSummary | null;
  isReadOnly: boolean;
  isInspector: boolean;
  onOpenCorrectionModal: () => void;
  onOpenObservationModal: () => void;
  onOpenSubmitModal: () => void;
}

export const InspectorVerificationSection: React.FC<InspectorVerificationSectionProps> = ({
  inspection,
  verificationState,
  complianceSummary,
  isReadOnly,
  isInspector,
  onOpenCorrectionModal,
  onOpenObservationModal,
  onOpenSubmitModal,
}) => {
  const corrections = verificationState?.corrections || [];
  const manualObservations = verificationState?.manual_observations || [];
  const canSubmit =
    !isReadOnly &&
    (inspection.status === 'EVALUATED' ||
      inspection.status === 'IN_VERIFICATION' ||
      inspection.status === 'REQUIRES_REVISION' ||
      inspection.status === 'EVIDENCE_UPLOADED' ||
      inspection.status === 'EXTRACTED');

  return (
    <div className="p-4 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <FileCheck className="w-4 h-4 text-slate-800" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-sans">
              Inspector Verification & Data Audit
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Inspectors verify perception outputs, record statutory data corrections with audit justifications, and register manual packaging observations.
          </p>
        </div>

        {isInspector && canSubmit && (
          <button
            onClick={onOpenSubmitModal}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded shadow-2xs transition-colors shrink-0"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Submit for Review</span>
          </button>
        )}
      </div>

      {/* Verification Checklist */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs space-y-2">
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
          Verification Readiness Checklist
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
          <div className="flex items-center space-x-2">
            {inspection.evidence_assets.length > 0 ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
            )}
            <span className="text-slate-700">
              Evidence: <strong>{inspection.evidence_assets.length} Assets</strong>
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {complianceSummary ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            )}
            <span className="text-slate-700">
              Compliance: <strong>{complianceSummary ? 'Evaluated' : 'Pending'}</strong>
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {inspection.status === 'SUBMITTED_FOR_REVIEW' || inspection.status === 'FINALIZED' ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            ) : (
              <Clock className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
            )}
            <span className="text-slate-700">
              Docket: <strong>{inspection.status.replace(/_/g, ' ')}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Visual Font-Size Screening Notice */}
      <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 flex items-start space-x-2">
        <Info className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-800">Visual Font-Size Screening Notice:</span>{' '}
          Visual font-size screening uses OCR bounding-box height as an engineering proxy. It is not a physical millimetre measurement; field verification may be required for statutory certification.
        </div>
      </div>

      {/* Section 1: Declaration Corrections */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Edit2 className="w-3.5 h-3.5 text-slate-700" />
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
              Declaration Corrections ({corrections.length})
            </h4>
          </div>
          {isInspector && !isReadOnly && (
            <button
              onClick={onOpenCorrectionModal}
              className="inline-flex items-center space-x-1 text-xs text-indigo-700 hover:text-indigo-900 font-medium hover:underline"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Record Correction</span>
            </button>
          )}
        </div>

        {corrections.length === 0 ? (
          <div className="bg-white border border-slate-200 border-dashed rounded-lg p-4 text-center text-slate-400 text-xs">
            No declaration corrections recorded. Extracted statutory values remain as originally perceived.
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-2xs">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 text-slate-700 font-semibold text-[11px] border-b border-slate-200 uppercase">
                <tr>
                  <th className="py-2.5 px-3 w-28">Rule Citation</th>
                  <th className="py-2.5 px-3 w-40">Statutory Field</th>
                  <th className="py-2.5 px-3 w-48">Prior Value</th>
                  <th className="py-2.5 px-3 w-48">Corrected Value</th>
                  <th className="py-2.5 px-3 min-w-[200px]">Audit Reason</th>
                  <th className="py-2.5 px-3 w-32">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-sans">
                {corrections.map((corr) => {
                  const prevText =
                    typeof corr.previous_value === 'object' && corr.previous_value !== null
                      ? JSON.stringify(corr.previous_value)
                      : String(corr.previous_value || 'None');
                  const corrText =
                    typeof corr.corrected_value === 'object' && corr.corrected_value !== null
                      ? JSON.stringify(corr.corrected_value)
                      : String(corr.corrected_value || '');

                  return (
                    <tr key={corr.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 px-3 font-mono font-bold text-slate-700 whitespace-nowrap">
                        {corr.rule_citation || '—'}
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-slate-900">
                        {corr.field_name}
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-500 line-through text-[11px]">
                        {prevText}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-emerald-800 bg-emerald-50/50 text-[11px]">
                        {corrText}
                      </td>
                      <td className="py-2.5 px-3 text-slate-700 leading-snug">
                        {corr.correction_reason}
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-400 text-[10px] whitespace-nowrap">
                        {new Date(corr.created_at).toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Section 2: Manual Observations */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-3.5 h-3.5 text-slate-700" />
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
              Manual Packaging Observations ({manualObservations.length})
            </h4>
          </div>
          {isInspector && !isReadOnly && (
            <button
              onClick={onOpenObservationModal}
              className="inline-flex items-center space-x-1 text-xs text-indigo-700 hover:text-indigo-900 font-medium hover:underline"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Add Observation</span>
            </button>
          )}
        </div>

        {manualObservations.length === 0 ? (
          <div className="bg-white border border-slate-200 border-dashed rounded-lg p-4 text-center text-slate-400 text-xs">
            No manual physical observations registered for this packaging docket.
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-2xs">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 text-slate-700 font-semibold text-[11px] border-b border-slate-200 uppercase">
                <tr>
                  <th className="py-2.5 px-3 w-44">Requirement Domain</th>
                  <th className="py-2.5 px-3 min-w-[260px]">Observation & Physical Context</th>
                  <th className="py-2.5 px-3 w-36">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-sans">
                {manualObservations.map((obs) => (
                  <tr key={obs.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-slate-900 whitespace-nowrap">
                      <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] border border-slate-200">
                        {obs.requirement_domain.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-800 leading-relaxed font-sans">
                      {obs.observation_text}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-400 text-[10px] whitespace-nowrap">
                      {new Date(obs.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
