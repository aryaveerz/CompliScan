import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  PlusCircle,
  Search,
  FileText,
  ArrowRight,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { InspectionSearchResultItem } from '../types';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatusBadge, OriginBadge } from '../components/StatusBadge';

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export const InspectionListPage: React.FC = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  // Search state
  const [search, setSearch] = useState(searchParams.get('q') ?? '');
  const [category, setCategory] = useState(searchParams.get('category') ?? '');
  const [status, setStatus] = useState(searchParams.get('status') ?? '');
  const [origin, setOrigin] = useState(searchParams.get('origin') ?? '');
  const [compliance, setCompliance] = useState(searchParams.get('compliance') ?? '');
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);

  // Data state
  const [items, setItems] = useState<InspectionSearchResultItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.searchInspections({
        q: search.trim() || undefined,
        category: category || undefined,
        status: status || undefined,
        origin: origin || undefined,
        compliance: compliance || undefined,
        page,
        page_size: 10,
        sort_by: 'created_at',
        sort_order: 'desc',
      });
      setItems(res.items);
      setTotalCount(res.total_count);
      setTotalPages(res.total_pages);
    } catch (err: any) {
      setError(err.message || 'Failed to search inspection repository');
    } finally {
      setLoading(false);
    }
  };

  // Debounced search trigger
  useEffect(() => {
    const handler = setTimeout(() => {
      fetchResults();
    }, 250);
    return () => clearTimeout(handler);
  }, [search, category, status, origin, compliance, page]);

  const handleResetFilters = () => {
    setSearch('');
    setCategory('');
    setStatus('');
    setOrigin('');
    setCompliance('');
    setPage(1);
  };

  const hasActiveFilters = Boolean(search || category || status || origin || compliance);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Inspection Repository & Archive
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {user?.role === 'INSPECTOR'
              ? 'Multi-parameter search and audit archive for your assigned inspection dockets.'
              : 'Regulatory inspection search, reviewer queue, and immutable audit archive.'}
          </p>
        </div>

        {user?.role === 'INSPECTOR' && (
          <Link
            to="/inspections/new"
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-[#1e293b] hover:bg-[#0f172a] text-white text-xs font-semibold rounded transition-colors shrink-0 shadow-xs"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Inspection</span>
          </Link>
        )}
      </div>

      {/* Filter Controls Bar */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-[0_1px_2px_rgba(15,23,42,0.05)] space-y-3">
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Text Search */}
          <div className="relative flex-1 w-full">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search by case number, product name, or category…"
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-300 rounded text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-800 focus:bg-white transition-colors"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {/* Category */}
            <select
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setPage(1);
              }}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-2 text-slate-800 focus:outline-none focus:border-slate-800 text-xs shrink-0"
            >
              <option value="">All Categories</option>
              <option value="Food & Beverages">Food & Beverages</option>
              <option value="Dry Fruits">Dry Fruits</option>
              <option value="Cosmetics & Personal Care">Cosmetics & Personal Care</option>
              <option value="Electronics & Appliances">Electronics & Appliances</option>
              <option value="Pharmaceuticals & Health">Pharmaceuticals & Health</option>
            </select>

            {/* Status */}
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setPage(1);
              }}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-2 text-slate-800 focus:outline-none focus:border-slate-800 text-xs shrink-0"
            >
              <option value="">All States</option>
              <option value="DRAFT">DRAFT</option>
              <option value="IN_VERIFICATION">IN_VERIFICATION</option>
              <option value="SUBMITTED_FOR_REVIEW">SUBMITTED_FOR_REVIEW</option>
              <option value="REQUIRES_REVISION">REQUIRES_REVISION</option>
              <option value="FINALIZED">FINALIZED</option>
            </select>

            {/* Origin */}
            <select
              value={origin}
              onChange={(e) => {
                setOrigin(e.target.value);
                setPage(1);
              }}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-2 text-slate-800 focus:outline-none focus:border-slate-800 text-xs shrink-0"
            >
              <option value="">All Origins</option>
              <option value="DOMESTIC">DOMESTIC</option>
              <option value="IMPORTED">IMPORTED</option>
            </select>

            {/* Compliance Outcome */}
            <select
              value={compliance}
              onChange={(e) => {
                setCompliance(e.target.value);
                setPage(1);
              }}
              className="bg-slate-50 border border-slate-300 rounded px-2.5 py-2 text-slate-800 focus:outline-none focus:border-slate-800 text-xs shrink-0"
            >
              <option value="">All Outcomes</option>
              <option value="COMPLIANT">COMPLIANT</option>
              <option value="NON_COMPLIANCE_CONFIRMED">VIOLATIONS CONFIRMED</option>
              <option value="INCONCLUSIVE">INCONCLUSIVE</option>
            </select>

            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                className="px-2.5 py-2 text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1 border border-slate-200 rounded hover:bg-slate-50 transition-colors cursor-pointer"
                title="Reset all search filters"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>

        {/* Results Metadata bar */}
        <div className="flex items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-100">
          <div>
            Showing <span className="font-semibold text-slate-800">{items.length}</span> of{' '}
            <span className="font-semibold text-slate-800">{totalCount}</span> total inspection dockets
          </div>
          <div className="font-mono text-[11px] text-slate-400">
            Page {page} of {totalPages}
          </div>
        </div>
      </div>

      {/* Results Table */}
      {loading ? (
        <div className="flex items-center justify-center py-20 bg-white border border-slate-200 rounded-lg">
          <div className="flex items-center space-x-2 text-slate-400 text-sm">
            <div className="w-4 h-4 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
            <span>Searching repository…</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      ) : items.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-lg py-16 text-center shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
          <FileText className="w-9 h-9 text-slate-300 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-700">No matching inspection records found</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
            {hasActiveFilters
              ? 'Try relaxing your search terms or filter combinations.'
              : 'Create your first inspection case to begin capturing evidence.'}
          </p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider font-mono">
                    Case #
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Product / Commodity
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">
                    Category
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Origin
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Lifecycle State
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">
                    Final Adjudication
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">
                    Created
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-700 whitespace-nowrap font-medium">
                      {item.case_number}
                    </td>
                    <td className="px-4 py-3 max-w-[200px]">
                      <span className="text-sm font-medium text-slate-900 truncate block">
                        {item.product_name}
                      </span>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-xs text-slate-600 font-medium">
                        {item.product_category ?? '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <OriginBadge origin={item.origin_status} />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      {item.final_decision ? (
                        <span
                          className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded border ${
                            item.final_decision === 'COMPLIANT'
                              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                              : item.final_decision === 'NON_COMPLIANT_CONFIRMED'
                              ? 'bg-rose-50 text-rose-800 border-rose-300'
                              : 'bg-amber-50 text-amber-800 border-amber-300'
                          }`}
                        >
                          {item.final_decision.replace(/_/g, ' ')}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400 font-mono">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      <span className="text-xs text-slate-500 tabular-nums whitespace-nowrap">
                        {formatDate(item.created_at)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <Link
                        to={`/inspections/${item.id}`}
                        className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                      >
                        <span>Open</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="inline-flex items-center space-x-1 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Previous</span>
              </button>

              <div className="text-xs text-slate-600 font-medium">
                Page <span className="font-bold text-slate-900">{page}</span> of{' '}
                <span className="font-bold text-slate-900">{totalPages}</span>
              </div>

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="inline-flex items-center space-x-1 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:pointer-events-none transition-colors cursor-pointer"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
