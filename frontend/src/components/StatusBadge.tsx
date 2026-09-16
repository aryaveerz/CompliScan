import React from 'react';
import { InspectionLifecycleState, OriginStatus } from '../types';

export const StatusBadge: React.FC<{ status: InspectionLifecycleState }> = ({ status }) => {
  const getStyles = () => {
    switch (status) {
      case 'DRAFT':
        return 'bg-slate-800 text-slate-300 border-slate-700';
      case 'EVIDENCE_UPLOADED':
        return 'bg-blue-950 text-blue-300 border-blue-800';
      case 'EXTRACTED':
        return 'bg-indigo-950 text-indigo-300 border-indigo-800';
      case 'APPLICABILITY_EVALUATED':
        return 'bg-purple-950 text-purple-300 border-purple-800';
      case 'EVALUATED':
        return 'bg-cyan-950 text-cyan-300 border-cyan-800';
      case 'IN_VERIFICATION':
        return 'bg-amber-950 text-amber-300 border-amber-800';
      case 'SUBMITTED_FOR_REVIEW':
        return 'bg-orange-950 text-orange-300 border-orange-800';
      case 'REQUIRES_REVISION':
        return 'bg-rose-950 text-rose-300 border-rose-800';
      case 'FINALIZED':
        return 'bg-emerald-950 text-emerald-300 border-emerald-800';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStyles()}`}
    >
      <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-current opacity-75"></span>
      {status.replace(/_/g, ' ')}
    </span>
  );
};

export const OriginBadge: React.FC<{ origin: OriginStatus }> = ({ origin }) => {
  const getStyles = () => {
    switch (origin) {
      case 'DOMESTIC':
        return 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60';
      case 'IMPORTED':
        return 'bg-amber-950/60 text-amber-400 border-amber-800/60';
      case 'UNKNOWN':
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStyles()}`}
    >
      {origin}
    </span>
  );
};
