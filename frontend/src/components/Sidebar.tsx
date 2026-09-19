import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FolderOpen, PlusCircle, Clock, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

// DESIGN.md: bg-white, slate-200 border-r, quiet nav.
// Active: dark navy bg (#1e293b) white text. Inactive: slate-600, hover slate-50.

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
  inspectorOnly?: boolean;
  reviewerOnly?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  {
    to: '/dashboard',
    icon: <LayoutDashboard className="w-4 h-4" />,
    label: 'Dashboard',
  },
  {
    to: '/inspections',
    icon: <FolderOpen className="w-4 h-4" />,
    label: 'Inspections',
  },
  {
    to: '/inspections/new',
    icon: <PlusCircle className="w-4 h-4" />,
    label: 'New Inspection',
    inspectorOnly: true,
  },
  {
    to: '/reviews',
    icon: <Shield className="w-4 h-4" />,
    label: 'Review Queue',
    reviewerOnly: true,
  },
  {
    to: '/history',
    icon: <Clock className="w-4 h-4" />,
    label: 'History',
  },
];

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();

  return (
    <aside className="w-56 shrink-0 bg-white border-r border-slate-200 flex flex-col overflow-y-auto">
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          // Hide INSPECTOR-only items for non-inspectors
          if (item.inspectorOnly && user?.role !== 'INSPECTOR') return null;
          // Hide REVIEWER-only items for non-reviewers
          if (item.reviewerOnly && user?.role !== 'REVIEWER') return null;

          // Exact match for /dashboard; prefix match for others to avoid /inspections
          // matching /inspections/new simultaneously
          const isActive =
            item.to === '/dashboard'
              ? location.pathname === '/dashboard'
              : item.to === '/inspections'
              ? location.pathname === '/inspections'
              : location.pathname.startsWith(item.to);

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={[
                'flex items-center space-x-2.5 px-3 py-2 rounded text-sm transition-colors',
                isActive
                  ? 'bg-[#1e293b] text-white'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              ].join(' ')}
            >
              <span className={isActive ? 'text-white' : 'text-slate-400'}>{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom rule — keeps sidebar visually grounded */}
      <div className="px-3 pb-3">
        <div className="border-t border-slate-100" />
      </div>
    </aside>
  );
};
