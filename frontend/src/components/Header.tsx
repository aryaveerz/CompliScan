import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, UserCheck, LogOut, PlusCircle, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Name */}
          <div className="flex items-center space-x-3">
            <Link to="/inspections" className="flex items-center space-x-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform duration-200">
                <ShieldCheck className="w-6 h-6 text-slate-950 font-bold" />
              </div>
              <div>
                <div className="flex items-center space-x-1.5">
                  <span className="font-extrabold text-lg text-white tracking-tight">CompliScan</span>
                  <span className="px-1.5 py-0.2 bg-emerald-500/20 text-emerald-400 text-xs font-mono font-bold rounded border border-emerald-500/30">LM</span>
                </div>
                <p className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">Legal Metrology Compliance</p>
              </div>
            </Link>
          </div>

          {/* Navigation & User Menu */}
          {user && (
            <div className="flex items-center space-x-4">
              <nav className="flex items-center space-x-1">
                <Link
                  to="/inspections"
                  className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Inspections</span>
                </Link>

                {user.role === 'INSPECTOR' && (
                  <Link
                    to="/inspections/new"
                    className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20 transition-all hover:scale-[1.02]"
                  >
                    <PlusCircle className="w-4 h-4" />
                    <span>New Inspection</span>
                  </Link>
                )}
              </nav>

              <div className="h-6 w-px bg-slate-800"></div>

              {/* User Profile */}
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-semibold text-slate-200">{user.full_name}</div>
                  <div className="text-[11px] font-mono text-emerald-400 font-medium flex items-center justify-end space-x-1">
                    <UserCheck className="w-3 h-3" />
                    <span>{user.role}</span>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  title="Logout"
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 rounded-lg border border-transparent hover:border-rose-900/50 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
