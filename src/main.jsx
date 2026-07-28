import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Landing from './pages/Landing.jsx';
import App from './App.jsx';
import Dashboard from './pages/Dashboard.jsx';
import ProjectForm from './pages/ProjectForm.jsx';
import Deployments from './pages/Deployments.jsx';
import Logs from './pages/Logs.jsx';
import AddServer from './pages/AddServer.jsx';
import SuiviDeploiement from './pages/SuiviDeploiement.jsx';
import DeploiementDetail from './pages/DeploiementDetail.jsx';
import ArtifactGenerator from './pages/ArtifactGenerator.jsx';
import Hyperviseurs from './pages/Hyperviseurs.jsx';
import Infrastructure from './pages/Infrastructure.jsx';
import History from './pages/History.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<App />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/projets/nouveau" element={<ProtectedRoute><ProjectForm /></ProtectedRoute>} />
          <Route path="/projets/:id/modifier" element={<ProtectedRoute><ProjectForm /></ProtectedRoute>} />
          <Route path="/deploiements" element={<ProtectedRoute><Deployments /></ProtectedRoute>} />
          <Route path="/deploiements/:id" element={<ProtectedRoute><DeploiementDetail /></ProtectedRoute>} />
          <Route path="/deploiements/:id/suivi" element={<ProtectedRoute><SuiviDeploiement /></ProtectedRoute>} />
          <Route path="/generateur" element={<ProtectedRoute><ArtifactGenerator /></ProtectedRoute>} />
          <Route path="/serveurs/nouveau" element={<ProtectedRoute><AddServer /></ProtectedRoute>} />
          <Route path="/logs" element={<ProtectedRoute><Logs /></ProtectedRoute>} />
          <Route path="/hyperviseurs" element={<ProtectedRoute><Hyperviseurs /></ProtectedRoute>} />
          <Route path="/infrastructure" element={<ProtectedRoute><Infrastructure /></ProtectedRoute>} />
          <Route path="/historique" element={<ProtectedRoute><History /></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);