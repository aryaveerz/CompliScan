import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Clock,
  Search,
  ShieldCheck,
  Download,
  FileDown,
  X,
  History,
} from 'lucide-react';
import { InspectionSearchResultItem } from '../types';
import { api } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { AuditTimeline } from '../components/AuditTimeline';

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<InspectionSearchResultItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [activeTimelineId, setActiveTimelineId] = useState<string | null>(null);
  const [downloadingPdfId, setDownloadingPdfId] = useState<string | null>(null);
  const [downloadingDocxId, setDownloadingDocxId] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.searchInspections({
        q: search.trim() || undefined,
        page: 1,
        page_size: 50,
        sort_by: 'updated_at',
        sort_order: 'desc',
      });
      setItems(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load inspection history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handler = setTimeout(() => {
      fetchHistory();
    }, 250);
    return () => clearTimeout(handler);
  }, [search]);

  const handleDownloadPdf = async (item: InspectionSearchResultItem) => {
    try {
      setDownloadingPdfId(item.id);
      await api.downloadFinalPdfReport(item.id, item.case_number);
    } catch (err: any) {
      alert(err.message || 'Failed to download PDF report');
    } finally {
      setDownloadingPdfId(null);
    }
  };

  const handleDownloadDocx = async (item: InspectionSearchResultItem) => {
    try {
      setDownloadingDocxId(item.id);
      await api.downloadFinalDocxReport(item.id, item.case_number);
    } catch (err: any) {
      alert(err.message || 'Failed to download DOCX report');
    } finally {
      setDownloadingDocxId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="w-5 h-5 text-slate-800" />
            Inspection Activity & Audit History
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Full chronological archive with immutable chain-of-custody ledgers and official reports.
          </p>
        </div>

        {/* Quick Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search history…"
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-300 rounded text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-800 focus:ring-1 focus:ring-slate-800 transition-colors"
          />
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20 bg-white border border-slate-200 rounded-lg">
          <div className="flex items-center space-x-2 text-slate-400 text-sm">
            <div className="w-4 h-4 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
            <span>Loading history…</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      ) : items.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-lg py-16 text-center shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
          <Clock className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-500">No inspection history records found.</p>
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
                    State
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">
                    Last Updated
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Audit / Reports
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
                      <span className="text-xs text-slate-500">
                        {item.product_category ?? '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      <span className="text-xs text-slate-500 tabular-nums whitespace-nowrap">
                        {formatDate(item.updated_at)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end space-x-2">
                        {/* Audit Trail Button */}
                        <button
                          onClick={() => setActiveTimelineId(item.id)}
                          className="px-2 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/80 rounded border border-slate-200 transition-colors cursor-pointer"
                          title="View complete chain-of-custody audit trail"
                        >
                          Audit Log
                        </button>

                        {/* If finalized: direct download buttons */}
                        {item.status === 'FINALIZED' && (
                          <>
                            <button
                              onClick={() => handleDownloadPdf(item)}
                              disabled={downloadingPdfId === item.id}
                              className="p-1 text-emerald-700 hover:bg-emerald-50 rounded border border-emerald-200 transition-colors cursor-pointer"
                              title="Download Official PDF Report"
                            >
                              <Download className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDownloadDocx(item)}
                              disabled={downloadingDocxId === item.id}
                              className="p-1 text-blue-700 hover:bg-blue-50 rounded border border-blue-200 transition-colors cursor-pointer"
                              title="Download Official DOCX Report"
                            >
                              <FileDown className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}

                        {/* Open Docket */}
                        <Link
                          to={`/inspections/${item.id}`}
                          className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors ml-1"
                        >
                          <span>Open</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Slide-over Modal for Audit Timeline */}
      {activeTimelineId && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-slate-200">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-blue-700" />
                <h3 className="text-sm font-bold text-slate-900">
                  Chain-of-Custody Audit Trail
                </h3>
              </div>
              <button
                onClick={() => setActiveTimelineId(null)}
                className="p-1 text-slate-400 hover:text-slate-700 rounded-md hover:bg-slate-200/60 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto flex-1">
              <AuditTimeline inspectionId={activeTimelineId} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
