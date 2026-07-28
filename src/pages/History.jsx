import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getHistory, getHistoryDetail } from '../api/devops';
import '../style/History.css';

function History() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [records, setRecords] = useState([]);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    getHistory()
      .then(res => {
        const d = res.data;
        setRecords(d?.history || d?.results || (Array.isArray(d) ? d : []));
      })
      .catch(() => setError('Erreur chargement historique'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleViewDetail = async (id) => {
    try {
      const res = await getHistoryDetail(id);
      setSelected(res.data);
    } catch {
      setError('Erreur chargement détail');
    }
  };

  const formatDate = (s) => {
    if (!s) return '—';
    return new Date(s).toLocaleString('fr-FR');
  };

  return (
    <div className="hist-layout">
      <aside className="hist-sidebar">
        <div className="hist-logo">Historique</div>
        <nav className="hist-nav">
          <ul>
            <li className="active">Générations</li>
            <li onClick={() => navigate('/generateur')}>Générateur</li>
            <li onClick={() => navigate('/dashboard')}>Projets</li>
            <li onClick={() => navigate('/deploiements')}>Déploiements</li>
          </ul>
        </nav>
        <button className="hist-logout" onClick={() => { logout(); navigate('/'); }}>Logout →</button>
      </aside>

      <main className="hist-main">
        <div className="hist-header">
          <h1>Historique des générations</h1>
          <button className="hist-btn-primary" onClick={() => navigate('/generateur')}>
            + Nouvelle génération
          </button>
        </div>

        {error && <p className="hist-error">{error}</p>}
        {loading && <p className="hist-loading">Chargement...</p>}

        {!loading && records.length === 0 && (
          <div className="hist-empty">
            <p>Aucune génération enregistrée</p>
            <button onClick={() => navigate('/generateur')}>Générer des artifacts</button>
          </div>
        )}

        <div className="hist-table-card">
          <table className="hist-table">
            <thead>
              <tr>
                <th>Projet</th>
                <th>Framework</th>
                <th>Provider</th>
                <th>CI/CD</th>
                <th>Artifacts</th>
                <th>Statut</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {records.map(r => (
                <tr key={r.id}>
                  <td className="hist-bold">{r.project_name}</td>
                  <td><span className="hist-badge">{r.framework || '—'}</span></td>
                  <td>{r.provider || '—'}</td>
                  <td>{r.ci_platform || '—'}</td>
                  <td>
                    {r.artifacts_generated && Object.entries(r.artifacts_generated)
                      .filter(([, v]) => v)
                      .map(([k]) => (
                        <span key={k} className="hist-tag">{k}</span>
                      ))}
                  </td>
                  <td>
                    <span className={`hist-status ${r.status === 'SUCCESS' ? 'ok' : 'fail'}`}>
                      {r.status}
                    </span>
                  </td>
                  <td>{formatDate(r.created_at)}</td>
                  <td>
                    <button className="hist-btn-sm" onClick={() => handleViewDetail(r.id)}>
                      Détails
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {selected && (
          <div className="hist-detail-card">
            <div className="hist-detail-header">
              <h3>{selected.project_name} — {selected.framework}</h3>
              <button className="hist-btn-sm" onClick={() => setSelected(null)}>Fermer</button>
            </div>
            <div className="hist-detail-grid">
              <div><span>Provider</span><strong>{selected.provider || '—'}</strong></div>
              <div><span>CI/CD</span><strong>{selected.ci_platform || '—'}</strong></div>
              <div><span>Statut</span><strong>{selected.status}</strong></div>
              <div><span>Date</span><strong>{formatDate(selected.created_at)}</strong></div>
            </div>
            <div className="hist-detail-artifacts">
              <h4>Artifacts générés</h4>
              <div className="hist-detail-tags">
                {selected.artifacts_generated && Object.entries(selected.artifacts_generated)
                  .map(([key, val]) => (
                    <span key={key} className={`hist-tag ${val ? 'active' : 'inactive'}`}>
                      {key} {val ? '✓' : '✗'}
                    </span>
                  ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default History;
