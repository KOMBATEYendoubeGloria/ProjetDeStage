import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getDeployment, getDeploymentLogs, lancerDeployment, terminerDeployment } from '../api/deployments';
import { generateAllArtifacts, startDeployment, getDeploymentStatus } from '../api/devops';
import { getProject } from '../api/projects';
import '../style/DeploiementDetail.css';

const STATUT_LABELS = {
  EN_ATTENTE: 'En attente',
  EN_COURS: 'En cours',
  SUCCES: 'Déployé',
  ECHEC: 'Échoué',
};

const STATUT_CLASS = {
  EN_ATTENTE: 'dd-statut-attente',
  EN_COURS: 'dd-statut-cours',
  SUCCES: 'dd-statut-succes',
  ECHEC: 'dd-statut-echec',
};

const NIVEAU_CLASS = {
  INFO: 'dd-niveau-info',
  WARN: 'dd-niveau-warn',
  ERROR: 'dd-niveau-error',
};

const FRAMEWORK_MAP = { NODEJS: 'nodejs', DJANGO: 'django', REACT: 'react' };

function DeploymentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [deployment, setDeployment] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [niveauFilter, setNiveauFilter] = useState('');
  const [showLaunchModal, setShowLaunchModal] = useState(false);
  const [launchForm, setLaunchForm] = useState({ ports: '8000', provider: 'docker', docker_image: '' });
  const [launching, setLaunching] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);

  const load = () => {
    getDeployment(id)
      .then((res) => setDeployment(res.data))
      .catch(() => setError('Impossible de charger ce déploiement.'));
    getDeploymentLogs(id, niveauFilter)
      .then((res) => setLogs(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // Rafraîchissement automatique toutes les 5s tant que le déploiement est en cours
    const interval = setInterval(() => {
      if (deployment?.statut === 'EN_COURS') load();
    }, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, niveauFilter, deployment?.statut]);

  const handleOpenLaunchModal = () => setShowLaunchModal(true);

  const handleConfirmLaunch = async () => {
    setError('');
    setLaunching(true);
    try {
      await lancerDeployment(id);

      const projectRes = await getProject(deployment.projet);
      const project = {
        name: deployment.projet_nom,
        framework: FRAMEWORK_MAP[projectRes.data.technologie] || 'generic',
        ports: launchForm.ports.split(',').map((p) => parseInt(p.trim(), 10)).filter(Boolean),
        provider: launchForm.provider,
        ...(launchForm.docker_image ? { docker_image: launchForm.docker_image } : {}),
      };

      const artifacts = await generateAllArtifacts(project);
      const artifactsPayload = {
        dockerfile: artifacts.dockerfile,
        docker_compose: artifacts.docker_compose,
        environment: artifacts.environment,
        terraform: artifacts.terraform,
        ansible_playbook: artifacts.ansible_playbook,
        ansible_inventory: artifacts.ansible_inventory,
        pipeline: artifacts.pipeline,
      };

      // Pour le provider "docker", Terraform n'a pas de rôle utile ici :
      // Docker seul gère provisioning + déploiement via docker-compose.
      if (launchForm.provider === 'docker') {
        delete artifactsPayload.terraform;
      }

      // Le code source réel doit être cloné avant le build — on transmet
      // l'URL du dépôt Git et la branche du projet (Gloria) au moteur DevOps.
      const config = {
        variables: {
          repo_url: projectRes.data.url_depot_git,
          repo_branch: projectRes.data.branche || 'main',
        },
      };

      const res = await startDeployment(launchForm.provider, project, artifactsPayload, config);
      setJobId(res.deployment_id);
      setShowLaunchModal(false);
    } catch (err) {
      setError(err.message || err.response?.data?.error || 'Échec du lancement.');
    } finally {
      setLaunching(false);
    }
  };

  useEffect(() => {
    if (!jobId) return;

    let isActive = true;
    let reachedTerminalState = false;

    const poll = async () => {
      try {
        const status = await getDeploymentStatus(jobId);
        if (!isActive) return;

        setJobStatus(status);

        if (['COMPLETED', 'FAILED', 'CANCELLED'].includes(status.status)) {
          reachedTerminalState = true;
          const resultat = status.status === 'COMPLETED' ? 'SUCCES' : 'ECHEC';
          await terminerDeployment(id, resultat);
          load();
        }
      } catch {
        // on ignore les erreurs de polling ponctuelles
      }
    };

    poll();
    const interval = setInterval(() => {
      if (reachedTerminalState) {
        clearInterval(interval);
        return;
      }
      poll();
    }, 3000);
    return () => {
      isActive = false;
      clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  if (loading) return <div className="dd-page"><p className="dd-loading">Chargement...</p></div>;
  if (!deployment) return <div className="dd-page"><p className="dd-error">{error || 'Déploiement introuvable.'}</p></div>;

  return (
    <div className="dd-page">
      <div className="dd-card">
        <button className="dd-back" onClick={() => navigate('/deploiements')}>← Retour</button>

        <div className="dd-header">
          <div>
            <h1 className="dd-title">Déploiement #{deployment.id}</h1>
            <p className="dd-project">{deployment.projet_nom}</p>
          </div>
          <span className={`dd-badge ${STATUT_CLASS[deployment.statut]}`}>
            {STATUT_LABELS[deployment.statut]}
          </span>
        </div>

        {error && <p className="dd-error">{error}</p>}

        <div className="dd-info-grid">
          <div>
            <span className="dd-info-label">Date</span>
            <span className="dd-info-value">{new Date(deployment.date_heure).toLocaleString()}</span>
          </div>
          <div>
            <span className="dd-info-label">Commit</span>
            <span className="dd-info-value">{deployment.commit_hash || '—'}</span>
          </div>
        </div>

        <div className="dd-actions">
          {deployment.statut === 'EN_ATTENTE' && (
            <button className="dd-btn dd-btn-primary" onClick={handleOpenLaunchModal}>
               Lancer le déploiement
            </button>
          )}
        </div>

        {jobId && jobStatus && (
          <div className="dd-job-progress">
            <h3>Exécution réelle</h3>
            <div className="dd-progress-bar">
              <div className="dd-progress-fill" style={{ width: `${jobStatus.progress_percent}%` }} />
            </div>
            <p>{jobStatus.status} — {jobStatus.progress_percent}%</p>
            {jobStatus.error_message && <p className="dd-error">{jobStatus.error_message}</p>}
          </div>
        )}

        <div className="dd-logs-section">
          <div className="dd-logs-header">
            <h2>Journaux</h2>
            <select value={niveauFilter} onChange={(e) => setNiveauFilter(e.target.value)}>
              <option value="">Tous les niveaux</option>
              <option value="INFO">Info</option>
              <option value="WARN">Avertissement</option>
              <option value="ERROR">Erreur</option>
            </select>
          </div>

          {logs.length === 0 ? (
            <p className="dd-empty">Aucun journal pour ce déploiement.</p>
          ) : (
            <div className="dd-log-list">
              {logs.map((log) => (
                <div key={log.id} className="dd-log-entry">
                  <span className={`dd-log-badge ${NIVEAU_CLASS[log.niveau]}`}>{log.niveau}</span>
                  <span className="dd-log-message">{log.message}</span>
                  <span className="dd-log-time">
                    {new Date(log.horodatage).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {showLaunchModal && (
          <div className="dd-modal-overlay" onClick={() => setShowLaunchModal(false)}>
            <div className="dd-modal" onClick={(e) => e.stopPropagation()}>
              <h3>Lancer le déploiement</h3>

              <label>Port(s) exposé(s)</label>
              <input
                type="text"
                value={launchForm.ports}
                onChange={(e) => setLaunchForm({ ...launchForm, ports: e.target.value })}
                placeholder="8000, 5432"
              />

              <label>Provider infra</label>
              <select
                value={launchForm.provider}
                onChange={(e) => setLaunchForm({ ...launchForm, provider: e.target.value })}
              >
                <option value="docker">Docker</option>
                <option value="proxmox">Proxmox</option>
                <option value="vmware">VMware</option>
                <option value="virtualbox">VirtualBox</option>
              </select>

              <label>Image Docker (optionnel, doit exister sur Docker Hub si laissé vide côté build local)</label>
              <input
                type="text"
                value={launchForm.docker_image}
                onChange={(e) => setLaunchForm({ ...launchForm, docker_image: e.target.value })}
                placeholder="laisser vide pour utiliser le nom du projet"
              />

              <div className="dd-modal-actions">
                <button onClick={() => setShowLaunchModal(false)} disabled={launching}>Annuler</button>
                <button className="dd-modal-confirm" onClick={handleConfirmLaunch} disabled={launching}>
                  {launching ? 'Lancement...' : 'Confirmer'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DeploymentDetail;