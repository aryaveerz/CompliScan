import React, { useState, useRef, useEffect } from 'react';
import { Upload, Trash2, CheckCircle2, ShieldAlert, Copy, Check, Eye, Camera } from 'lucide-react';
import { EvidenceAsset } from '../types';
import { api } from '../api/client';
import { CameraCapture } from './CameraCapture';

interface EvidenceUploaderProps {
  inspectionId: string;
  evidenceAssets: EvidenceAsset[];
  onUploadSuccess: (asset: EvidenceAsset) => void;
  onDeleteSuccess: (evidenceId: string) => void;
  readOnly?: boolean;
}

export const EvidenceUploader: React.FC<EvidenceUploaderProps> = ({
  inspectionId,
  evidenceAssets,
  onUploadSuccess,
  onDeleteSuccess,
  readOnly = false,
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);
  const [selectedPreview, setSelectedPreview] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [cameraSupported, setCameraSupported] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setCameraSupported(Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
  }, []);

  const handleFiles = async (files: FileList | null | File[]) => {
    if (!files || (Array.isArray(files) ? files.length === 0 : files.length === 0)) return;
    setError(null);
    setUploading(true);

    const fileList = Array.isArray(files) ? files : Array.from(files);
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      try {
        const asset = await api.uploadEvidence(inspectionId, file, 'PRIMARY');
        onUploadSuccess(asset);
      } catch (err: any) {
        setError(err.message || `Failed to upload ${file.name}`);
      }
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDelete = async (evidenceId: string) => {
    if (!confirm('Are you sure you want to remove this draft evidence asset?')) return;
    try {
      await api.deleteEvidence(inspectionId, evidenceId);
      onDeleteSuccess(evidenceId);
    } catch (err: any) {
      alert(err.message || 'Failed to delete evidence');
    }
  };

  const copyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      {!readOnly && (
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            Upload Primary Evidence <span className="text-emerald-400">*</span>
          </label>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              handleFiles(e.dataTransfer.files);
            }}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 text-center cursor-pointer bg-slate-900/40 hover:bg-slate-900/80 transition-all duration-200 group"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFiles(e.target.files)}
              accept="image/jpeg,image/png,image/webp"
              multiple
              className="hidden"
            />
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3 group-hover:bg-emerald-500/20 group-hover:text-emerald-400 transition-colors text-slate-400">
                <Upload className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-slate-200 group-hover:text-white">
                {uploading ? 'Processing & Computing SHA-256 Hash...' : 'Click or Drag & Drop package photographs / labels'}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supported formats: JPEG, PNG, WebP (Max 15MB per image). Evaluates decodability and SHA-256 integrity upon upload.
              </p>
            </div>
          </div>

          {cameraSupported && (
            <div className="mt-2.5 flex justify-end">
              <button
                type="button"
                onClick={() => setShowCamera(true)}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 border border-slate-700 transition-colors"
              >
                <Camera className="w-3.5 h-3.5 text-emerald-400" />
                <span>Capture with Camera</span>
              </button>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="p-3 bg-rose-950/40 border border-rose-900/60 rounded-lg flex items-center space-x-2 text-xs text-rose-300">
          <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Evidence Assets List */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-400">
            Accepted Primary Evidence ({evidenceAssets.length})
          </h4>
          {evidenceAssets.length > 0 && (
            <span className="text-xs text-emerald-400 font-mono flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>SHA-256 Verified</span>
            </span>
          )}
        </div>

        {evidenceAssets.length === 0 ? (
          <div className="p-6 bg-slate-900/30 rounded-xl border border-slate-800 text-center text-xs text-slate-500">
            No evidence images uploaded yet. Please provide package photographs to proceed.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evidenceAssets.map((asset) => (
              <div
                key={asset.id}
                className="glass-card rounded-xl p-4 flex flex-col justify-between space-y-3 transition-all border border-slate-800 hover:border-slate-700"
              >
                <div className="flex space-x-3 items-start">
                  <div className="w-16 h-16 rounded-lg bg-slate-950 border border-slate-800 overflow-hidden shrink-0 flex items-center justify-center relative group">
                    <img
                      src={api.getEvidenceDownloadUrl(asset.id)}
                      alt={asset.original_filename}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback icon if image cannot be rendered directly
                        (e.target as HTMLElement).style.display = 'none';
                      }}
                    />
                    <button
                      onClick={() => setSelectedPreview(api.getEvidenceDownloadUrl(asset.id))}
                      className="absolute inset-0 bg-slate-950/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Eye className="w-5 h-5 text-white" />
                    </button>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40">
                        {asset.id}
                      </span>
                      <span className="text-[11px] text-slate-500 font-mono">{formatBytes(asset.file_size_bytes)}</span>
                    </div>

                    <p className="text-xs font-semibold text-slate-200 truncate mt-1" title={asset.original_filename}>
                      {asset.original_filename}
                    </p>

                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-[10px] uppercase font-mono px-1 bg-slate-800 text-slate-400 rounded">
                        {asset.mime_type.replace('image/', '')}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        {new Date(asset.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                </div>

                {/* SHA-256 Hash Display */}
                <div className="bg-slate-950/80 rounded p-2 border border-slate-800/80 text-[10px] font-mono">
                  <div className="flex items-center justify-between text-slate-500 mb-0.5">
                    <span>SHA-256 INTEGRITY HASH</span>
                    <button
                      onClick={() => copyHash(asset.sha256_hash)}
                      className="hover:text-emerald-400 transition-colors flex items-center space-x-1"
                      title="Copy full hash"
                    >
                      {copiedHash === asset.sha256_hash ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="text-slate-300 break-all select-all font-mono leading-tight">
                    {asset.sha256_hash}
                  </div>
                </div>

                {/* Actions */}
                {!readOnly && (
                  <div className="flex items-center justify-end pt-1">
                    <button
                      onClick={() => handleDelete(asset.id)}
                      className="text-xs text-slate-500 hover:text-rose-400 flex items-center space-x-1 transition-colors p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Remove Draft</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Image Lightbox Modal */}
      {selectedPreview && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setSelectedPreview(null)}
        >
          <div className="relative max-w-4xl max-h-[90vh] overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 p-2 shadow-2xl">
            <img src={selectedPreview} alt="Evidence Full Preview" className="max-h-[85vh] max-w-full object-contain rounded-lg" />
            <button
              onClick={() => setSelectedPreview(null)}
              className="absolute top-4 right-4 bg-slate-950/80 text-white rounded-full p-2 hover:bg-rose-600 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Camera Capture Modal */}
      {showCamera && (
        <CameraCapture
          onCapture={(file) => {
            setShowCamera(false);
            handleFiles([file]);
          }}
          onClose={() => setShowCamera(false)}
        />
      )}
    </div>
  );
};
