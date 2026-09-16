import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, LogIn, UserCheck, ShieldAlert, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';

export const LoginPage: React.FC = () => {
  const { login, loginAsDemo } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/inspections');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role: UserRole) => {
    setError(null);
    setLoading(true);
    try {
      await loginAsDemo(role);
      navigate('/inspections');
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[90vh] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      {/* Brand Header */}
      <div className="text-center mb-8 max-w-md">
        <div className="inline-flex p-3 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 shadow-xl shadow-emerald-500/20 mb-4 animate-bounce-slow">
          <ShieldCheck className="w-10 h-10 text-slate-950 font-bold" />
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          CompliScan <span className="text-emerald-400">LM</span>
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Legal Metrology (Packaged Commodities) Rules, 2011 Automated Inspection Platform
        </p>
        <div className="mt-2 inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-slate-800/80 text-slate-300 border border-slate-700">
          <span>Smart India Hackathon • PS ID 26034</span>
        </div>
      </div>

      {/* Main Login Card */}
      <div className="w-full max-w-md glass-panel rounded-2xl p-8 shadow-2xl border border-slate-800">
        {error && (
          <div className="mb-6 p-3.5 bg-rose-950/50 border border-rose-800/60 rounded-xl flex items-center space-x-2 text-xs text-rose-300">
            <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              Official Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="officer@compliscan.gov.in"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2.5 bg-slate-900/80 border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 rounded-xl text-sm text-white placeholder-slate-500 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-semibold text-sm rounded-xl shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/30 flex items-center justify-center space-x-2 transition-all hover:scale-[1.01]"
          >
            <LogIn className="w-4 h-4" />
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
          </button>
        </form>

        {/* Quick Demo Access */}
        <div className="mt-8 pt-6 border-t border-slate-800">
          <div className="flex items-center justify-center space-x-1 text-xs text-slate-400 mb-3 font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>1-Click Test Access</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleDemoLogin('INSPECTOR')}
              disabled={loading}
              className="p-3 bg-slate-900/60 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/50 rounded-xl text-left transition-all group"
            >
              <div className="flex items-center space-x-1.5 text-xs font-bold text-emerald-400 group-hover:text-emerald-300">
                <UserCheck className="w-3.5 h-3.5" />
                <span>Inspector</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 truncate">Rajesh Sharma</p>
              <p className="text-[9px] text-slate-500 font-mono">Create & Upload</p>
            </button>

            <button
              type="button"
              onClick={() => handleDemoLogin('REVIEWER')}
              disabled={loading}
              className="p-3 bg-slate-900/60 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/50 rounded-xl text-left transition-all group"
            >
              <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-400 group-hover:text-indigo-300">
                <UserCheck className="w-3.5 h-3.5" />
                <span>Reviewer</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 truncate">Priya Patel</p>
              <p className="text-[9px] text-slate-500 font-mono">Review & Audit</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
