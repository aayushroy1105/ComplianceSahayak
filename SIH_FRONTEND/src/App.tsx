import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import ProtectedRoute from './components/layout/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';

// Auth
import LoginPage from './pages/auth/LoginPage';

// User Pages
import UserDashboard from './pages/user/UserDashboard';
import NewScan from './pages/user/NewScan';
import ScanHistory from './pages/user/ScanHistory';
import UserReportView from './pages/user/UserReportView';

// Officer Pages
import OfficerDashboard from './pages/officer/OfficerDashboard';
import NewInspection from './pages/officer/NewInspection';
import InspectionDetail from './pages/officer/InspectionDetail';
import OfficerHistory from './pages/officer/OfficerHistory';
import Manufacturers from './pages/officer/ManufacturerRepeat';
import Analytics from './pages/officer/Analytics';
import MapPage from './pages/officer/Map';
import OfficerReports from './pages/officer/OfficerReports';
import ComplianceRules from './pages/officer/ComplianceRules';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* User Routes (/app/user) */}
        <Route element={<ProtectedRoute allowedRoles={['USER']} />}>
          <Route path="/app/user" element={<AppLayout role="user" />}>
            <Route index element={<Navigate to="/app/user/dashboard" replace />} />
            <Route path="dashboard" element={<UserDashboard />} />
            <Route path="scan/new" element={<NewScan />} />
            <Route path="scan" element={<ScanHistory />} />
            <Route path="reports/:id" element={<UserReportView />} />
          </Route>
        </Route>

        {/* Scan redirects for legacy/shortcut paths */}
        <Route path="/app/scans" element={<Navigate to="/app/user/scan" replace />} />
        <Route path="/app/scan" element={<Navigate to="/app/user/scan" replace />} />
        <Route path="/app/user/scans" element={<Navigate to="/app/user/scan" replace />} />

        {/* Officer Routes (/app) */}
        <Route element={<ProtectedRoute allowedRoles={['OFFICER', 'ADMIN']} />}>
          <Route path="/app" element={<AppLayout role="officer" />}>
            <Route index element={<OfficerDashboard />} />
            <Route path="inspection/new" element={<NewInspection />} />
            <Route path="inspection/:id" element={<InspectionDetail />} />
            <Route path="history" element={<OfficerHistory />} />
            <Route path="manufacturer" element={<Manufacturers />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="map" element={<MapPage />} />
            <Route path="reports" element={<OfficerReports />} />
            <Route path="rules" element={<ComplianceRules />} />
          </Route>
        </Route>
      </Routes>
    </Router>
    </AuthProvider>
  );
}

export default App;
