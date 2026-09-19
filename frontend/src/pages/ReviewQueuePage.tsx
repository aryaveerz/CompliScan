import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Shield,
  Search,
  FileCheck,
  ArrowRight,
  AlertTriangle,
  UserCheck,
  RefreshCw,
} from 'lucide-react';
import { ReviewQueueItem } from '../types';
import { api } from '../api/client';
import { StatusBadge, OriginBadge } from '../components/StatusBadge';

export const ReviewQueuePage: React.FC = () => {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterState, setFilterState] = useState<string>('ALL');
  const [error, setError] = useState<string | null>(null);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getReviewQueue();
      setQueue(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch review queue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const filtered = queue.filter((item) => {
    const matchesSearch =
      item.product_name.toLowerCase().includes(search.toLowerCase()) ||
      item.case_number.toLowerCase().includes(search.toLowerCase()) ||
      (item.inspector_name && item.inspector_name.toLowerCase().includes(search.toLowerCase()));

    const matchesState =
      filterState === 'ALL' ||
      (filterState === 'SUBMITTED' && item.status === 'SUBMITTED_FOR_REVIEW') ||
      (filterState === 'REVISION' && item.status === 'REQUIRES_REVISION') ||
      (filterState === 'FINALIZED' && item.status === 'FINALIZED');

    return matchesSearch && matchesState;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-slate-900" />
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Reviewer Governance Workspace
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-0.5">
            Adjudicate submitted Legal Metrology inspections, verify evidence requests, and finalize legally immutable audit records.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchQueue}
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Queue</span>
          </button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 mb-5">
        <div className="sm:col-span-8 relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by case number, product name, or inspector..."
            className="w-full pl-8 pr-4 py-2 bg-white border border-slate-300 rounded text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-800"
          />
        </div>

        <div className="sm:col-span-4 flex items-center space-x-1.5 bg-slate-100 p-1 rounded border border-slate-200 text-xs font-medium">
          <button
            onClick={() => setFilterState('ALL')}
            className={`flex-1 py-1 px-2 rounded text-center transition-colors ${
              filterState === 'ALL' ? 'bg-white text-slate-900 shadow-2xs font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All ({queue.length})
          </button>
          <button
            onClick={() => setFilterState('SUBMITTED')}
            className={`flex-1 py-1 px-2 rounded text-center transition-colors ${
              filterState === 'SUBMITTED' ? 'bg-white text-slate-900 shadow-2xs font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Submitted ({queue.filter((q) => q.status === 'SUBMITTED_FOR_REVIEW').length})
          </button>
          <button
            onClick={() => setFilterState('REVISION')}
            className={`flex-1 py-1 px-2 rounded text-center transition-colors ${
              filterState === 'REVISION' ? 'bg-white text-slate-900 shadow-2xs font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Revision ({queue.filter((q) => q.status === 'REQUIRES_REVISION').length})
          </button>
          <button
            onClick={() => setFilterState('FINALIZED')}
            className={`flex-1 py-1 px-2 rounded text-center transition-colors ${
              filterState === 'FINALIZED' ? 'bg-white text-slate-900 shadow-2xs font-semibold' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Finalized ({queue.filter((q) => q.status === 'FINALIZED').length})
          </button>
        </div>
      </div>

      {/* Queue Content */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="flex items-center space-x-2 text-slate-400 text-sm">
            <div className="w-4 h-4 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
            <span>Loading review queue...</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700">{error}</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-lg py-14 text-center shadow-xs">
          <FileCheck className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-700">No inspection cases in review queue</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            {search
              ? 'Try adjusting your search criteria.'
              : 'When inspectors complete verification and submit cases for review, they will appear here for statutory adjudication.'}
          </p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-slate-700 font-sans font-semibold text-[11px] border-b border-slate-200 uppercase">
              <tr>
                <th className="py-3 px-4 w-36">Case Number</th>
                <th className="py-3 px-4 min-w-[200px]">Product & Origin</th>
                <th className="py-3 px-4 w-36">Inspector</th>
                <th className="py-3 px-4 w-40">Status</th>
                <th className="py-3 px-4 w-44">Findings Summary</th>
                <th className="py-3 px-4 w-32 text-right">Evidence Req</th>
                <th className="py-3 px-4 w-24 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                  {/* Case Number */}
                  <td className="py-3 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                    <Link
                      to={`/inspections/${item.id}`}
                      className="text-slate-900 hover:text-blue-700 hover:underline"
                    >
                      {item.case_number}
                    </Link>
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                      {new Date(item.created_at).toLocaleDateString()}
                    </div>
                  </td>

                  {/* Product & Origin */}
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900 text-xs">{item.product_name}</div>
                    <div className="flex items-center space-x-2 mt-1">
                      <OriginBadge origin={item.origin_status} />
                      {item.product_category && (
                        <span className="text-[10px] text-slate-500 font-mono">
                          {item.product_category}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Inspector */}
                  <td className="py-3 px-4 text-slate-700 whitespace-nowrap">
                    <div className="flex items-center space-x-1 font-medium">
                      <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                      <span>{item.inspector_name || 'Inspector'}</span>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="py-3 px-4 whitespace-nowrap">
                    <StatusBadge status={item.status} />
                    {item.finalization_status === 'READ_ONLY' && (
                      <span className="ml-1.5 text-[9px] font-mono px-1.5 py-0.2 bg-emerald-50 text-emerald-800 border border-emerald-300 rounded font-bold">
                        IMMUTABLE
                      </span>
                    )}
                  </td>

                  {/* Findings Summary */}
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1 text-[10px] font-mono">
                      {item.summary_counts ? (
                        <>
                          {item.summary_counts.PASS ? (
                            <span className="px-1.5 py-0.2 bg-emerald-50 text-emerald-700 rounded border border-emerald-200">
                              {item.summary_counts.PASS} PASS
                            </span>
                          ) : null}
                          {item.summary_counts.POTENTIAL_NON_COMPLIANCE ? (
                            <span className="px-1.5 py-0.2 bg-orange-50 text-orange-700 rounded border border-orange-200 font-bold">
                              {item.summary_counts.POTENTIAL_NON_COMPLIANCE} WARN
                            </span>
                          ) : null}
                          {item.summary_counts.REQUIRES_REVIEW ? (
                            <span className="px-1.5 py-0.2 bg-amber-50 text-amber-700 rounded border border-amber-200">
                              {item.summary_counts.REQUIRES_REVIEW} REVIEW
                            </span>
                          ) : null}
                        </>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </div>
                  </td>

                  {/* Evidence Requests */}
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    {item.open_evidence_requests_count > 0 ? (
                      <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-50 text-amber-800 border border-amber-300">
                        <AlertTriangle className="w-3 h-3 text-amber-600" />
                        <span>{item.open_evidence_requests_count} OPEN</span>
                      </span>
                    ) : (
                      <span className="text-[11px] text-slate-400 font-mono">0 Open</span>
                    )}
                  </td>

                  {/* Action */}
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <Link
                      to={`/inspections/${item.id}`}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white text-[11px] font-semibold rounded transition-colors shadow-2xs"
                    >
                      <span>Review</span>
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ReviewQueuePage;
