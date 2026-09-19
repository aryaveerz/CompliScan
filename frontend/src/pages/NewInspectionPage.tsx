import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  PlusCircle,
  AlertCircle,
  Info,
  Globe,
  Building2,
  HelpCircle,
} from 'lucide-react';
import { api } from '../api/client';
import { OriginStatus } from '../types';

// DESIGN.md: light-mode form (#ffffff container, #cbd5e1 input borders, #1e293b primary button)

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

  const inputClass =
    'w-full px-3 py-2 bg-white border border-slate-300 rounded text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-800 focus:ring-1 focus:ring-slate-800 transition-colors';

  const labelClass = 'block text-xs font-medium text-slate-700 mb-1.5';

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
      {/* Back */}
      <Link
        to="/inspections"
        className="inline-flex items-center space-x-1.5 text-xs text-slate-500 hover:text-slate-900 mb-6 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Inspections</span>
      </Link>

      <div className="bg-white rounded-lg border border-slate-200 shadow-[0_1px_2px_rgba(15,23,42,0.05)] p-6 sm:p-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-lg font-bold text-slate-900 tracking-tight">Create Inspection Case</h1>
          <p className="text-xs text-slate-500 mt-1">
            Capture initial product context under Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-5 p-3 bg-red-50 border border-red-200 rounded flex items-center space-x-2 text-xs text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Product Name */}
          <div>
            <label className={labelClass}>
              Product Name / Common Brand Name{' '}
              <span className="text-red-500" aria-label="required">*</span>
            </label>
            <input
              type="text"
              required
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g., Parle-G Gold Glucose Biscuits 100g"
              className={inputClass}
            />
          </div>

          {/* Origin Status */}
          <div>
            <label className={labelClass}>
              Origin Status{' '}
              <span className="text-slate-400 font-normal">(Applicability Trigger)</span>{' '}
              <span className="text-red-500" aria-label="required">*</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {/* DOMESTIC */}
              <button
                type="button"
                onClick={() => setOriginStatus('DOMESTIC')}
                className={`p-3 rounded border text-left transition-colors ${
                  originStatus === 'DOMESTIC'
                    ? 'bg-[#1e293b] border-[#1e293b] text-white'
                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center space-x-1.5 text-xs font-semibold">
                  <Building2 className="w-3.5 h-3.5 shrink-0" />
                  <span>DOMESTIC</span>
                </div>
                <p className={`text-[10px] mt-0.5 ${originStatus === 'DOMESTIC' ? 'text-slate-300' : 'text-slate-400'}`}>
                  Made/Packed in India
                </p>
              </button>

              {/* IMPORTED */}
              <button
                type="button"
                onClick={() => setOriginStatus('IMPORTED')}
                className={`p-3 rounded border text-left transition-colors ${
                  originStatus === 'IMPORTED'
                    ? 'bg-[#1e293b] border-[#1e293b] text-white'
                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center space-x-1.5 text-xs font-semibold">
                  <Globe className="w-3.5 h-3.5 shrink-0" />
                  <span>IMPORTED</span>
                </div>
                <p className={`text-[10px] mt-0.5 ${originStatus === 'IMPORTED' ? 'text-slate-300' : 'text-slate-400'}`}>
                  Requires COO check
                </p>
              </button>

              {/* UNKNOWN */}
              <button
                type="button"
                onClick={() => setOriginStatus('UNKNOWN')}
                className={`p-3 rounded border text-left transition-colors ${
                  originStatus === 'UNKNOWN'
                    ? 'bg-[#1e293b] border-[#1e293b] text-white'
                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center space-x-1.5 text-xs font-semibold">
                  <HelpCircle className="w-3.5 h-3.5 shrink-0" />
                  <span>UNKNOWN</span>
                </div>
                <p className={`text-[10px] mt-0.5 ${originStatus === 'UNKNOWN' ? 'text-slate-300' : 'text-slate-400'}`}>
                  Determine in review
                </p>
              </button>
            </div>
          </div>

          {/* Category + Reference URL */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>
                Product Category{' '}
                <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Packaged Foods, Personal Care"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>
                Reference URL{' '}
                <span className="text-slate-400 font-normal">(Optional)</span>
              </label>
              <input
                type="text"
                value={referenceUrl}
                onChange={(e) => setReferenceUrl(e.target.value)}
                placeholder="https://brand.in/listing"
                className={inputClass}
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className={labelClass}>
              Inspector Notes{' '}
              <span className="text-slate-400 font-normal">(Optional)</span>
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record batch identifiers, market location, sampling details…"
              className={inputClass}
            />
          </div>

          {/* Info notice */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded flex items-start space-x-2 text-xs text-slate-600">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
            <span>
              Creating this case initializes the inspection workspace in{' '}
              <strong className="font-medium text-slate-700">DRAFT</strong> state. Next, you will
              upload primary package photographs.
            </span>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-[#1e293b] hover:bg-[#0f172a] disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-sm rounded flex items-center justify-center space-x-2 transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{loading ? 'Creating…' : 'Create Inspection & Proceed to Evidence'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
