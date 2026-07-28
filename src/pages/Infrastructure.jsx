import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getEnvironments, createEnvironment,
  getDeploymentTargets, createDeploymentTarget, deleteDeploymentTarget,
  getHypervisors, getVirtualMachines,
  getDockerContainers,
  registerTargetFromVM, validateTarget, healthCheckTarget,
  disableTarget, enableTarget,
} from '../api/infrastructure';
import { getProjects } from '../api/projects';
import '../style/Infrastructure.css';

const TARGET_TYPES = [
  { value: 'VIRTUAL_MACHINE', label: 'Machine Virtuelle' },
  { value: 'DOCKER_CONTAINER', label: 'Conteneur Docker' },
  { value: 'KUBERNETES', label: 'Kubernetes' },
  { value: 'SERVER', label: 'Serveur' },
  { value: 'OTHER', label: 'Autre' },
];

const TARGET_STATUS_LABELS = {
  REGISTERING: 'Enregistrement',
  REGISTERED: 'Enregistré',
  VALIDATING: 'Validation',
  READY_FOR_DEPLOYMENT: 'Prêt',
  UNAVAILABLE: 'Indisponible',
  DISABLED: 'Désactivé',
  FAILED: 'Échec',
};

const TARGET_STATUS_COLORS = {
  REGISTERING: '#eab308',
  REGISTERED: '#3b82f6',
  VALIDATING: '#eab308',
  READY_FOR_DEPLOYMENT: '#22c55e',
  UNAVAILABLE: '#ef4444',
  DISABLED: '#64748b',
  FAILED: '#ef4444',
};

