import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDeployments } from '../api/deployment';
import { useAuth } from '../context/AuthContext';
import '../style/logs.css';

const NIVEAU_CLASS = {
  INFO: 'niveau-info',
  WARN: 'niveau-warn',
  ERROR: 'niveau-error',
};

function Logs() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const { logout } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    getDeployments()
      .then((res) => {
        // Chaque déploiement contient un tableau "journaux" -> on aplatit tout
        const allLogs = res.data.flatMap((dep) =>
          (dep.journaux || []).map((j) => ({
            ...j,
            projet_nom: dep.projet_nom,
            deploiement_id: dep.id,
          }))
        );
        // Tri du plus récent au plus ancien
        allLogs.sort((a, b) => new Date(b.horodatage) - new Date(a.horodatage));
        setLogs(allLogs);
      })
      .catch(() => setError('Impossible de charger les journaux.'))
      .finally(() => setLoading(false));
  }, []);

  const filteredLogs = logs.filter((l) =>
    `${l.projet_nom} ${l.message} ${l.source}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="log-layout">
      <aside className="log-sidebar">
        <div className="log-logo"><span className="log-logo-dot"></span> Tableau de bord</div>
        <div className="log-search"><input type="text" placeholder="Search for..." /></div>
        <nav className="log-nav">
          <p className="log-nav-title">Dashboard</p>
          <ul>
            <li onClick={() => navigate('/dashboard')}>Projets</li>
            <li onClick={() => navigate('/projets/nouveau')}>Création de projet</li>
            <li onClick={() => navigate('/deploiements')}>Configuration du déploiement</li>
            <li onClick={() => navigate('/generateur')}>Générateur DevOps</li>
            <li className="active">Logs</li>
          </ul>
          <p className="log-nav-title">Infrastructure</p>
          <ul>
            <li onClick={() => navigate('/hyperviseurs')}>Hyperviseurs</li>
            <li onClick={() => navigate('/infrastructure')}>Provisionnement</li>
          </ul>
        </nav>
        <button
          className="log-logout"
          onClick={() => {
            logout();
            navigate('/');
          }}
        >
          Logout →
        </button>
      </aside>

      <main className="log-main">
        <h1 className="log-welcome">Welcome</h1>

        <div className="log-search-bar">
          <input
            type="text"
            placeholder="Search for..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <h2 className="log-history-title">Historique des journalisations</h2>

        {error && <p className="log-error">{error}</p>}

        <section className="log-table-card">
          <div className="log-table-header">
            <h2>Logs</h2>
          </div>

          {loading ? (
            <p className="log-loading">Chargement...</p>
          ) : filteredLogs.length === 0 ? (
            <p className="log-empty">Aucun journal disponible pour le moment.</p>
          ) : (
            <table className="log-table">
              <thead>
                <tr>
                  <th></th>
                  <th>Projet</th>
                  <th>Source</th>
                  <th>Message</th>
                  <th>Niveau</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map((l) => (
                  <tr key={l.id}>
                    <td><input type="checkbox" /></td>
                    <td>{l.projet_nom}</td>
                    <td>{l.source || '—'}</td>
                    <td>{l.message}</td>
                    <td>
                      <span className={`log-badge ${NIVEAU_CLASS[l.niveau]}`}>
                        {l.niveau}
                      </span>
                    </td>
                    <td className="log-actions">
                      <button title="Voir le déploiement" onClick={() => navigate(`/deploiements/${l.deploiement_id}`)}>👁️</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}

export default Logs;