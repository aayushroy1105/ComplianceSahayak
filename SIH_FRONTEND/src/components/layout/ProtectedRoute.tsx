import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  allowedRoles: Array<'USER' | 'OFFICER' | 'ADMIN'>;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    // Redirect to the appropriate portal if they don't have the right role for this route
    if (user.role === 'USER') {
      return <Navigate to="/app/user/dashboard" replace />;
    } else {
      // OFFICER or ADMIN goes to main officer app
      return <Navigate to="/app" replace />;
    }
  }

  return <Outlet />;
};

export default ProtectedRoute;
