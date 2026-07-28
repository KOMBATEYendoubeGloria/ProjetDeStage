import devopsApi, { unwrap } from './devopsAxios';

export const getHealth = () => unwrap(devopsApi.get('health/'));

export const analyzeProject = (payload) => unwrap(devopsApi.post('analyze/', payload));

export const generateArtifact = (type, payload) =>
  unwrap(devopsApi.post(`artifacts/${type}/`, payload));

export const generateAllArtifacts = (payload) =>
  unwrap(devopsApi.post('artifacts/all/', payload));

export const getHistory = () => unwrap(devopsApi.get('history/'));
export const getHistoryDetail = (id) => unwrap(devopsApi.get(`history/${id}/`));

// --- Déploiement asynchrone réel ---
export const startDeployment = (providerName, project, artifacts, config = {}, deploiementId = null) =>
  unwrap(devopsApi.post('deployment/async/start/', {
    provider_name: providerName,
    project,
    artifacts,
    config,
    deploiement_id: deploiementId,
  }));

export const getDeploymentStatus = (deploymentId) =>
  unwrap(devopsApi.get(`deployment/async/${deploymentId}/status/`));

export const getDeploymentLogs = (deploymentId) =>
  unwrap(devopsApi.get(`deployment/async/${deploymentId}/logs/`));

export const getDeploymentEvents = (deploymentId) =>
  unwrap(devopsApi.get(`deployment/async/${deploymentId}/events/`));

export const cancelDeployment = (deploymentId) =>
  unwrap(devopsApi.post(`deployment/async/${deploymentId}/cancel/`));