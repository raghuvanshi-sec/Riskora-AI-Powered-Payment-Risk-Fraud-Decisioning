import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import LoginView from './views/LoginView';
import LandingView from './views/LandingView';
import DashboardView from './views/DashboardView';
import TransactionsView from './views/TransactionsView';
import TransactionDetail from './views/TransactionDetail';
import RiskQueueView from './views/RiskQueueView';
import AlertsView from './views/AlertsView';
import AppNavbar from './components/AppNavbar';

function AuthenticatedLayout() {
  return (
    <div className="app-layout">
      <AppNavbar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<DashboardView />} />
          <Route path="/transactions" element={<TransactionsView />} />
          <Route path="/transactions/:transactionId" element={<TransactionDetail />} />
          <Route path="/risk-queue" element={<RiskQueueView />} />
          <Route path="/alerts" element={<AlertsView />} />
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingView />} />
        <Route path="/login" element={<LoginView />} />
        <Route path="/app/*" element={
          <ProtectedRoute>
            <AuthenticatedLayout />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
