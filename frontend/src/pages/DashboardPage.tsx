import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  PlusCircle,
  Search,
  ArrowRight,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Inbox,
  ShieldCheck,
  Scale,
  Globe,
} from 'lucide-react';
import { InspectionCase, DashboardMetricsResponse } from '../types';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/StatusBadge';

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return 'N/A';
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}

interface MetricCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  accent?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  icon,
  accent = 'text-slate-900',
}) => (
  <div className="bg-white border border-slate-200 rounded-lg p-5 flex items-start space-x-4 shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
    <div className="w-9 h-9 rounded bg-slate-50 border border-slate-200 flex items-center justify-center shrink-0 text-slate-500">
      {icon}
    </div>
    <div className="min-w-0">
      <div className={`text-2xl font-bold tabular-nums leading-none ${accent}`}>{value}</div>
      <div className="text-xs text-slate-600 mt-1 font-medium truncate">{label}</div>
      {subtitle && <div className="text-[11px] text-slate-400 mt-0.5">{subtitle}</div>}
    </div>
  </div>
);

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [metrics, setMetrics] = useState<DashboardMetricsResponse | null>(null);
  const [recentInspections, setRecentInspections] = useState<InspectionCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [metricsData, listData] = await Promise.all([
        api.getDashboardMetrics({
          date_range: dateRange,
          category: selectedCategory || undefined,
        }),
        api.listInspections(),
      ]);
      setMetrics(metricsData);
      setRecentInspections(listData.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load operational dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange, selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/inspections?q=${encodeURIComponent(search.trim())}`);
    } else {
      navigate('/inspections');
    }
  };

  // Needs Attention items
  const attentionItems = recentInspections
    .filter((i) => i.status === 'REQUIRES_REVISION' || i.status === 'IN_VERIFICATION')
    .slice(0, 5);

  const topRecentItems = recentInspections.slice(0, 8);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* ── Page Header ──────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Scale className="w-5 h-5 text-slate-800" />
            Operational & Compliance Intelligence
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Operational Legal Metrology inspection throughput, statutory pass rates, and governance metrics.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {/* Quick Search */}
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search repository…"
              className="pl-8 pr-3 py-2 bg-white border border-slate-300 rounded text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-800 focus:ring-1 focus:ring-slate-800 w-48 transition-colors"
            />
          </form>

          {/* New Inspection — INSPECTOR only */}
          {user?.role === 'INSPECTOR' && (
            <Link
              to="/inspections/new"
              className="inline-flex items-center space-x-1.5 px-3 py-2 bg-[#1e293b] hover:bg-[#0f172a] text-white text-xs font-semibold rounded transition-colors shadow-xs"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>New Inspection</span>
            </Link>
          )}
        </div>
      </div>

      {/* ── Time Horizon & Category Filters ───────────────────── */}
      <div className="bg-white border border-slate-200 rounded-lg p-3.5 flex flex-wrap items-center justify-between gap-3 shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-md text-xs font-medium">
          {(['7d', '30d', '90d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setDateRange(range)}
              className={`px-3 py-1 rounded transition-colors cursor-pointer ${
                dateRange === range
                  ? 'bg-white text-slate-900 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {range === '7d' ? 'Last 7 Days' : range === '30d' ? 'Last 30 Days' : range === '90d' ? 'Last 90 Days' : 'All Time'}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-500 font-medium">Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded px-2.5 py-1 text-slate-800 focus:outline-none focus:border-slate-800 text-xs"
          >
            <option value="">All Categories</option>
            <option value="Food & Beverages">Food & Beverages</option>
            <option value="Dry Fruits">Dry Fruits</option>
            <option value="Cosmetics & Personal Care">Cosmetics & Personal Care</option>
            <option value="Electronics & Appliances">Electronics & Appliances</option>
            <option value="Pharmaceuticals & Health">Pharmaceuticals & Health</option>
          </select>
        </div>
      </div>

      {/* ── Loading / Error ───────────────────────────────────── */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center space-x-2 text-slate-400 text-sm">
            <div className="w-4 h-4 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
            <span>Calculating live database compliance aggregations…</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      ) : metrics ? (
        <>
          {/* ── Core KPI Cards ────────────────────────────────── */}
          <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <MetricCard
              label="Total Cases in Scope"
              value={metrics.total_inspections}
              subtitle={`${metrics.active_inspections} active workflows`}
              icon={<FileText className="w-4 h-4" />}
              accent="text-slate-900"
            />
            <MetricCard
              label="Awaiting Verification"
              value={metrics.in_verification_count}
              subtitle="Inspector verification stage"
              icon={<Clock className="w-4 h-4" />}
              accent="text-amber-700"
            />
            <MetricCard
              label="Reviewer Queue"
              value={metrics.submitted_for_review_count}
              subtitle={`${metrics.requires_revision_count} returned for revision`}
              icon={<Inbox className="w-4 h-4" />}
              accent="text-blue-700"
            />
            <MetricCard
              label="Statutory Compliance Rate"
              value={`${metrics.compliance_rate_percent}%`}
              subtitle={`${metrics.total_finalized} finalized dockets`}
              icon={<ShieldCheck className="w-4 h-4 text-emerald-600" />}
              accent="text-emerald-700"
            />
          </section>

          {/* ── Middle Row: Compliance Outcomes & Rule Violations ─ */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 1. Final Statutory Adjudication Distribution */}
            <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Final Statutory Decisions ({metrics.total_finalized} Finalized)</span>
                <span className="text-[11px] font-mono text-slate-500 lowercase font-normal">
                  source: final_audit_records
                </span>
              </h2>

              <div className="space-y-3">
                {/* Compliant */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-semibold text-emerald-800">Compliant (PASS)</span>
                    <span className="font-mono text-slate-700">
                      {metrics.compliance_distribution['COMPLIANT'] || 0} cases (
                      {metrics.total_finalized > 0
                        ? Math.round(((metrics.compliance_distribution['COMPLIANT'] || 0) / metrics.total_finalized) * 100)
                        : 0}
                      %)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-emerald-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          metrics.total_finalized > 0
                            ? ((metrics.compliance_distribution['COMPLIANT'] || 0) / metrics.total_finalized) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>

                {/* Non-Compliant Confirmed */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-semibold text-rose-800">Confirmed Violations (Non-Compliant)</span>
                    <span className="font-mono text-slate-700">
                      {metrics.compliance_distribution['NON_COMPLIANCE_CONFIRMED'] || 0} cases (
                      {metrics.total_finalized > 0
                        ? Math.round(
                            ((metrics.compliance_distribution['NON_COMPLIANCE_CONFIRMED'] || 0) /
                              metrics.total_finalized) *
                              100
                          )
                        : 0}
                      %)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-rose-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          metrics.total_finalized > 0
                            ? ((metrics.compliance_distribution['NON_COMPLIANCE_CONFIRMED'] || 0) /
                                metrics.total_finalized) *
                              100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>

                {/* Inconclusive */}
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-semibold text-amber-800">Inconclusive (Evidence Deficient)</span>
                    <span className="font-mono text-slate-700">
                      {metrics.compliance_distribution['INCONCLUSIVE'] || 0} cases (
                      {metrics.total_finalized > 0
                        ? Math.round(
                            ((metrics.compliance_distribution['INCONCLUSIVE'] || 0) / metrics.total_finalized) * 100
                          )
                        : 0}
                      %)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-amber-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          metrics.total_finalized > 0
                            ? ((metrics.compliance_distribution['INCONCLUSIVE'] || 0) / metrics.total_finalized) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Origin Breakdown */}
              <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-slate-900">
                    {metrics.origin_distribution['DOMESTIC'] || 0}
                  </div>
                  <div className="text-[11px] text-slate-500 flex items-center justify-center gap-1 mt-0.5">
                    <Globe className="w-3 h-3 text-slate-400" />
                    Domestic
                  </div>
                </div>
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-slate-900">
                    {metrics.origin_distribution['IMPORTED'] || 0}
                  </div>
                  <div className="text-[11px] text-slate-500 flex items-center justify-center gap-1 mt-0.5">
                    <Globe className="w-3 h-3 text-blue-500" />
                    Imported
                  </div>
                </div>
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-slate-900">
                    {metrics.origin_distribution['UNKNOWN'] || 0}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">Unknown</div>
                </div>
              </div>
            </div>

            {/* 2. Top Statutory Non-Compliance Citations */}
            <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Top Statutory Rule Non-Compliance Citations</span>
                <span className="text-[11px] font-mono text-slate-500 lowercase font-normal">
                  PCR 2011 Rules
                </span>
              </h2>

              {Object.keys(metrics.rule_violation_counts).length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-500">
                  <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                  No statutory rule violations recorded in this time horizon.
                </div>
              ) : (
                <div className="space-y-3">
                  {Object.entries(metrics.rule_violation_counts).map(([citation, count]) => (
                    <div key={citation} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-medium text-slate-800">{citation}</span>
                        <span className="font-mono font-bold text-rose-700">{count} citations</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-rose-500 h-2 rounded-full"
                          style={{
                            width: `${Math.min(100, (count / Math.max(...Object.values(metrics.rule_violation_counts))) * 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Reviewer Governance KPIs */}
              <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-slate-900">
                    {formatDuration(metrics.governance_metrics.avg_review_turnaround_seconds)}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Avg Turnaround</div>
                </div>
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-rose-700">
                    {metrics.governance_metrics.revision_count}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Revisions</div>
                </div>
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-amber-700">
                    {metrics.governance_metrics.correction_count}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Corrections</div>
                </div>
                <div className="p-2 bg-slate-50 rounded border border-slate-100">
                  <div className="font-mono font-bold text-purple-700">
                    {metrics.governance_metrics.override_count}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Overrides</div>
                </div>
              </div>
            </div>
          </div>

          {/* ── Needs Attention Section ───────────────────────── */}
          {attentionItems.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                <span>Needs Your Attention</span>
              </h2>
              <div className="bg-white border border-slate-200 rounded-lg divide-y divide-slate-100 shadow-[0_1px_2px_rgba(15,23,42,0.05)]">
                {attentionItems.map((item) => (
                  <Link
                    key={item.id}
                    to={`/inspections/${item.id}`}
                    className="flex items-center justify-between px-4 py-3 hover:bg-slate-50 transition-colors group"
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <span className="font-mono text-xs text-slate-500 shrink-0">{item.case_number}</span>
                      <span className="text-sm font-medium text-slate-800 truncate">{item.product_name}</span>
                      <StatusBadge status={item.status} />
                    </div>
                    <div className="flex items-center space-x-3 shrink-0 ml-4">
                      <span className="text-xs text-slate-400 tabular-nums hidden sm:block">
                        {formatDate(item.updated_at)}
                      </span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-slate-600 transition-colors" />
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* ── Recent Inspections ────────────────────────────── */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Recent Inspection Cases
              </h2>
              <Link
                to="/inspections"
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold transition-colors flex items-center gap-1"
              >
                <span>Search Full Repository</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

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
                        Updated
                      </th>
                      <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {topRecentItems.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-4 py-3 font-mono text-xs text-slate-600 whitespace-nowrap font-medium">
                          {item.case_number}
                        </td>
                        <td className="px-4 py-3 max-w-[200px]">
                          <span className="text-sm font-medium text-slate-800 truncate block">
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
                          <span className="text-xs text-slate-400 tabular-nums whitespace-nowrap">
                            {formatDate(item.updated_at)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
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
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
};
