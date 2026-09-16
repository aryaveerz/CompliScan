import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  User,
  ExternalLink,
  Cpu,
  CheckCircle2,
  FileCheck2,
  FileSpreadsheet,
  AlertCircle,
} from 'lucide-react';
import { InspectionCase, EvidenceAsset } from '../types';
import { api } from '../api/client';
import { StatusBadge, OriginBadge } from '../components/StatusBadge';
import { EvidenceUploader } from '../components/EvidenceUploader';

export const InspectionWorkspacePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [inspection, setInspection] = useState<InspectionCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInspection = async () => {
    if (!id) return;
    try {
      const data = await api.getInspection(id);
      setInspection(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load inspection case');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspection();
  }, [id]);

  const handleEvidenceUploaded = (newAsset: EvidenceAsset) => {
    if (!inspection) return;
    setInspection({
      ...inspection,
      status: 'EVIDENCE_UPLOADED',
      evidence_assets: [...inspection.evidence_assets, newAsset],
    });
  };

  const handleEvidenceDeleted = (evidenceId: string) => {
    if (!inspection) return;
    setInspection({
      ...inspection,
      evidence_assets: inspection.evidence_assets.filter((a) => a.id !== evidenceId),
    });
  };

  if (loading) {
    return <div className="max-w-7xl mx-auto p-8 text-center text-slate-500 text-sm">Loading inspection workspace...</div>;
  }

  if (error || !inspection) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="p-4 bg-rose-950/40 border border-rose-900 rounded-xl text-rose-300 text-sm mb-4">
          {error || 'Inspection not found'}
        </div>
        <Link to="/inspections" className="text-xs text-emerald-400 hover:underline">
          Return to Inspections
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Breadcrumb & Case Bar */}
      <div>
        <Link
          to="/inspections"
          className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Inspections</span>
        </Link>

        <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2.5">
              <span className="font-mono text-sm font-extrabold text-emerald-400 bg-emerald-950/60 px-2.5 py-0.5 rounded border border-emerald-800/40">
                {inspection.case_number}
              </span>
              <StatusBadge status={inspection.status} />
              <OriginBadge origin={inspection.origin_status} />
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">{inspection.product_name}</h1>
          </div>

          <div className="flex items-center space-x-6 text-xs text-slate-400">
            <div className="flex items-center space-x-1.5">
              <User className="w-4 h-4 text-slate-500" />
              <span>Inspector: {inspection.created_by?.full_name || 'Assigned'}</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <Calendar className="w-4 h-4 text-slate-500" />
              <span>{new Date(inspection.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Lifecycle Stepper */}
      <div className="glass-card rounded-xl p-4 border border-slate-800 overflow-x-auto">
        <div className="flex items-center justify-between min-w-[700px] text-xs font-semibold text-slate-400">
          <div className="flex items-center space-x-2 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span>1. Product Context</span>
          </div>
          <div className="h-0.5 w-12 bg-emerald-500/40"></div>
          <div
            className={`flex items-center space-x-2 ${
              inspection.evidence_assets.length > 0 ? 'text-emerald-400' : 'text-blue-400'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>2. Evidence Capture</span>
          </div>
          <div className="h-0.5 w-12 bg-slate-800"></div>
          <div className="flex items-center space-x-2 text-slate-600">
            <Cpu className="w-4 h-4" />
            <span>3. OCR & AI Perception (Phase 2)</span>
          </div>
          <div className="h-0.5 w-12 bg-slate-800"></div>
          <div className="flex items-center space-x-2 text-slate-600">
            <FileSpreadsheet className="w-4 h-4" />
            <span>4. Rule Evaluation (Phase 3)</span>
          </div>
          <div className="h-0.5 w-12 bg-slate-800"></div>
          <div className="flex items-center space-x-2 text-slate-600">
            <FileCheck2 className="w-4 h-4" />
            <span>5. Review & Finalize (Phase 4)</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Product Context Details */}
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-3">
              Product Context
            </h3>

            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase">Product Name</span>
              <p className="text-sm font-semibold text-white mt-0.5">{inspection.product_name}</p>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase">Origin Status</span>
              <div className="mt-1">
                <OriginBadge origin={inspection.origin_status} />
              </div>
            </div>

            {inspection.product_category && (
              <div>
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Category</span>
                <p className="text-xs text-slate-300 mt-0.5">{inspection.product_category}</p>
              </div>
            )}

            {inspection.reference_url && (
              <div>
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Reference URL</span>
                <a
                  href={inspection.reference_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-emerald-400 hover:underline flex items-center space-x-1 mt-0.5 truncate"
                >
                  <span className="truncate">{inspection.reference_url}</span>
                  <ExternalLink className="w-3 h-3 shrink-0" />
                </a>
              </div>
            )}

            {inspection.notes && (
              <div>
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Notes</span>
                <p className="text-xs text-slate-300 mt-0.5 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                  {inspection.notes}
                </p>
              </div>
            )}
          </div>

          {/* Phase Boundary Notice */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 text-xs text-slate-400 space-y-2">
            <div className="flex items-center space-x-2 text-slate-200 font-bold">
              <AlertCircle className="w-4 h-4 text-emerald-400" />
              <span>Phase 1 Architectural Invariant</span>
            </div>
            <p className="text-[11px] leading-relaxed text-slate-400">
              In Phase 1, primary evidence is stored with verifiable SHA-256 integrity. Perception (PaddleOCR) and Semantic Extraction (Gemini 2.5 Flash) will be integrated behind dedicated worker pipelines in Phase 2 & Phase 3.
            </p>
          </div>
        </div>

        {/* Right Column: Evidence Assets Manager */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
          <EvidenceUploader
            inspectionId={inspection.id}
            evidenceAssets={inspection.evidence_assets}
            onUploadSuccess={handleEvidenceUploaded}
            onDeleteSuccess={handleEvidenceDeleted}
          />
        </div>
      </div>
    </div>
  );
};
