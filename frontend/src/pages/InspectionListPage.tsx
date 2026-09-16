import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, Search, FileText, ArrowRight, Image as ImageIcon, Calendar } from 'lucide-react';
import { InspectionCase } from '../types';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatusBadge, OriginBadge } from '../components/StatusBadge';

export const InspectionListPage: React.FC = () => {
  const { user } = useAuth();
  const [inspections, setInspections] = useState<InspectionCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInspections = async () => {
      try {
        const data = await api.listInspections();
        setInspections(data.items);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch inspections');
      } finally {
        setLoading(false);
      }
    };
    fetchInspections();
  }, []);

  const filtered = inspections.filter(
    (item) =>
      item.product_name.toLowerCase().includes(search.toLowerCase()) ||
      item.case_number.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">Inspection Repository</h1>
          <p className="text-sm text-slate-400 mt-1">
            {user?.role === 'INSPECTOR'
              ? 'Manage your active inspection cases and evidence submissions.'
              : 'Review queue and compliance case audits.'}
          </p>
        </div>

        {user?.role === 'INSPECTOR' && (
          <Link
            to="/inspections/new"
            className="inline-flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-600/20 transition-all hover:scale-[1.02]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create New Inspection</span>
          </Link>
        )}
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Cases</div>
          <div className="text-3xl font-extrabold text-white mt-2 font-mono">{inspections.length}</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Draft Status</div>
          <div className="text-3xl font-extrabold text-slate-300 mt-2 font-mono">
            {inspections.filter((i) => i.status === 'DRAFT').length}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Evidence Uploaded</div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">
            {inspections.filter((i) => i.status === 'EVIDENCE_UPLOADED').length}
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6 relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter cases by product name or case number..."
          className="w-full pl-10 pr-4 py-2.5 bg-slate-900/60 border border-slate-800 focus:border-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
        />
      </div>

      {/* List / Table */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 text-sm">Loading inspection cases...</div>
      ) : error ? (
        <div className="p-4 bg-rose-950/40 border border-rose-900 rounded-xl text-rose-300 text-sm">{error}</div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">No inspection cases found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {search ? 'Try adjusting your search terms.' : 'Create your first inspection case to begin capturing evidence.'}
          </p>
          {!search && user?.role === 'INSPECTOR' && (
            <Link
              to="/inspections/new"
              className="inline-flex items-center space-x-2 mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Create Inspection</span>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {filtered.map((item) => (
            <Link
              key={item.id}
              to={`/inspections/${item.id}`}
              className="glass-panel p-5 rounded-2xl border border-slate-800/90 hover:border-emerald-500/40 hover:bg-slate-900/60 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
            >
              <div className="space-y-1.5 flex-1 min-w-0">
                <div className="flex items-center space-x-2.5">
                  <span className="font-mono text-xs font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/40">
                    {item.case_number}
                  </span>
                  <StatusBadge status={item.status} />
                  <OriginBadge origin={item.origin_status} />
                </div>

                <h3 className="text-base font-bold text-white truncate group-hover:text-emerald-300 transition-colors">
                  {item.product_name}
                </h3>

                {item.product_category && (
                  <p className="text-xs text-slate-400 font-medium">{item.product_category}</p>
                )}
              </div>

              <div className="flex items-center space-x-6 shrink-0 sm:border-l sm:border-slate-800/80 sm:pl-6 text-xs text-slate-400">
                <div className="flex items-center space-x-1.5" title="Evidence Artifacts">
                  <ImageIcon className="w-4 h-4 text-slate-500" />
                  <span className="font-mono font-medium text-slate-300">{item.evidence_assets.length} images</span>
                </div>

                <div className="flex items-center space-x-1.5 hidden md:flex" title="Creation Date">
                  <Calendar className="w-4 h-4 text-slate-500" />
                  <span>{new Date(item.created_at).toLocaleDateString()}</span>
                </div>

                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};
