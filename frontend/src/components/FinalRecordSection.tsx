import React, { useState } from 'react';
import {
  Shield,
  Download,
  Lock,
  Hash,
  FileDown,
  History,
} from 'lucide-react';
import { FinalAuditRecord, InspectionCase } from '../types';
import { AuditTimeline } from './AuditTimeline';

interface FinalRecordSectionProps {
  inspection: InspectionCase;
  finalRecord: FinalAuditRecord | null;
  onDownloadPdf: () => void;
  isDownloadingPdf: boolean;
  onDownloadDocx?: () => void;
  isDownloadingDocx?: boolean;
}

export const FinalRecordSection: React.FC<FinalRecordSectionProps> = ({
  inspection,
  finalRecord,
  onDownloadPdf,
  isDownloadingPdf,
  onDownloadDocx,
  isDownloadingDocx = false,
}) => {
  const [showTimeline, setShowTimeline] = useState(false);

  if (!finalRecord) {
    return (
      <div className="p-8 text-center bg-white">
        <Shield className="w-10 h-10 text-slate-300 mx-auto mb-2" />
        <h4 className="text-sm font-semibold text-slate-700">Final Audit Record Not Created</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
          This inspection docket has not been finalized yet. Once an authorized Reviewing Officer records the final adjudication and finalizes the case, the immutable record snapshot, official PDF report, and editable DOCX report will appear here.
        </p>
      </div>
    );
  }

  const isCompliant = finalRecord.final_decision === 'COMPLIANT';
  const isViolation = finalRecord.final_decision === 'NON_COMPLIANT_CONFIRMED';

  const decisionBadgeColor = isCompliant
    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
    : isViolation
    ? 'bg-rose-50 text-rose-800 border-rose-300'
    : 'bg-amber-50 text-amber-800 border-amber-300';

  return (
    <div className="p-4 space-y-6">
      {/* Top Banner: Immutable Legal Snapshot */}
      <div className="bg-slate-900 text-white rounded-lg p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4 shadow-xs">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span className="text-[11px] font-mono uppercase tracking-wider font-bold text-emerald-400">
              IMMUTABLE FINAL AUDIT RECORD — LAWFULLY FROZEN
            </span>
          </div>
          <h3 className="text-base font-bold tracking-tight">
            Case {inspection.case_number}: {inspection.product_name}
          </h3>
          <p className="text-xs text-slate-300 font-sans">
            Finalized by Reviewing Officer on {new Date(finalRecord.finalized_at).toLocaleString()}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <button
            onClick={onDownloadPdf}
            disabled={isDownloadingPdf}
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold rounded-md shadow-xs transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isDownloadingPdf ? 'Generating PDF…' : 'Download PDF'}</span>
          </button>

          {onDownloadDocx && (
            <button
              onClick={onDownloadDocx}
              disabled={isDownloadingDocx}
              className="inline-flex items-center space-x-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold rounded-md shadow-xs transition-colors cursor-pointer"
            >
              <FileDown className="w-3.5 h-3.5" />
              <span>{isDownloadingDocx ? 'Generating DOCX…' : 'Download DOCX'}</span>
            </button>
          )}

          <button
            onClick={() => setShowTimeline(!showTimeline)}
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-md border border-slate-700 transition-colors cursor-pointer"
          >
            <History className="w-3.5 h-3.5" />
            <span>{showTimeline ? 'Hide Audit Log' : 'Audit Chain'}</span>
          </button>
        </div>
      </div>

      {/* Embedded Audit Timeline (if toggled) */}
      {showTimeline && (
        <AuditTimeline inspectionId={inspection.id} />
      )}

      {/* Decision Summary Card */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-2xs space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
            Final Statutory Determination
          </span>
          <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${decisionBadgeColor}`}>
            {finalRecord.final_decision.replace(/_/g, ' ')}
          </span>
        </div>

        <div>
          <span className="text-[11px] text-slate-500 block font-semibold">Master Reviewer Rationale:</span>
          <p className="text-xs text-slate-800 mt-1 leading-relaxed bg-slate-50 p-2.5 rounded border border-slate-200 font-sans">
            {finalRecord.final_rationale}
          </p>
        </div>

        {/* Regulatory Governance Provenance */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100 text-[10px] font-mono text-slate-600">
          <div>
            <span className="text-slate-400 block font-sans">Rule Set ID</span>
            <span className="font-semibold text-slate-800">{finalRecord.rule_set_id}</span>
          </div>
          <div>
            <span className="text-slate-400 block font-sans">Rule Set Version</span>
            <span className="font-semibold text-slate-800">{finalRecord.rule_set_version}</span>
          </div>
          <div>
            <span className="text-slate-400 block font-sans">Evaluation Version</span>
            <span className="font-semibold text-slate-800">{finalRecord.evaluation_version}</span>
          </div>
          <div>
            <span className="text-slate-400 block font-sans">Record ID</span>
            <span className="font-semibold text-slate-800 truncate block" title={finalRecord.id}>
              {finalRecord.id.slice(0, 8)}…
            </span>
          </div>
        </div>
      </div>

      {/* Evidence SHA-256 Hashes Snapshot */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-2xs space-y-2">
        <div className="flex items-center space-x-2">
          <Hash className="w-3.5 h-3.5 text-slate-700" />
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
            Source Evidence SHA-256 Digests
          </h4>
        </div>
        <div className="space-y-1.5 pt-1">
          {finalRecord.source_evidence_hashes &&
            Object.entries(finalRecord.source_evidence_hashes).map(([evId, sha]) => (
              <div
                key={evId}
                className="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-100 font-mono text-[11px]"
              >
                <span className="text-slate-600 font-medium">Evidence #{evId.slice(0, 8)}</span>
                <span className="text-slate-900 font-semibold select-all">{sha}</span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
