import React from 'react';
import {
  FileQuestion,
  PlusCircle,
  Upload,
} from 'lucide-react';
import {
  InspectionCase,
  EvidenceRequest,
} from '../types';

interface EvidenceRequestsSectionProps {
  inspection: InspectionCase;
  evidenceRequests: EvidenceRequest[];
  isReadOnly: boolean;
  isReviewer: boolean;
  isInspector: boolean;
  onOpenCreateRequestModal: () => void;
  onOpenFulfillModal: (er: EvidenceRequest) => void;
}

export const EvidenceRequestsSection: React.FC<EvidenceRequestsSectionProps> = ({
  evidenceRequests,
  isReadOnly,
  isReviewer,
  isInspector,
  onOpenCreateRequestModal,
  onOpenFulfillModal,
}) => {
  const openRequests = evidenceRequests.filter((r) => r.status === 'OPEN');
  const fulfilledRequests = evidenceRequests.filter((r) => r.status === 'FULFILLED');

  return (
    <div className="p-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <FileQuestion className="w-4 h-4 text-slate-800" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-sans">
              Supplemental Evidence Requests ({evidenceRequests.length})
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Formal reviewer requests for supplemental packaging evidence to verify unobserved or ambiguous statutory conditions.
          </p>
        </div>

        {isReviewer && !isReadOnly && (
          <button
            onClick={onOpenCreateRequestModal}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded shadow-2xs transition-colors shrink-0"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Create Evidence Request</span>
          </button>
        )}
      </div>

      {/* Requests Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
            Total Requests
          </span>
          <div className="text-lg font-bold text-slate-900 mt-1 font-mono">
            {evidenceRequests.length}
          </div>
        </div>

        <div className="bg-amber-50/50 border border-amber-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-amber-800 uppercase tracking-wider block">
            Pending Fulfillment
          </span>
          <div className="text-lg font-bold text-amber-900 mt-1 font-mono">
            {openRequests.length}
          </div>
        </div>

        <div className="bg-emerald-50/50 border border-emerald-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">
            Fulfilled
          </span>
          <div className="text-lg font-bold text-emerald-900 mt-1 font-mono">
            {fulfilledRequests.length}
          </div>
        </div>
      </div>

      {/* Requests Table */}
      {evidenceRequests.length === 0 ? (
        <div className="bg-white border border-slate-200 border-dashed rounded-lg p-8 text-center text-slate-400 text-xs">
          No formal evidence requests created for this packaging inspection docket.
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-2xs">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-slate-700 font-semibold text-[11px] border-b border-slate-200 uppercase">
              <tr>
                <th className="py-2.5 px-3 w-28">Request ID</th>
                <th className="py-2.5 px-3 w-40">Requirement</th>
                <th className="py-2.5 px-3 w-32">Status</th>
                <th className="py-2.5 px-3 min-w-[220px]">Requested Condition & Reason</th>
                <th className="py-2.5 px-3 w-48">Fulfillment Note</th>
                <th className="py-2.5 px-3 w-28 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {evidenceRequests.map((er) => {
                const isOpen = er.status === 'OPEN';
                const isFulfilled = er.status === 'FULFILLED';

                const statusColor = isOpen
                  ? 'bg-amber-50 text-amber-800 border-amber-300'
                  : isFulfilled
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                  : 'bg-slate-100 text-slate-600 border-slate-300';

                return (
                  <tr key={er.id} className="hover:bg-slate-50/70 transition-colors">
                    {/* Request ID */}
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900 whitespace-nowrap align-top">
                      {er.request_id}
                    </td>

                    {/* Requirement */}
                    <td className="py-2.5 px-3 font-semibold text-slate-900 align-top">
                      {er.requirement_name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                    </td>

                    {/* Status */}
                    <td className="py-2.5 px-3 align-top whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${statusColor}`}>
                        {er.status}
                      </span>
                    </td>

                    {/* Request Details */}
                    <td className="py-2.5 px-3 align-top space-y-1 text-slate-800 text-[11px]">
                      <div className="font-medium text-slate-900">{er.request_reason}</div>
                      {er.requested_condition && (
                        <div className="text-slate-500 text-[10px]">
                          <strong>Condition:</strong> {er.requested_condition}
                        </div>
                      )}
                      <div className="text-slate-400 text-[9px] font-mono">
                        Requested: {new Date(er.created_at).toLocaleString()}
                      </div>
                    </td>

                    {/* Fulfillment */}
                    <td className="py-2.5 px-3 align-top text-[11px] text-slate-700">
                      {isFulfilled ? (
                        <div className="space-y-0.5">
                          <span className="text-emerald-700 font-semibold block">Fulfilled</span>
                          <p className="text-slate-600 text-[10px]">{er.response_note || 'Evidence linked'}</p>
                          {er.resolved_at && (
                            <span className="text-slate-400 font-mono text-[9px] block">
                              {new Date(er.resolved_at).toLocaleString()}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-400 italic text-[10px]">Awaiting inspector evidence</span>
                      )}
                    </td>

                    {/* Action */}
                    <td className="py-2.5 px-3 text-right align-top whitespace-nowrap">
                      {isOpen && isInspector && !isReadOnly && (
                        <button
                          onClick={() => onOpenFulfillModal(er)}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 bg-emerald-700 hover:bg-emerald-800 text-white text-[11px] font-semibold rounded transition-colors shadow-2xs"
                        >
                          <Upload className="w-3 h-3" />
                          <span>Fulfill</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