function Infrastructure() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [tab, setTab] = useState('targets');
  const [environments, setEnvironments] = useState([]);
  const [targets, setTargets] = useState([]);
  const [hypervisors, setHypervisors] = useState([]);
  const [vms, setVms] = useState([]);
  const [containers, setContainers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [registerVM, setRegisterVM] = useState(null);
  const [registerForm, setRegisterForm] = useState({ name: '', environment: '', ssh_user: 'root', ssh_port: 22, description: '' });
  const [regSaving, setRegSaving] = useState(false);
  const [actionMsg, setActionMsg] = useState('');

  const load = useCallback(() => {
    getEnvironments().then(res => { setEnvironments(res?.results || (Array.isArray(res) ? res : [])); }).catch(() => {});
    getDeploymentTargets().then(res => { setTargets(res?.results || (Array.isArray(res) ? res : [])); }).catch(() => {});
    getHypervisors().then(res => { setHypervisors(res?.results || (Array.isArray(res) ? res : [])); }).catch(() => {});
    getVirtualMachines().then(res => { setVms(res?.results || (Array.isArray(res) ? res : [])); }).catch(() => {});
    getDockerContainers().then(res => { setContainers(res?.results || (Array.isArray(res) ? res : [])); }).catch(() => {});
    getProjects().then(res => { setProjects(res?.results || (Array.isArray(res) ? res : [])); }).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSaveEnv = async () => {
    if (!form.name) return;
    setSaving(true);
    try {
      await createEnvironment({
        ...form,
        slug: form.name.toLowerCase().replace(/\s+/g, '-'),
      });
      setShowModal(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur');
    } finally { setSaving(false); }
  };

  const handleSaveTarget = async () => {
    if (!form.name || !form.environment) return;
    setSaving(true);
    try {
      await createDeploymentTarget(form);
      setShowModal(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur');
    } finally { setSaving(false); }
  };

  const handleDeleteTarget = async (id) => {
    if (!window.confirm('Supprimer cette cible ?')) return;
    try { await deleteDeploymentTarget(id); load(); } catch { setError('Erreur suppression'); }
  };

  const handleRegisterFromVM = async () => {
    setRegSaving(true);
    setError('');
    try {
      await registerTargetFromVM(registerForm);
      setRegisterVM(null);
      load();
    } catch (err) {
      const data = err.response?.data;
      let msg = "Erreur d'enregistrement";
      if (data?.detail) msg = data.detail;
      else if (data?.errors) msg = Array.isArray(data.errors) ? data.errors.join(' ') : data.errors;
      else if (err.message) msg = err.message;
      setError(msg);
    } finally { setRegSaving(false); }
  };

  const handleValidate = async (id) => {
    setActionMsg('Validation en cours...');
    try {
      const res = await validateTarget(id);
      setActionMsg('Validation terminee');
      load();
      setTimeout(() => setActionMsg(''), 3000);
    } catch (err) {
      setActionMsg('Erreur validation');
      setTimeout(() => setActionMsg(''), 3000);
    }
  };

  const handleHealthCheck = async (id) => {
    setActionMsg('Health check en cours...');
    try {
      const res = await healthCheckTarget(id);
      setActionMsg('Health check OK');
      load();
      setTimeout(() => setActionMsg(''), 3000);
    } catch (err) {
      setActionMsg('Erreur health check');
      setTimeout(() => setActionMsg(''), 3000);
    }
  };

  const handleDisable = async (id) => {
    try { await disableTarget(id); load(); } catch { setError('Erreur desactivation'); }
  };

  const handleEnable = async (id) => {
    try { await enableTarget(id); load(); } catch { setError('Erreur activation'); }
  };

  return (
    <div className="infra-layout">
      <aside className="infra-sidebar">
        <div className="infra-logo">Provisioning</div>
        <nav className="infra-nav">
          <p className="infra-nav-title">Infrastructure</p>
          <ul>
            <li className={tab === 'targets' ? 'active' : ''} onClick={() => setTab('targets')}>Cibles de déploiement</li>
            <li className={tab === 'environments' ? 'active' : ''} onClick={() => setTab('environments')}>Environnements</li>
            <li className={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>Vue d'ensemble</li>
          </ul>
        </nav>
        <button className="infra-logout" onClick={() => { logout(); navigate('/'); }}>Logout →</button>
      </aside>

      <main className="infra-main">
        <div className="infra-header">
          <h1>{tab === 'targets' ? 'Cibles de déploiement' : tab === 'environments' ? 'Environnements' : 'Vue d\'ensemble'}</h1>
          <div style={{ display: 'flex', gap: 8 }}>
            {tab === 'targets' && (
              <button className="infra-btn-secondary" onClick={() => { setRegisterForm({ name: '', environment: '', ssh_user: 'root', ssh_port: 22, description: '' }); setRegisterVM(true); }}>
                + Depuis une VM
              </button>
            )}
            {(tab === 'targets' || tab === 'environments') && (
              <button className="infra-btn-primary" onClick={() => { setForm(tab === 'environments' ? { name: '', description: '', is_default: false } : { name: '', environment: '', target_type: 'SERVER', host: '', port: 22, description: '' }); setShowModal(tab); }}>
                + Ajouter
              </button>
            )}
          </div>
        </div>

        {error && <p className="infra-error">{error}</p>}
        {actionMsg && <p className="infra-success">{actionMsg}</p>}

        {tab === 'environments' && (
          <div className="infra-table-card">
            <table className="infra-table">
              <thead>
                <tr><th>Nom</th><th>Slug</th><th>Description</th><th>Par défaut</th></tr>
              </thead>
              <tbody>
                {environments.length === 0 && <tr><td colSpan="4" className="infra-empty">Aucun environnement</td></tr>}
                {environments.map(e => (
                  <tr key={e.id}>
                    <td className="infra-bold">{e.name}</td>
                    <td><code>{e.slug}</code></td>
                    <td>{e.description || '—'}</td>
                    <td>{e.is_default ? '✓' : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'targets' && (
          <div className="infra-table-card">
            <table className="infra-table">
              <thead>
                <tr><th>Nom</th><th>Type</th><th>Environnement</th><th>Hôte</th><th>Port</th><th>Statut</th><th></th></tr>
              </thead>
              <tbody>
                {targets.length === 0 && <tr><td colSpan="7" className="infra-empty">Aucune cible de déploiement configurée</td></tr>}
                {targets.map(t => (
                  <tr key={t.id}>
                    <td className="infra-bold">{t.name}</td>
                    <td><span className="infra-badge">{TARGET_TYPES.find(x => x.value === t.target_type)?.label || t.target_type}</span></td>
                    <td>{t.environment_name || environments.find(e => e.id === t.environment)?.name || '—'}</td>
                    <td>{t.host || '—'}</td>
                    <td>{t.port}</td>
                    <td>
                      {t.target_status ? (
                        <span className="infra-badge" style={{
                          borderColor: TARGET_STATUS_COLORS[t.target_status] || '#666',
                          color: TARGET_STATUS_COLORS[t.target_status] || '#666',
                        }}>
                          {TARGET_STATUS_LABELS[t.target_status] || t.target_status}
                        </span>
                      ) : '—'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                        <button className="infra-btn-sm infra-btn-validate" onClick={() => handleValidate(t.id)}>Valider</button>
                        <button className="infra-btn-sm infra-btn-health" onClick={() => handleHealthCheck(t.id)}>Health</button>
                        {t.is_active !== false
                          ? <button className="infra-btn-sm infra-btn-warning" onClick={() => handleDisable(t.id)}>Désactiver</button>
                          : <button className="infra-btn-sm infra-btn-ok" onClick={() => handleEnable(t.id)}>Activer</button>
                        }
                        <button className="infra-btn-sm infra-btn-danger" onClick={() => handleDeleteTarget(t.id)}>Suppr.</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'overview' && (
          <div className="infra-overview-grid">
            <div className="infra-stat-card">
              <span className="infra-stat-label">Hyperviseurs</span>
              <span className="infra-stat-value">{hypervisors.length}</span>
              <button className="infra-link" onClick={() => navigate('/hyperviseurs')}>Gérer →</button>
            </div>
            <div className="infra-stat-card">
              <span className="infra-stat-label">Machines Virtuelles</span>
              <span className="infra-stat-value">{vms.length}</span>
              <button className="infra-link" onClick={() => navigate('/hyperviseurs')}>Gérer →</button>
            </div>
            <div className="infra-stat-card">
              <span className="infra-stat-label">Environnements</span>
              <span className="infra-stat-value">{environments.length}</span>
            </div>
            <div className="infra-stat-card">
              <span className="infra-stat-label">Cibles de déploiement</span>
              <span className="infra-stat-value">{targets.length}</span>
            </div>
            <div className="infra-stat-card">
              <span className="infra-stat-label">Conteneurs Docker</span>
              <span className="infra-stat-value">{containers.length}</span>
            </div>
            <div className="infra-stat-card">
              <span className="infra-stat-label">Projets</span>
              <span className="infra-stat-value">{projects.length}</span>
              <button className="infra-link" onClick={() => navigate('/dashboard')}>Voir →</button>
            </div>
          </div>
        )}
      </main>

      {showModal && (
        <div className="infra-modal-overlay" onClick={() => setShowModal(null)}>
          <div className="infra-modal" onClick={e => e.stopPropagation()}>
            <h3>{showModal === 'environments' ? 'Nouvel environnement' : 'Nouvelle cible de déploiement'}</h3>

            {showModal === 'environments' && (
              <div className="infra-form">
                <label>Nom *</label>
                <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Production" />
                <label>Description</label>
                <textarea value={form.description || ''} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} />
                <label className="infra-checkbox">
                  <input type="checkbox" checked={form.is_default || false} onChange={e => setForm({ ...form, is_default: e.target.checked })} />
                  Environnement par défaut
                </label>
              </div>
            )}

            {showModal === 'targets' && (
              <div className="infra-form">
                <label>Nom *</label>
                <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Serveur-Prod-1" />
                <label>Type</label>
                <select value={form.target_type || 'SERVER'} onChange={e => setForm({ ...form, target_type: e.target.value })}>
                  {TARGET_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
                <label>Environnement *</label>
                <select value={form.environment || ''} onChange={e => setForm({ ...form, environment: e.target.value })}>
                  <option value="">-- Sélectionner --</option>
                  {environments.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
                </select>
                <label>Hôte</label>
                <input value={form.host || ''} onChange={e => setForm({ ...form, host: e.target.value })} placeholder="192.168.1.10" />
                <label>Port SSH</label>
                <input type="number" value={form.port || 22} onChange={e => setForm({ ...form, port: parseInt(e.target.value) || 22 })} />
                <label>Description</label>
                <textarea value={form.description || ''} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} />
              </div>
            )}

            <div className="infra-modal-actions">
              <button onClick={() => setShowModal(null)}>Annuler</button>
              <button className="infra-btn-primary" onClick={showModal === 'environments' ? handleSaveEnv : handleSaveTarget} disabled={saving || !form.name}>
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}
      {registerVM && (
        <div className="infra-modal-overlay" onClick={() => setRegisterVM(null)}>
          <div className="infra-modal" onClick={e => e.stopPropagation()}>
            <h3>Enregistrer depuis une VM</h3>
            <div className="infra-form">
              <label>Nom *</label>
              <input value={registerForm.name} onChange={e => setRegisterForm({ ...registerForm, name: e.target.value })} placeholder="Prod-Web-01" />
              <label>Environnement *</label>
              <select value={registerForm.environment} onChange={e => setRegisterForm({ ...registerForm, environment: e.target.value })}>
                <option value="">-- Sélectionner --</option>
                {environments.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
              <label>VM</label>
              <select value={registerForm.vm_id || ''} onChange={e => setRegisterForm({ ...registerForm, vm_id: parseInt(e.target.value) || '' })}>
                <option value="">-- Sélectionner --</option>
                {vms.filter(v => v.status === 'READY' || v.status === 'RUNNING').map(v => (
                  <option key={v.id} value={v.id}>{v.name} ({v.ip_address || 'N/A'})</option>
                ))}
              </select>
              <label>Utilisateur SSH</label>
              <input value={registerForm.ssh_user} onChange={e => setRegisterForm({ ...registerForm, ssh_user: e.target.value })} />
              <label>Port SSH</label>
              <input type="number" value={registerForm.ssh_port} onChange={e => setRegisterForm({ ...registerForm, ssh_port: parseInt(e.target.value) || 22 })} />
              <label>Description</label>
              <textarea value={registerForm.description} onChange={e => setRegisterForm({ ...registerForm, description: e.target.value })} rows={2} />
            </div>
            <div className="infra-modal-actions">
              <button onClick={() => setRegisterVM(null)}>Annuler</button>
              <button className="infra-btn-primary" onClick={handleRegisterFromVM} disabled={regSaving || !registerForm.name || !registerForm.environment}>
                {regSaving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Infrastructure;
