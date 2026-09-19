import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Eye, EyeOff, FileSpreadsheet } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between font-sans">
      {/* Top Bar Header */}
      <header className="px-6 py-4 border-b border-slate-200/60 bg-white/50 backdrop-blur-xs flex items-center space-x-3">
        <div className="w-6 h-6 bg-[#0f172a] text-white rounded flex items-center justify-center shrink-0">
          <FileSpreadsheet className="w-3.5 h-3.5" />
        </div>
        <div className="flex items-center space-x-2 text-xs font-sans">
          <span className="font-bold text-slate-900">CompliScan LM</span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-500 font-medium">Legal Metrology Compliance Workspace</span>
        </div>
      </header>

      {/* Main Centered Auth Card Container */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-4xl bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden grid grid-cols-1 md:grid-cols-2">
          {/* Left Column: Brand Statement */}
          <div className="p-8 md:p-10 bg-slate-50/70 border-b md:border-b-0 md:border-r border-slate-200/80 flex flex-col justify-between space-y-8">
            <div className="space-y-6">
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 bg-[#0f172a] text-white rounded-lg flex items-center justify-center shadow-xs">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="font-bold text-slate-900 text-base leading-tight">CompliScan LM</h2>
                  <p className="text-xs text-slate-500">Legal Metrology Compliance Workspace</p>
                </div>
              </div>

              <div className="w-8 h-1 bg-blue-600 rounded-full" />

              <div className="space-y-3">
                <h3 className="text-xl font-bold text-slate-900 tracking-tight leading-snug">
                  Evidence-driven inspection and verification for packaged commodity compliance.
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Capture evidence. Verify declarations. Maintain an auditable inspection record.
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-normal font-sans pt-4">
              Designed for authorized legal metrology inspection officers and verified verifiers.
            </p>
          </div>

          {/* Right Column: Form */}
          <div className="p-8 md:p-10 bg-white flex flex-col justify-center">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Welcome back</h2>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">Sign in to your CompliScan workspace.</p>
            </div>

            {error && (
              <div className="mb-5 p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center space-x-2 text-xs text-rose-700">
                <ShieldAlert className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Email address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@domain.gov.in"
                  className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-800 focus:ring-1 focus:ring-slate-800 transition-colors font-sans"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-3.5 pr-10 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-800 focus:ring-1 focus:ring-slate-800 transition-colors font-sans"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1 transition-colors"
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-2 py-1">
                <input
                  type="checkbox"
                  id="rememberMe"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-slate-800 focus:ring-slate-800 cursor-pointer"
                />
                <label htmlFor="rememberMe" className="text-xs text-slate-600 cursor-pointer select-none">
                  Remember me
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 bg-[#1e293b] hover:bg-[#0f172a] disabled:bg-slate-300 text-white font-semibold text-sm rounded-lg shadow-xs flex items-center justify-center space-x-2 transition-colors cursor-pointer"
              >
                <span>{loading ? 'Authenticating...' : 'Sign in'}</span>
              </button>
            </form>

            <p className="text-center text-xs text-slate-400 mt-6 font-sans">
              Authorized access only.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-slate-400 font-sans">
        © CompliScan LM
      </footer>
    </div>
  );
};

export default LoginPage;
