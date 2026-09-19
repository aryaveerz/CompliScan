import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { InspectionListPage } from './pages/InspectionListPage';
import { NewInspectionPage } from './pages/NewInspectionPage';
import { InspectionWorkspacePage } from './pages/InspectionWorkspacePage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { HistoryPage } from './pages/HistoryPage';

// ── Protected Route ───────────────────────────────────────────────────────────

const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: string }> = ({
  children,
  requiredRole,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f8fafc]">
        <div className="flex items-center space-x-2.5 text-slate-500 text-sm">
          <div className="w-4 h-4 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
          <span>Initializing CompliScan…</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// ── Authenticated App Shell ───────────────────────────────────────────────────
//
// Layout:
//   ┌────────────────────────────────────────────────────┐
//   │  Header  (full-width top bar, sticky)              │
//   ├──────────────┬─────────────────────────────────────┤
//   │  Sidebar     │  Main content (scrollable)          │
//   │  (fixed)     │                                     │
//   └──────────────┴─────────────────────────────────────┘

const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex flex-col h-screen bg-[#f8fafc]">
    <Header />
    <div className="flex flex-1 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-[#f8fafc] cleanroom-scrollbar">{children}</main>
    </div>
  </div>
);

// ── App Content ───────────────────────────────────────────────────────────────

export const AppContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Authenticated — wrapped in AppShell */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AppShell>
              <DashboardPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="/inspections"
        element={
          <ProtectedRoute>
            <AppShell>
              <InspectionListPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="/inspections/new"
        element={
          <ProtectedRoute requiredRole="INSPECTOR">
            <AppShell>
              <NewInspectionPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="/inspections/:id"
        element={
          <ProtectedRoute>
            <AppShell>
              <InspectionWorkspacePage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="/reviews"
        element={
          <ProtectedRoute>
            <AppShell>
              <ReviewQueuePage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <AppShell>
              <HistoryPage />
            </AppShell>
          </ProtectedRoute>
        }
      />

      {/* Catch-all → dashboard */}
      <Route
        path="*"
        element={
          user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
        }
      />
    </Routes>
  );
};

// ── Root ──────────────────────────────────────────────────────────────────────

export const App: React.FC = () => (
  <BrowserRouter>
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  </BrowserRouter>
);

export default App;
