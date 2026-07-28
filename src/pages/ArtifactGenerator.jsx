import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects } from '../api/projects';
import {
  analyzeProject,
  generateArtifact,
  generateAllArtifacts,
  startDeployment,
  getDeploymentStatus,
  getDeploymentLogs,
  getDeploymentEvents,
} from '../api/devops';
import '../style/artifactgenerator.css';

const FRAMEWORK_MAP = { NODEJS: 'nodejs', DJANGO: 'django', REACT: 'react' };

const ARTIFACT_TYPES = [
  { key: 'docker', label: 'Dockerfile', dataKey: 'generate_dockerfile' },
  { key: 'docker-compose', label: 'Docker Compose', dataKey: 'generate_docker_compose' },
  { key: 'environment', label: 'Environnement', dataKey: 'generate_environment' },
  { key: 'terraform', label: 'Terraform', dataKey: 'generate_terraform' },
  { key: 'ansible', label: 'Ansible', dataKey: 'generate_ansible' },
  { key: 'pipeline', label: 'Pipeline CI/CD', dataKey: 'generate_pipeline' },
];

function ArtifactGenerator() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');

  const [form, setForm] = useState({
    name: '',
    framework: 'django',
    ports: '',
    environment: 'dev',
    provider: 'docker',
    ci_platform: 'github-actions',
    repo_url: '',
    repo_branch: 'main',
  });

  const [analyzed, setAnalyzed] = useState(null);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [loadingGenerate, setLoadingGenerate] = useState('');
  const [error, setError] = useState('');
  const [results, setResults] = useState({});
  const [activeTab, setActiveTab] = useState('');
  const [allArtifacts, setAllArtifacts] = useState(null);
  const [deploymentId, setDeploymentId] = useState(null);
  const [deployStatus, setDeployStatus] = useState(null);
  const [deployLogs, setDeployLogs] = useState([]);
  const [deployEvents, setDeployEvents] = useState([]);
  const [deploying, setDeploying] = useState(false);

  useEffect(() => {
    getProjects()
      .then((res) => setProjects(res.data.results))
      .catch(() => {});
  }, []);

  const handleSelectProject = (e) => {
    const id = e.target.value;
    setSelectedProjectId(id);
    const project = projects.find((p) => String(p.id) === id);
    if (project) {
      setForm((f) => ({
        ...f,
        name: project.nom,
        framework: FRAMEWORK_MAP[project.technologie] || 'generic',
        repo_url: project.url_depot_git || f.repo_url,
        repo_branch: project.branche || f.repo_branch || 'main',
      }));
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const buildPayload = () => ({
    name: form.name,
    framework: form.framework,
    environment: form.environment,
    provider: form.provider,
    ci_platform: form.ci_platform,
    ...(form.ports
      ? { ports: form.ports.split(',').map((p) => parseInt(p.trim(), 10)).filter(Boolean) }
      : {}),
  });

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setError('');
    setLoadingAnalyze(true);
    setAnalyzed(null);
    try {
      const result = await analyzeProject(buildPayload());
      setAnalyzed(result);
      setForm((f) => ({
        ...f,
        framework: result.framework || f.framework,
        environment: result.environment || f.environment,
        provider: result.provider || f.provider,
        ci_platform: result.ci_platform || f.ci_platform,
        ports: (result.ports || []).join(', '),
      }));
    } catch (err) {
      setError(err.message || "Échec de l'analyse.");
    } finally {
      setLoadingAnalyze(false);
    }
  };

  const handleGenerateOne = async (type, dataKey) => {
    setError('');
    setLoadingGenerate(type);
    try {
      const data = await generateArtifact(type, buildPayload());
      setResults((prev) => ({ ...prev, [type]: data[dataKey] }));
      setActiveTab(type);
    } catch (err) {
      setError(err.message || `Échec de la génération (${type}).`);
    } finally {
      setLoadingGenerate('');
    }
  };

  const handleGenerateAll = async () => {
    setError('');
    setLoadingGenerate('all');
    try {
      const data = await generateAllArtifacts(buildPayload());
      setAllArtifacts(data);
      setResults({
        docker: data.dockerfile,
        'docker-compose': data.docker_compose,
        environment: data.environment,
        terraform: data.terraform,
        ansible: data.ansible_playbook,
        pipeline: data.pipeline,
      });
      setActiveTab('docker');
    } catch (err) {
      setError(err.message || 'Échec de la génération complète.');
    } finally {
      setLoadingGenerate('');
    }
  };

  const handleDeploy = async () => {
  if (!allArtifacts) return;
  setError('');
  setDeploying(true);
  setDeployStatus(null);
  setDeployLogs([]);
  setDeployEvents([]);
  try {
    const ports = form.ports
      ? form.ports.split(',').map((p) => parseInt(p.trim(), 10)).filter(Boolean)
      : [8000];
    const artifactsPayload = {
      dockerfile: allArtifacts.dockerfile,
      docker_compose: allArtifacts.docker_compose,
      environment: allArtifacts.environment,
      terraform: allArtifacts.terraform,
      ansible_playbook: allArtifacts.ansible_playbook,
      ansible_inventory: allArtifacts.ansible_inventory,
      pipeline: allArtifacts.pipeline,
      metadata: {
        project_name: form.name,
        framework: form.framework,
        port: ports[0],
      },
    };
    // Pour le provider "docker", Terraform n'a pas de rôle utile :
    // Docker seul gère provisioning + déploiement via docker-compose.
    if (form.provider === 'docker') {
      delete artifactsPayload.terraform;
    }
    const config = {
      variables: {
        repo_url: form.repo_url,
        repo_branch: form.repo_branch || 'main',
      },
    };
    const res = await startDeployment(form.provider, buildPayload(), artifactsPayload, config);
    setDeploymentId(res.deployment_id);
  } catch (err) {
    setError(err.message || 'Échec du démarrage du déploiement.');
    setDeploying(false);
  }
};


  useEffect(() => {
    if (!deploymentId) return;

    const poll = async () => {
      try {
        const status = await getDeploymentStatus(deploymentId);
        setDeployStatus(status);

        const logsRes = await getDeploymentLogs(deploymentId);
        setDeployLogs(logsRes.logs || []);

        const eventsRes = await getDeploymentEvents(deploymentId);
        setDeployEvents(eventsRes.events || []);

        if (['COMPLETED', 'FAILED', 'CANCELLED'].includes(status.status)) {
          setDeploying(false);
        }
      } catch (err) {
        // on ignore les erreurs de polling ponctuelles, on continue d'essayer
      }
    };

    poll();
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [deploymentId]);

  return (
    <div className="ag-page">
      <div className="ag-card">
        <button className="ag-back" onClick={() => navigate('/dashboard')}>← Retour</button>
        <h1 className="ag-title">Générateur d'artefacts DevOps</h1>

        {error && <p className="ag-error">{error}</p>}

        <div className="ag-field">
          <label>Charger depuis un projet existant (optionnel)</label>
          <select value={selectedProjectId} onChange={handleSelectProject}>
            <option value="">-- Aucun --</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.nom}</option>
            ))}
          </select>
        </div>

        <form onSubmit={handleAnalyze} className="ag-form">
          <div className="ag-row">
            <div className="ag-field">
              <label>Nom du projet</label>
              <input type="text" name="name" value={form.name} onChange={handleChange} required />
            </div>
            <div className="ag-field">
              <label>Framework</label>
              <select name="framework" value={form.framework} onChange={handleChange}>
                <option value="django">Django</option>
                <option value="nodejs">Node.js</option>
                <option value="react">React</option>
                <option value="laravel">Laravel</option>
                <option value="springboot">Spring Boot</option>
                <option value="generic">Generic</option>
              </select>
            </div>
          </div>

          <div className="ag-row">
            <div className="ag-field">
              <label>Ports (séparés par virgule)</label>
              <input type="text" name="ports" placeholder="8000, 5432" value={form.ports} onChange={handleChange} />
            </div>
            <div className="ag-field">
              <label>Environnement</label>
              <select name="environment" value={form.environment} onChange={handleChange}>
                <option value="dev">Development</option>
                <option value="staging">Staging</option>
                <option value="prod">Production</option>
              </select>
            </div>
          </div>

          <div className="ag-row">
            <div className="ag-field">
              <label>Provider (infra)</label>
              <select name="provider" value={form.provider} onChange={handleChange}>
                <option value="docker">Docker</option>
                <option value="proxmox">Proxmox</option>
                <option value="vmware">VMware</option>
                <option value="virtualbox">VirtualBox</option>
              </select>
            </div>
            <div className="ag-field">
              <label>Plateforme CI/CD</label>
              <select name="ci_platform" value={form.ci_platform} onChange={handleChange}>
                <option value="github-actions">GitHub Actions</option>
                <option value="gitlab-ci">GitLab CI</option>
                <option value="jenkins">Jenkins</option>
              </select>
            </div>
          </div>

          <div className="ag-row">
            <div className="ag-field" style={{ flex: 2 }}>
              <label>URL du dépôt Git (source)</label>
              <input type="url" name="repo_url" placeholder="https://github.com/user/repo.git" value={form.repo_url} onChange={handleChange} />
            </div>
            <div className="ag-field" style={{ flex: 1 }}>
              <label>Branche</label>
              <input type="text" name="repo_branch" placeholder="main" value={form.repo_branch} onChange={handleChange} />
            </div>
          </div>

          <button type="submit" className="ag-btn ag-btn-secondary" disabled={loadingAnalyze}>
            {loadingAnalyze ? 'Analyse...' : 'Analyser le projet'}
          </button>
        </form>

        {analyzed && (
          <div className="ag-analyzed">
            Projet analysé : {analyzed.language} · {analyzed.database || 'aucune DB détectée'}
          </div>
        )}

        <div className="ag-generate-section">
          <h2>Générer les artefacts</h2>
          <div className="ag-buttons-grid">
            {ARTIFACT_TYPES.map((t) => (
              <button
                key={t.key}
                type="button"
                className="ag-btn ag-btn-outline"
                onClick={() => handleGenerateOne(t.key, t.dataKey)}
                disabled={!form.name || loadingGenerate !== ''}
              >
                {loadingGenerate === t.key ? '...' : t.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="ag-btn ag-btn-primary"
            onClick={handleGenerateAll}
            disabled={!form.name || loadingGenerate !== ''}
          >
            {loadingGenerate === 'all' ? 'Génération en cours...' : ' Tout générer'}
          </button>
        </div>

        {Object.keys(results).length > 0 && (
          <div className="ag-results">
            <div className="ag-tabs">
              {Object.keys(results).map((key) => (
                <button
                  key={key}
                  type="button"
                  className={`ag-tab ${activeTab === key ? 'active' : ''}`}
                  onClick={() => setActiveTab(key)}
                >
                  {key}
                </button>
              ))}
            </div>
            <pre className="ag-code-viewer">
              <code>{results[activeTab]}</code>
            </pre>
          </div>
        )}

        {allArtifacts && (
          <div className="ag-deploy-section">
            <h2>Déploiement</h2>
            <button
              className="ag-btn ag-btn-primary"
              onClick={handleDeploy}
              disabled={deploying}
            >
              {deploying ? 'Déploiement en cours...' : 'Déployer maintenant'}
            </button>

            {deployStatus && (
              <div className="ag-deploy-status">
                <div className="ag-deploy-row">
                  <span>Statut :</span>
                  <span className={`ag-deploy-badge ag-deploy-${deployStatus.status?.toLowerCase()}`}>
                    {deployStatus.status}
                  </span>
                </div>
                <div className="ag-deploy-row">
                  <span>Progression :</span>
                  <span>{deployStatus.progress_percent}%</span>
                </div>
                <div className="ag-progress-bar">
                  <div className="ag-progress-fill" style={{ width: `${deployStatus.progress_percent}%` }} />
                </div>

                {deployStatus.notification && deployStatus.notification.type === 'DEPLOYMENT_SUCCESS' && (
                  <div className="ag-notification ag-notification-success">
                    <strong>Déploiement réussi!</strong>
                    <p>{deployStatus.notification.message}</p>
                    <a href={deployStatus.notification.url} target="_blank" rel="noopener noreferrer" className="ag-btn ag-btn-primary" style={{ marginTop: '8px', display: 'inline-block' }}>
                      Ouvrir l'application ({deployStatus.notification.url})
                    </a>
                  </div>
                )}

                {deployStatus.notification && deployStatus.notification.type === 'DEPLOYMENT_FAILED' && (
                  <div className="ag-notification ag-notification-error">
                    <strong>Échec du déploiement</strong>
                    <p>{deployStatus.notification.message}</p>
                  </div>
                )}

                {deployStatus.error_message && (
                  <p className="ag-error">{deployStatus.error_message}</p>
                )}
              </div>
            )}

            {deployLogs.length > 0 && (
              <div className="ag-deploy-logs">
                <h3>Logs</h3>
                {deployLogs.map((log, i) => (
                  <div key={i} className="ag-log-line">
                    <span className="ag-log-level">{log.level}</span> {log.message}
                  </div>
                ))}
              </div>
            )}

            {deployEvents.length > 0 && (
              <div className="ag-deploy-events">
                <h3>Événements (données brutes)</h3>
                <pre className="ag-code-viewer">{JSON.stringify(deployEvents, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ArtifactGenerator;
