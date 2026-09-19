import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileSpreadsheet, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// DESIGN.md: light-mode header — bg-white, slate-200 border.
// Navigation lives in Sidebar. Header owns: brand identity + user info + logout.

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const roleLabel =
    user?.role === 'INSPECTOR' ? 'Inspector' : user?.role === 'REVIEWER' ? 'Reviewer' : user?.role ?? '';

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 h-14 flex items-center">
      <div className="w-full px-4 sm:px-6 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 bg-[#0f172a] text-white rounded flex items-center justify-center shrink-0">
            <FileSpreadsheet className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-900 leading-tight">CompliScan LM</div>
            <div className="text-[10px] text-slate-500 leading-none mt-0.5 hidden sm:block">
              Legal Metrology Compliance Workspace
            </div>
          </div>
        </div>

        {/* User block */}
        {user && (
          <div className="flex items-center space-x-3">
            {/* Name + role */}
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-slate-800 leading-tight">{user.full_name}</div>
              <div className="text-[10px] text-slate-500 mt-0.5">{roleLabel}</div>
            </div>

            {/* Avatar initial */}
            <div className="w-7 h-7 rounded bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0">
              <span className="text-xs font-semibold text-slate-600">
                {user.full_name?.charAt(0)?.toUpperCase() ?? '?'}
              </span>
            </div>

            {/* Divider */}
            <div className="h-4 w-px bg-slate-200" />

            {/* Logout */}
            <button
              onClick={handleLogout}
              title="Sign out"
              className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
