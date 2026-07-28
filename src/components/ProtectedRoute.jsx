import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <p style={{ color: '#e5e0f0', textAlign: 'center', marginTop: 40 }}>Chargement...</p>;
  }

  if (!user) {
    if (!user) return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
