import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, deleteProject } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import HealthBanner from '../components/HealthBanner';
import '../style/dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState('');
  const { logout } = useAuth();

  const loadProjects = () => {
    getProjects()
      .then((res) => setProjects(res.data.results))
      .catch(() => setError('Impossible de charger les projets.'));
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer ce projet définitivement ?')) return;
    try {
      await deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch {
      setError('Échec de la suppression.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('username');
    navigate('/');
  };

  return (
    <div className="dash-layout">
      <aside className="dash-sidebar">
        <div className="dash-logo">
          <span className="dash-logo-dot"></span>
          Tableau de bord
        </div>

        <div className="dash-search">
          <input type="text" placeholder="Search for..." />
        </div>

        <nav className="dash-nav">
          <p className="dash-nav-title">Dashboard</p>
          <ul>
            <li>Projets</li>
            <li onClick={() => navigate('/projets/nouveau')}>Création de projet</li>
            <li onClick={() => navigate('/deploiements')}>Configuration du déploiement</li>
            <li onClick={() => navigate('/generateur')}>Générateur DevOps</li>
            <li onClick={() => navigate('/historique')}>Historique</li>
            <li onClick={() => navigate('/logs')}>Logs</li>
          </ul>

          <p className="dash-nav-title">Infrastructure</p>
          <ul>
            <li onClick={() => navigate('/hyperviseurs')}>Hyperviseurs</li>
            <li onClick={() => navigate('/infrastructure')}>Provisionnement</li>
            <li onClick={() => navigate('/serveurs/nouveau')}>Ajout Serveur</li>
          </ul>
        </nav>

        <button
          className="dash-logout"
          onClick={() => {
            logout();
            navigate('/');
          }}
        >
          Logout 
        </button>
      </aside>

      <main className="dash-main">
        <h1 className="dash-welcome">Welcome , {localStorage.getItem('username')}</h1>
        <HealthBanner />

        {error && <p style={{ color: '#e57373' }}>{error}</p>}

        <section className="dash-table-card">
          <div className="dash-table-header">
            <h2>Projets</h2>
            <button className="dash-new-project-btn" onClick={() => navigate('/projets/nouveau')}>
              Créer un projet
            </button>
          </div>

          <table className="dash-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Technologie</th>
                <th>Branche</th>
                <th>Date</th>
            
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id}>
                  <td>{p.nom}</td>
                  <td>{p.technologie}</td>
                  <td>{p.branche}</td>
                  <td>{new Date(p.date_creation).toLocaleDateString()}</td>
                  <td className="dash-actions">
                    <button title="Modifier" onClick={() => navigate(`/projets/${p.id}/modifier`)}>Edit</button>
                    <button title="Supprimer" onClick={() => handleDelete(p.id)}>Del</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;