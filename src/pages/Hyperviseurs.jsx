import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getHypervisors, createHypervisor, updateHypervisor, deleteHypervisor,
  getSSHCredentials, createSSHCredential,
  getVirtualMachines, createVirtualMachine, deleteVirtualMachine,
  initializeVM,
} from '../api/infrastructure';
import '../style/Hyperviseurs.css';

const PROVIDERS = [
  { value: 'VMWARE', label: 'VMware' },
  { value: 'HYPERV', label: 'Hyper-V' },
  { value: 'KVM', label: 'KVM' },
  { value: 'XEN', label: 'Xen' },
  { value: 'PROXMOX', label: 'Proxmox' },
  { value: 'OTHER', label: 'Autre' },
];

const VM_STATUS_COLORS = {
  STOPPED: '#ef4444',
  RUNNING: '#22c55e',
  PAUSED: '#eab308',
  ERROR: '#ef4444',
};

const INIT_STATUS_COLORS = {
  INITIALIZING: '#eab308',
  INSTALLING_DEPENDENCIES: '#eab308',
  CONFIGURING: '#eab308',
  READY: '#22c55e',
  INITIALIZATION_FAILED: '#ef4444',
};

function Hyperviseurs() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [tab, setTab] = useState('hypervisors');
  const [hypervisors, setHypervisors] = useState([]);
  const [credentials, setCredentials] = useState([]);
  const [vms, setVms] = useState([]);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [initTarget, setInitTarget] = useState(null);
  const [initForm, setInitForm] = useState({ ssh_username: 'root', ssh_password: '', ssh_port: 22 });
  const [initSaving, setInitSaving] = useState(false);

  const load = useCallback(() => {
    getHypervisors()
      .then(res => { setHypervisors(res?.hypervisors || res?.results || (Array.isArray(res) ? res : [])); })
      .catch(() => setError('Erreur chargement hyperviseurs'));
    getSSHCredentials()
      .then(res => { setCredentials(res?.results || (Array.isArray(res) ? res : [])); })
      .catch(() => {});
    getVirtualMachines()
      .then(res => { setVms(res?.virtual_machines || res?.results || (Array.isArray(res) ? res : [])); })
      .catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = (type) => {
    setForm(type === 'hypervisor' ? { name: '', provider: 'PROXMOX', endpoint: '', management_port: 443, credential: '', description: '' }
      : type === 'credential' ? { name: '', username: '', host: '', port: 22, private_key: '', passphrase: '', description: '' }
      : { name: '', uuid: crypto.randomUUID(), hypervisor: '', ip_address: '', operating_system: 'Ubuntu 22.04', cpu: 2, memory_mb: 2048, disk_gb: 20 });
    setShowModal(type);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      if (showModal === 'hypervisor') {
        await createHypervisor(form);
      } else if (showModal === 'credential') {
        await createSSHCredential(form);
      } else if (showModal === 'vm') {
        await createVirtualMachine({ ...form, status: 'STOPPED' });
      }
      setShowModal(null);
      load();
    } catch (err) {
      const data = err.response?.data;
      let msg = 'Erreur de sauvegarde';
      if (data) {
        if (data.detail) msg = data.detail;
        else if (data.errors) msg = Array.isArray(data.errors) ? data.errors.join(' ') : data.errors;
        else {
          const fieldErrors = Object.entries(data)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' | ');
          if (fieldErrors) msg = fieldErrors;
        }
      } else if (err.message) {
        msg = err.message;
      }
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleOpenInit = (vm) => {
    setInitTarget(vm);
    setInitForm({ ssh_username: 'root', ssh_password: '', ssh_port: 22 });
  };

  const handleInitVM = async () => {
    setInitSaving(true);
    setError('');
    try {
      const res = await initializeVM(initTarget.id, initForm);
      setInitTarget(null);
      load();
    } catch (err) {
      const data = err.response?.data;
      let msg = "Erreur d'initialisation";
      if (data) {
        if (data.detail) msg = data.detail;
        else if (data.errors) msg = Array.isArray(data.errors) ? data.errors.join(' ') : data.errors;
        else {
          const fieldErrors = Object.entries(data)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' | ');
          if (fieldErrors) msg = fieldErrors;
        }
      } else if (err.message) msg = err.message;
      setError(msg);
    } finally {
      setInitSaving(false);
    }
  };

  const handleDelete = async (type, id) => {
    if (!window.confirm('Supprimer cet élément ?')) return;
    try {
      if (type === 'hypervisor') await deleteHypervisor(id);
      else if (type === 'vm') await deleteVirtualMachine(id);
      load();
    } catch {
      setError('Erreur de suppression');
    }
  };

  return (
    <div className="hyp-layout">
      <aside className="hyp-sidebar">
        <div className="hyp-logo">Infra Manager</div>
        <nav className="hyp-nav">
          <p className="hyp-nav-title">Infrastructure</p>
          <ul>
            <li className={tab === 'hypervisors' ? 'active' : ''} onClick={() => setTab('hypervisors')}>Hyperviseurs</li>
            <li className={tab === 'credentials' ? 'active' : ''} onClick={() => setTab('credentials')}>Credentials SSH</li>
            <li className={tab === 'vms' ? 'active' : ''} onClick={() => setTab('vms')}>Machines Virtuelles</li>
          </ul>
        </nav>
        <button className="hyp-logout" onClick={() => { logout(); navigate('/'); }}>Logout →</button>
      </aside>

      <main className="hyp-main">
        <div className="hyp-header">
          <h1>{tab === 'hypervisors' ? 'Hyperviseurs' : tab === 'credentials' ? 'Credentials SSH' : 'Machines Virtuelles'}</h1>
          <button className="hyp-btn-primary" onClick={() => openCreate(tab === 'hypervisors' ? 'hypervisor' : tab === 'credentials' ? 'credential' : 'vm')}>
            + Ajouter
          </button>
        </div>

        {error && <p className="hyp-error">{error}</p>}

        {tab === 'hypervisors' && (
          <div className="hyp-table-card">
            <table className="hyp-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Fournisseur</th>
                  <th>Endpoint</th>
                  <th>Port</th>
                  <th>Description</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {hypervisors.length === 0 && <tr><td colSpan="6" className="hyp-empty">Aucun hyperviseur configuré</td></tr>}
                {hypervisors.map(h => (
                  <tr key={h.id}>
                    <td className="hyp-bold">{h.name}</td>
                    <td><span className="hyp-badge">{PROVIDERS.find(p => p.value === h.provider)?.label || h.provider}</span></td>
                    <td>{h.endpoint || '—'}</td>
                    <td>{h.management_port}</td>
                    <td className="hyp-desc">{h.description || '—'}</td>
                    <td>
                      <button className="hyp-btn-sm hyp-btn-danger" onClick={() => handleDelete('hypervisor', h.id)}>Supprimer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'credentials' && (
          <div className="hyp-table-card">
            <table className="hyp-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Utilisateur</th>
                  <th>Hôte</th>
                  <th>Port</th>
                  <th>Clé SSH</th>
                  <th>Actif</th>
                </tr>
              </thead>
              <tbody>
                {credentials.length === 0 && <tr><td colSpan="6" className="hyp-empty">Aucun credential configuré</td></tr>}
                {credentials.map(c => (
                  <tr key={c.id}>
                    <td className="hyp-bold">{c.name}</td>
                    <td>{c.username}</td>
                    <td>{c.host}</td>
                    <td>{c.port}</td>
                    <td>{c.private_key ? '✓ Configurée' : '—'}</td>
                    <td><span className="hyp-status-dot" style={{ background: c.is_active ? '#22c55e' : '#ef4444' }} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'vms' && (
          <div className="hyp-table-card">
            <table className="hyp-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Hyperviseur</th>
                  <th>IP</th>
                  <th>OS</th>
                  <th>CPU</th>
                  <th>RAM (MB)</th>
                  <th>Disque (GB)</th>
                  <th>Statut</th>
                  <th>Init</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {vms.length === 0 && <tr><td colSpan="10" className="hyp-empty">Aucune machine virtuelle</td></tr>}
                {vms.map(vm => (
                  <tr key={vm.id}>
                    <td className="hyp-bold">{vm.name}</td>
                    <td>{vm.hypervisor_name || vm.hypervisor}</td>
                    <td>{vm.ip_address || '—'}</td>
                    <td>{vm.operating_system || '—'}</td>
                    <td>{vm.cpu}</td>
                    <td>{vm.memory_mb}</td>
                    <td>{vm.disk_gb}</td>
                    <td>
                      <span className="hyp-badge" style={{ borderColor: VM_STATUS_COLORS[vm.status] || '#666', color: VM_STATUS_COLORS[vm.status] || '#666' }}>
                        {vm.status}
                      </span>
                    </td>
                    <td>
                      {vm.status === 'READY' || vm.status === 'INITIALIZING' || vm.status === 'INSTALLING_DEPENDENCIES' || vm.status === 'CONFIGURING' || vm.status === 'INITIALIZATION_FAILED' ? (
                        <span className="hyp-badge" style={{ borderColor: INIT_STATUS_COLORS[vm.status] || '#666', color: INIT_STATUS_COLORS[vm.status] || '#666' }}>
                          {vm.status === 'READY' ? 'Prêt' : vm.status === 'INITIALIZATION_FAILED' ? 'Échec' : 'En cours'}
                        </span>
                      ) : '—'}
                    </td>
                    <td style={{ display: 'flex', gap: 4 }}>
                      <button className="hyp-btn-sm hyp-btn-init" onClick={() => handleOpenInit(vm)}
                        disabled={vm.status !== 'RUNNING' && vm.status !== 'INITIALIZATION_FAILED'}>
                        Initialiser
                      </button>
                      <button className="hyp-btn-sm hyp-btn-danger" onClick={() => handleDelete('vm', vm.id)}>Supprimer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {showModal && (
        <div className="hyp-modal-overlay" onClick={() => setShowModal(null)}>
          <div className="hyp-modal" onClick={e => e.stopPropagation()}>
            <h3>{showModal === 'hypervisor' ? 'Ajouter un hyperviseur' : showModal === 'credential' ? 'Ajouter un credential SSH' : 'Ajouter une VM'}</h3>

            {showModal === 'hypervisor' && (
              <div className="hyp-form">
                <label>Nom *</label>
                <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Mon hyperviseur" />
                <label>Fournisseur</label>
                <select value={form.provider || 'PROXMOX'} onChange={e => setForm({ ...form, provider: e.target.value })}>
                  {PROVIDERS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                </select>
                <label>Endpoint (URL)</label>
                <input value={form.endpoint || ''} onChange={e => setForm({ ...form, endpoint: e.target.value })} placeholder="https://192.168.1.100:8006" />
                <label>Port management</label>
                <input type="number" value={form.management_port || 443} onChange={e => setForm({ ...form, management_port: parseInt(e.target.value) || 443 })} />
                <label>Credential SSH</label>
                <select value={form.credential || ''} onChange={e => setForm({ ...form, credential: e.target.value || null })}>
                  <option value="">-- Aucun --</option>
                  {credentials.map(c => <option key={c.id} value={c.id}>{c.name} ({c.host})</option>)}
                </select>
                <label>Description</label>
                <textarea value={form.description || ''} onChange={e => setForm({ ...form, description: e.target.value })} rows={2} />
              </div>
            )}

            {showModal === 'credential' && (
              <div className="hyp-form">
                <label>Nom *</label>
                <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Mon credential" />
                <label>Utilisateur *</label>
                <input value={form.username || ''} onChange={e => setForm({ ...form, username: e.target.value })} placeholder="root" />
                <label>Hôte *</label>
                <input value={form.host || ''} onChange={e => setForm({ ...form, host: e.target.value })} placeholder="192.168.1.100" />
                <label>Port SSH</label>
                <input type="number" value={form.port || 22} onChange={e => setForm({ ...form, port: parseInt(e.target.value) || 22 })} />
                <label>Clé privée (PEM)</label>
                <textarea value={form.private_key || ''} onChange={e => setForm({ ...form, private_key: e.target.value })} rows={4} placeholder="-----BEGIN RSA PRIVATE KEY-----..." />
                <label>Passphrase (optionnel)</label>
                <input type="password" value={form.passphrase || ''} onChange={e => setForm({ ...form, passphrase: e.target.value })} />
              </div>
            )}

            {showModal === 'vm' && (
              <div className="hyp-form">
                <label>Nom *</label>
                <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="VM-Production" />
                <label>Hyperviseur *</label>
                <select value={form.hypervisor || ''} onChange={e => setForm({ ...form, hypervisor: e.target.value })}>
                  <option value="">-- Sélectionner --</option>
                  {hypervisors.map(h => <option key={h.id} value={h.id}>{h.name} ({h.provider})</option>)}
                </select>
                <label>Adresse IP</label>
                <input value={form.ip_address || ''} onChange={e => setForm({ ...form, ip_address: e.target.value })} placeholder="192.168.1.50" />
                <label>Système d'exploitation</label>
                <input value={form.operating_system || ''} onChange={e => setForm({ ...form, operating_system: e.target.value })} placeholder="Ubuntu 22.04" />
                <label>CPU</label>
                <input type="number" min="1" value={form.cpu || 2} onChange={e => setForm({ ...form, cpu: parseInt(e.target.value) || 1 })} />
                <label>RAM (MB)</label>
                <input type="number" min="256" value={form.memory_mb || 2048} onChange={e => setForm({ ...form, memory_mb: parseInt(e.target.value) || 256 })} />
                <label>Disque (GB)</label>
                <input type="number" min="10" value={form.disk_gb || 20} onChange={e => setForm({ ...form, disk_gb: parseInt(e.target.value) || 10 })} />
              </div>
            )}

            <div className="hyp-modal-actions">
              <button onClick={() => setShowModal(null)}>Annuler</button>
              <button className="hyp-btn-primary" onClick={handleSave} disabled={saving || !form.name}>
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      )}

      {initTarget && (
        <div className="hyp-modal-overlay" onClick={() => setInitTarget(null)}>
          <div className="hyp-modal" onClick={e => e.stopPropagation()}>
            <h3>Initialiser : {initTarget.name}</h3>
            <div className="hyp-form">
              <label>Utilisateur SSH</label>
              <input value={initForm.ssh_username} onChange={e => setInitForm({ ...initForm, ssh_username: e.target.value })} />
              <label>Mot de passe SSH</label>
              <input type="password" value={initForm.ssh_password} onChange={e => setInitForm({ ...initForm, ssh_password: e.target.value })} />
              <label>Port SSH</label>
              <input type="number" value={initForm.ssh_port} onChange={e => setInitForm({ ...initForm, ssh_port: parseInt(e.target.value) || 22 })} />
            </div>
            <div className="hyp-modal-actions">
              <button onClick={() => setInitTarget(null)}>Annuler</button>
              <button className="hyp-btn-primary" onClick={handleInitVM} disabled={initSaving}>
                {initSaving ? 'Initialisation...' : 'Lancer'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Hyperviseurs;
