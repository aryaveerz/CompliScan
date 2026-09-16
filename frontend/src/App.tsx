import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import { LoginPage } from './pages/LoginPage';
import { InspectionListPage } from './pages/InspectionListPage';
import { NewInspectionPage } from './pages/NewInspectionPage';
import { InspectionWorkspacePage } from './pages/InspectionWorkspacePage';

const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: string }> = ({
  children,
  requiredRole,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-500 text-sm">
        Initializing CompliScan Session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/inspections" replace />;
  }

  return <>{children}</>;
};

export const AppContent: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] text-slate-100">
      {user && <Header />}
      <main className="flex-1">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/inspections"
            element={
              <ProtectedRoute>
                <InspectionListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inspections/new"
            element={
              <ProtectedRoute requiredRole="INSPECTOR">
                <NewInspectionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inspections/:id"
            element={
              <ProtectedRoute>
                <InspectionWorkspacePage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/inspections" replace />} />
        </Routes>
      </main>
      <footer className="py-6 border-t border-slate-900 text-center text-xs text-slate-600 font-mono">
        CompliScan LM • Legal Metrology (Packaged Commodities) Rules, 2011 • PS ID 26034
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
