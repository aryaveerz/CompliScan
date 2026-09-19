import React from 'react';
import { InspectionLifecycleState, OriginStatus, ComplianceResult } from '../types';

// DESIGN.md: restrained badge geometry — rounded (4px), no rounded-full pills
// Semantic colour distinctions are preserved across all three badge variants.

export const StatusBadge: React.FC<{ status: InspectionLifecycleState }> = ({ status }) => {
  const getStyles = () => {
    switch (status) {
      case 'DRAFT':
        return 'bg-slate-100 text-slate-700 border-slate-300';
      case 'EVIDENCE_UPLOADED':
        return 'bg-sky-50 text-sky-800 border-sky-200';
      case 'EXTRACTED':
        return 'bg-sky-100 text-sky-900 border-sky-300';
      case 'APPLICABILITY_EVALUATED':
        return 'bg-teal-50 text-teal-800 border-teal-200';
      case 'EVALUATED':
        return 'bg-cyan-50 text-cyan-800 border-cyan-200';
      case 'IN_VERIFICATION':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'SUBMITTED_FOR_REVIEW':
        return 'bg-blue-50 text-blue-800 border-blue-200';
      case 'REQUIRES_REVISION':
        return 'bg-orange-50 text-orange-800 border-orange-300';
      case 'FINALIZED':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStyles()} font-mono`}
    >
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current opacity-75" />
      {status.replace(/_/g, ' ')}
    </span>
  );
};

export const OriginBadge: React.FC<{ origin: OriginStatus }> = ({ origin }) => {
  const getStyles = () => {
    switch (origin) {
      case 'DOMESTIC':
        return 'bg-emerald-50 text-emerald-800 border-emerald-300';
      case 'IMPORTED':
        return 'bg-amber-50 text-amber-800 border-amber-300';
      case 'UNKNOWN':
      default:
        return 'bg-slate-100 text-slate-600 border-slate-300';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStyles()} font-mono`}
    >
      {origin}
    </span>
  );
};

export const ComplianceBadge: React.FC<{ result: ComplianceResult }> = ({ result }) => {
  const getStyles = () => {
    switch (result) {
      case 'PASS':
        return 'bg-[#f0fdf4] text-[#15803d] border-[#bbf7d0]';
      case 'POTENTIAL_NON_COMPLIANCE':
        // Warm ochre/amber — NEVER red (Rarity of Red Rule)
        return 'bg-[#fff7ed] text-[#c2410c] border-[#fed7aa]';
      case 'REQUIRES_REVIEW':
        return 'bg-[#fffbeb] text-[#b45309] border-[#fde68a]';
      case 'NOT_APPLICABLE':
        return 'bg-[#f8fafc] text-[#475569] border-[#e2e8f0]';
      case 'INCOMPLETE':
        return 'bg-[#f8fafc] text-[#64748b] border-[#cbd5e1]';
      case 'PROCESSING_FAILED':
        return 'bg-[#fef2f2] text-[#b91c1c] border-[#fecaca]';
      case 'CONFIRMED_VIOLATION':
        // Reserved strictly for explicit human reviewer adjudication
        return 'bg-[#fef2f2] text-[#991b1b] border-[#f87171]';
      default:
        return 'bg-[#f8fafc] text-[#475569] border-[#e2e8f0]';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStyles()} font-mono`}
    >
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current opacity-75" />
      {result.replace(/_/g, ' ')}
    </span>
  );
};
