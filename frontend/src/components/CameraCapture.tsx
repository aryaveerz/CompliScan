import React, { useState, useEffect, useRef } from 'react';
import { Camera, RefreshCw, Check, X, AlertCircle, FlipHorizontal, ShieldCheck } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onClose: () => void;
}

export const CameraCapture: React.FC<CameraCaptureProps> = ({ onCapture, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedBlob, setCapturedBlob] = useState<Blob | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [hasMultipleCameras, setHasMultipleCameras] = useState(false);
  const [isStartingCamera, setIsStartingCamera] = useState(true);

  // Check if multiple camera devices exist
  useEffect(() => {
    const checkDevices = async () => {
      try {
        if (!navigator.mediaDevices?.enumerateDevices) return;
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter((d) => d.kind === 'videoinput');
        setHasMultipleCameras(videoDevices.length > 1);
      } catch {
        // Ignore device enumeration errors
      }
    };
    checkDevices();
  }, []);

  // Stop camera tracks helper
  const stopTracks = (mediaStream: MediaStream | null) => {
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => {
        track.stop();
      });
    }
  };

  // Start camera stream
  const startCamera = async (mode: 'environment' | 'user') => {
    setIsStartingCamera(true);
    setError(null);

    // Stop current stream if running
    if (stream) {
      stopTracks(stream);
      setStream(null);
    }

    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('Camera access is not supported by your browser or requires a secure context (HTTPS/localhost).');
      }

      let newStream: MediaStream;
      try {
        newStream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: mode },
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          },
          audio: false,
        });
      } catch (err: any) {
        // If ideal facingMode fails, try basic video request
        newStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      }

      setStream(newStream);
      if (videoRef.current) {
        videoRef.current.srcObject = newStream;
        await videoRef.current.play();
      }
    } catch (err: any) {
      console.error('Camera initialization error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('Camera permission was denied. Please allow camera permissions in your browser or device settings.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError('No compatible camera device found on this system.');
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setError('Camera is currently in use by another application.');
      } else {
        setError(err.message || 'Unable to access camera.');
      }
    } finally {
      setIsStartingCamera(false);
    }
  };

  // Effect to initialize camera on mount or facingMode change (when not in preview mode)
  useEffect(() => {
    if (!capturedBlob) {
      startCamera(facingMode);
    }
    return () => {
      // Cleanup on unmount
      if (stream) {
        stopTracks(stream);
      }
    };
  }, [facingMode]);

  // Clean up object URLs
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // Handle Capture button click
  const handleTakeSnapshot = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0, width, height);

    // Convert to JPEG blob
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setError('Failed to capture image snapshot from camera.');
          return;
        }

        // Stop live stream while reviewing
        if (stream) {
          stopTracks(stream);
          setStream(null);
        }

        const url = URL.createObjectURL(blob);
        setCapturedBlob(blob);
        setPreviewUrl(url);
      },
      'image/jpeg',
      0.92
    );
  };

  // Handle Retake button click
  const handleRetake = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setCapturedBlob(null);
    setError(null);
    startCamera(facingMode);
  };

  // Handle Accept Photo button click
  const handleAccept = () => {
    if (!capturedBlob) return;

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `camera_capture_${timestamp}.jpg`;
    const file = new File([capturedBlob], filename, { type: 'image/jpeg' });

    // Clean up tracks and object URLs before calling onCapture
    if (stream) {
      stopTracks(stream);
    }
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    onCapture(file);
  };

  // Toggle camera between environment and user
  const handleToggleCamera = () => {
    const nextMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextMode);
  };

  const handleClose = () => {
    if (stream) {
      stopTracks(stream);
    }
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 sm:p-6 animate-fadeIn">
      {/* Hidden canvas for snapshot rendering */}
      <canvas ref={canvasRef} className="hidden" />

      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-2xl w-full flex flex-col overflow-hidden text-slate-100 max-h-[90vh]">
        {/* Header */}
        <div className="px-5 py-3.5 bg-slate-800/80 border-b border-slate-700/80 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight">
                {previewUrl ? 'Review Captured Packaging Evidence' : 'Camera Evidence Acquisition'}
              </h3>
              <p className="text-[11px] text-slate-400">
                {previewUrl
                  ? 'Verify sharpness and legibility of statutory text before committing.'
                  : 'Align commodity packaging or label within viewfinder.'}
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700/60 rounded-lg transition-colors"
            title="Close camera"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Viewport / Content Area */}
        <div className="relative bg-black flex-1 min-h-[360px] sm:min-h-[440px] flex items-center justify-center overflow-hidden">
          {error ? (
            <div className="p-6 max-w-md text-center">
              <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto mb-3">
                <AlertCircle className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-rose-200 mb-1">Camera Acquisition Error</h4>
              <p className="text-xs text-rose-300 leading-relaxed mb-4">{error}</p>
              <div className="flex items-center justify-center space-x-3">
                <button
                  onClick={() => startCamera(facingMode)}
                  className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg text-white border border-slate-600 transition-colors flex items-center space-x-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Retry Camera</span>
                </button>
                <button
                  onClick={handleClose}
                  className="px-3.5 py-1.5 bg-slate-700 hover:bg-slate-600 text-xs font-semibold rounded-lg text-white transition-colors"
                >
                  Use File Upload Instead
                </button>
              </div>
            </div>
          ) : previewUrl ? (
            /* Review Preview Mode */
            <div className="relative w-full h-full flex items-center justify-center bg-slate-950 p-2">
              <img
                src={previewUrl}
                alt="Captured packaging evidence preview"
                className="max-h-[500px] w-auto max-w-full object-contain rounded border border-slate-800 shadow-lg"
              />
              <div className="absolute top-4 right-4 bg-slate-900/90 backdrop-blur-md border border-slate-700 px-3 py-1 rounded-full text-xs text-emerald-400 flex items-center space-x-1.5 font-mono shadow-sm">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Ready for SHA-256 Hashing</span>
              </div>
            </div>
          ) : (
            /* Live Camera Viewfinder Mode */
            <div className="relative w-full h-full flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-contain max-h-[500px]"
              />

              {/* Viewfinder Target Framing Guides */}
              <div className="absolute inset-8 sm:inset-12 pointer-events-none border border-white/20 rounded-lg flex flex-col justify-between p-3">
                <div className="flex justify-between">
                  <div className="w-6 h-6 border-t-2 border-l-2 border-emerald-400 rounded-tl" />
                  <div className="w-6 h-6 border-t-2 border-r-2 border-emerald-400 rounded-tr" />
                </div>
                <div className="text-center">
                  <span className="px-2.5 py-1 rounded-full bg-slate-900/70 backdrop-blur-sm text-[11px] text-slate-300 font-mono border border-slate-700/50">
                    Align PDP / Statutory Labels Inside Frame
                  </span>
                </div>
                <div className="flex justify-between">
                  <div className="w-6 h-6 border-b-2 border-l-2 border-emerald-400 rounded-bl" />
                  <div className="w-6 h-6 border-b-2 border-r-2 border-emerald-400 rounded-br" />
                </div>
              </div>

              {isStartingCamera && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center space-x-2 text-xs text-slate-300">
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>Connecting to camera hardware...</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Controls */}
        <div className="px-5 py-3.5 bg-slate-800/80 border-t border-slate-700/80 flex items-center justify-between">
          {previewUrl ? (
            /* Preview Action Buttons */
            <div className="w-full flex items-center justify-between">
              <button
                onClick={handleRetake}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs font-semibold flex items-center space-x-2 transition-colors border border-slate-600"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retake Photo</span>
              </button>

              <button
                onClick={handleAccept}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-2 transition-colors shadow-sm"
              >
                <Check className="w-4 h-4" />
                <span>Accept & Ingest Evidence</span>
              </button>
            </div>
          ) : (
            /* Live Capture Controls */
            <div className="w-full flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {hasMultipleCameras && (
                  <button
                    onClick={handleToggleCamera}
                    disabled={isStartingCamera || !!error}
                    className="px-3 py-1.5 bg-slate-700/70 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-medium flex items-center space-x-1.5 border border-slate-600/70 transition-colors disabled:opacity-40"
                    title="Switch front/rear camera"
                  >
                    <FlipHorizontal className="w-3.5 h-3.5" />
                    <span>Flip Camera</span>
                  </button>
                )}
                <span className="text-[11px] text-slate-400 font-mono hidden sm:inline">
                  Mode: {facingMode === 'environment' ? 'Rear (Environment)' : 'Front (User)'}
                </span>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleClose}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  Cancel
                </button>

                <button
                  onClick={handleTakeSnapshot}
                  disabled={isStartingCamera || !!error}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white rounded-lg text-xs font-bold flex items-center space-x-2 transition-all shadow-md disabled:opacity-40 disabled:pointer-events-none"
                >
                  <Camera className="w-4 h-4" />
                  <span>Take Photo</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
