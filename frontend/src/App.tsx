import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import AppLayout from './components/layout/AppLayout';
import LoadingSpinner from './components/ui/LoadingSpinner';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ProtocolListPage from './pages/ProtocolListPage';
import ProtocolBuilderPage from './pages/ProtocolBuilderPage';
import ProtocolDetailPage from './pages/ProtocolDetailPage';
import ProtocolReviewPage from './pages/ProtocolReviewPage';
import EvidenceExplorerPage from './pages/EvidenceExplorerPage';
import SafetyCheckPage from './pages/SafetyCheckPage';
import PersonalizationPage from './pages/PersonalizationPage';
import AuditLogPage from './pages/AuditLogPage';
import PlaceholderPage from './pages/PlaceholderPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner size="lg" className="mt-20" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="protocols" element={<ProtocolListPage />} />
        <Route path="protocols/new" element={<ProtocolBuilderPage />} />
        <Route path="protocols/:id" element={<ProtocolDetailPage />} />
        <Route path="protocols/:id/review" element={<ProtocolReviewPage />} />
        <Route path="evidence" element={<EvidenceExplorerPage />} />
        <Route path="safety" element={<SafetyCheckPage />} />
        <Route path="personalization" element={<PersonalizationPage />} />

        {/* V2 placeholders */}
        <Route path="patients" element={<PlaceholderPage />} />
        <Route path="patients/:id" element={<PlaceholderPage />} />
        <Route path="patients/:id/eeg" element={<PlaceholderPage />} />

        <Route path="admin/audit" element={<AuditLogPage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
