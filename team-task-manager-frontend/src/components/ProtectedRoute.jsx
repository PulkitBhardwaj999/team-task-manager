import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks';
import { LoadingSkeleton } from './Skeleton';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
