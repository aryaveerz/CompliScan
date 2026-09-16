import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, PlusCircle, ShieldAlert, Info, Globe, Building2, HelpCircle } from 'lucide-react';
import { api } from '../api/client';
import { OriginStatus } from '../types';

export const NewInspectionPage: React.FC = () => {
  const navigate = useNavigate();
  const [productName, setProductName] = useState('');
  const [originStatus, setOriginStatus] = useState<OriginStatus>('DOMESTIC');
  const [category, setCategory] = useState('');
  const [referenceUrl, setReferenceUrl] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName.trim()) {
      setError('Product Name is required.');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const created = await api.createInspection({
        product_name: productName.trim(),
        origin_status: originStatus,
        product_category: category.trim() || undefined,
        reference_url: referenceUrl.trim() || undefined,
        notes: notes.trim() || undefined,
      });
      navigate(`/inspections/${created.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create inspection case');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back button */}
      <Link
        to="/inspections"
        className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Inspections</span>
      </Link>

      <div className="glass-panel rounded-2xl p-8 border border-slate-800 shadow-2xl">
        <div className="mb-6">
          <h1 className="text-xl font-extrabold text-white">Create Inspection Case</h1>
          <p className="text-xs text-slate-400 mt-1">
            Capture initial Product Context under Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3.5 bg-rose-950/50 border border-rose-800/60 rounded-xl flex items-center space-x-2 text-xs text-rose-300">
            <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Product Name */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Product Name / Common Brand Name <span className="text-emerald-400">*</span>
            </label>
            <input
              type="text"
              required
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g., Parle-G Gold Glucose Biscuits 100g"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 focus:border-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          {/* Origin Status */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Origin Status (Applicability Trigger) <span className="text-emerald-400">*</span>
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setOriginStatus('DOMESTIC')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  originStatus === 'DOMESTIC'
                    ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-1.5 font-bold text-xs">
                  <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>DOMESTIC</span>
                </div>
                <p className="text-[10px] text-slate-500 mt-1">Made/Packed in India</p>
              </button>

              <button
                type="button"
                onClick={() => setOriginStatus('IMPORTED')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  originStatus === 'IMPORTED'
                    ? 'bg-amber-950/80 border-amber-500 text-amber-300 ring-1 ring-amber-500'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-1.5 font-bold text-xs">
                  <Globe className="w-3.5 h-3.5 text-amber-400" />
                  <span>IMPORTED</span>
                </div>
                <p className="text-[10px] text-slate-500 mt-1">Requires COO check</p>
              </button>

              <button
                type="button"
                onClick={() => setOriginStatus('UNKNOWN')}
                className={`p-3 rounded-xl border text-left transition-all ${
                  originStatus === 'UNKNOWN'
                    ? 'bg-slate-800 border-slate-500 text-slate-200 ring-1 ring-slate-500'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-1.5 font-bold text-xs">
                  <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                  <span>UNKNOWN</span>
                </div>
                <p className="text-[10px] text-slate-500 mt-1">Determine in review</p>
              </button>
            </div>
          </div>

          {/* Product Category & Reference URL */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Product Category <span className="text-slate-500 font-normal">(Optional Metadata)</span>
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Packaged Foods, Personal Care"
                className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 focus:border-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Reference / URL <span className="text-slate-500 font-normal">(Optional Metadata)</span>
              </label>
              <input
                type="text"
                value={referenceUrl}
                onChange={(e) => setReferenceUrl(e.target.value)}
                placeholder="e.g. https://brand.in/listing"
                className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 focus:border-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
              Inspector Notes <span className="text-slate-500 font-normal">(Optional)</span>
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record batch identifiers, market location, sampling details..."
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 focus:border-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-[11px] text-slate-400 flex items-start space-x-2">
            <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>
              Creating this case initializes the inspection workspace in <strong>DRAFT</strong> state. Next, you will upload primary package photographs.
            </span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-bold text-sm rounded-xl shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/30 flex items-center justify-center space-x-2 transition-all hover:scale-[1.01]"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{loading ? 'Creating Inspection...' : 'Create Inspection & Proceed to Evidence'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
