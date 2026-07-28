import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDeployments, deleteDeployment, createDeployment, lancerDeployment } from '../api/deployments';
import { getProjects } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import '../style/deploiement.css';

const STATUT_LABELS = {
  EN_ATTENTE: 'En attente',
  EN_COURS: 'En cours',
  SUCCES: 'Déployé',
  ECHEC: 'Échoué',
};

const STATUT_CLASS = {
  EN_ATTENTE: 'statut-attente',
  EN_COURS: 'statut-cours',
  SUCCES: 'statut-succes',
  ECHEC: 'statut-echec',
};

function Deployments() {
  const navigate = useNavigate();
  const [deployments, setDeployments] = useState([]);
  const { logout } = useAuth();
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState('');
  const [creating, setCreating] = useState(false);

  const load = () => {
    getDeployments()
      .then((res) => setDeployments(res.data.results))
      .catch(() => setError('Impossible de charger les déploiements.'));
    getProjects()
      .then((res) => setProjects(res.data.results))
      .catch(() => {});
  };

  useEffect(() => {
    load();
  }, []);

  const stats = {
    applications: projects.length,
    serveurs: '—', // en attente des données d'Ackèklna
    reussis: deployments.filter((d) => d.statut === 'SUCCES').length,
    echoues: deployments.filter((d) => d.statut === 'ECHEC').length,
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Supprimer ce déploiement ?')) return;
    try {
      await deleteDeployment(id);
      setDeployments((prev) => prev.filter((d) => d.id !== id));
    } catch {
      setError('Échec de la suppression.');
    }
  };

  const handleLancer = async (id) => {
    try {
      await lancerDeployment(id);
      load();
    } catch (err) {
      const msg = err.response?.data?.error || 'Impossible de lancer le déploiement.';
      setError(msg);
    }
  };

  const handleCreate = async () => {
    if (!selectedProject) return;
    setCreating(true);
    try {
      await createDeployment({ projet: selectedProject });
      setShowNewModal(false);
      setSelectedProject('');
      load();
    } catch (err) {
      const msg = err.response?.data
        ? Object.values(err.response.data).flat().join(' ')
        : 'Erreur lors du lancement du déploiement.';
      setError(msg);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="dep-layout">
      <aside className="dep-sidebar">
        <div className="dep-logo"><span className="dep-logo-dot"></span> Tableau de bord</div>
        <div className="dep-search"><input type="text" placeholder="Search for..." /></div>
        <nav className="dep-nav">
          <p className="dep-nav-title">Dashboard</p>
          <ul>
            <li onClick={() => navigate('/dashboard')}>Projets</li>
            <li onClick={() => navigate('/projets/nouveau')}>Création de projet</li>
            <li className="active">Configuration du déploiement</li>
            <li onClick={() => navigate('/generateur')}>Générateur DevOps</li>
            <li onClick={() => navigate('/logs')}>Logs</li>
          </ul>
          <p className="dep-nav-title">Infrastructure</p>
          <ul>
            <li onClick={() => navigate('/hyperviseurs')}>Hyperviseurs</li>
            <li onClick={() => navigate('/infrastructure')}>Provisionnement</li>
          </ul>
        </nav>
        <button className="dep-logout" onClick={() => {
          logout();
          navigate('/');
        }}>Logout </button>
      </aside>

      <main className="dep-main">
        <div className="dep-header">
          <h1>Welcome back</h1>
          <button className="dep-new-btn" onClick={() => setShowNewModal(true)}>
            Lancer un déploiement ↓
          </button>
        </div>

        {error && <p className="dep-error">{error}</p>}

        <div className="dep-stats">
          <div className="dep-stat-card">
            <span className="dep-stat-label">Applications</span>
            <span className="dep-stat-value">{stats.applications}</span>
          </div>
          <div className="dep-stat-card">
            <span className="dep-stat-label">Serveurs</span>
            <span className="dep-stat-value">{stats.serveurs}</span>
          </div>
          <div className="dep-stat-card">
            <span className="dep-stat-label">Déploiements réussis</span>
            <span className="dep-stat-value ok">{stats.reussis}</span>
          </div>
          <div className="dep-stat-card">
            <span className="dep-stat-label">Déploiements échoués</span>
            <span className="dep-stat-value fail">{stats.echoues}</span>
          </div>
        </div>

        <section className="dep-table-card">
          <h2>Déploiements récents</h2>
          <table className="dep-table">
            <thead>
              <tr>
                <th>Projet</th>
                <th>Date</th>
                <th>Statut</th>
                <th>Commit</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {deployments.map((d) => (
                <tr key={d.id}>
                  <td>{d.projet_nom}</td>
                  <td>{new Date(d.date_heure).toLocaleString()}</td>
                  <td>
                    <span className={`dep-badge ${STATUT_CLASS[d.statut]}`}>
                      {STATUT_LABELS[d.statut]}
                    </span>
                  </td>
                  <td>{d.commit_hash || '—'}</td>
                  <td className="dep-actions">
                    {d.statut === 'EN_ATTENTE' && (
                      <button title="Lancer le déploiement" onClick={() => handleLancer(d.id)}>Run</button>
                    )}
                    <button title="Voir les logs" onClick={() => navigate(`/deploiements/${d.id}`)}>Logs</button>
                    <button title="Supprimer" onClick={() => handleDelete(d.id)}>Del</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {showNewModal && (
          <div className="dep-modal-overlay" onClick={() => setShowNewModal(false)}>
            <div className="dep-modal" onClick={(e) => e.stopPropagation()}>
              <h3>Lancer un déploiement</h3>
              <label>Choisir un projet</label>
              <select value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)}>
                <option value="">Sélectionner </option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.nom}</option>
                ))}
              </select>
              <div className="dep-modal-actions">
                <button onClick={() => setShowNewModal(false)}>Annuler</button>
                <button className="dep-modal-confirm" onClick={handleCreate} disabled={creating || !selectedProject}>
                  {creating ? 'Lancement...' : 'Lancer'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Deployments;