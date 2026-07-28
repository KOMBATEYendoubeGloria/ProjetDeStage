import devopsApi from './devopsAxios';

const infraAxios = devopsApi;

// --- SSH Credentials ---
export const getSSHCredentials = () =>
  infraAxios.get('infrastructure/ssh-credentials/').then(r => r.data);

export const getSSHCredential = (id) =>
  infraAxios.get(`infrastructure/ssh-credentials/${id}/`).then(r => r.data);

export const createSSHCredential = (data) =>
  infraAxios.post('infrastructure/ssh-credentials/', data).then(r => r.data);

export const updateSSHCredential = (id, data) =>
  infraAxios.put(`infrastructure/ssh-credentials/${id}/`, data).then(r => r.data);

export const deleteSSHCredential = (id) =>
  infraAxios.delete(`infrastructure/ssh-credentials/${id}/`).then(r => r.data);

// --- Environments ---
export const getEnvironments = () =>
  infraAxios.get('infrastructure/environments/').then(r => r.data);

export const createEnvironment = (data) =>
  infraAxios.post('infrastructure/environments/', data).then(r => r.data);

export const deleteEnvironment = (id) =>
  infraAxios.delete(`infrastructure/environments/${id}/`).then(r => r.data);

// --- Hypervisors ---
export const getHypervisors = () =>
  infraAxios.get('infrastructure/hypervisors/').then(r => r.data);

export const getHypervisor = (id) =>
  infraAxios.get(`infrastructure/hypervisors/${id}/`).then(r => r.data);

export const createHypervisor = (data) =>
  infraAxios.post('infrastructure/hypervisors/', data).then(r => r.data);

export const updateHypervisor = (id, data) =>
  infraAxios.put(`infrastructure/hypervisors/${id}/`, data).then(r => r.data);

export const deleteHypervisor = (id) =>
  infraAxios.delete(`infrastructure/hypervisors/${id}/`).then(r => r.data);

// --- Virtual Machines ---
export const getVirtualMachines = () =>
  infraAxios.get('infrastructure/virtual-machines/').then(r => r.data);

export const getVirtualMachine = (id) =>
  infraAxios.get(`infrastructure/virtual-machines/${id}/`).then(r => r.data);

export const createVirtualMachine = (data) =>
  infraAxios.post('infrastructure/virtual-machines/', data).then(r => r.data);

export const updateVirtualMachine = (id, data) =>
  infraAxios.put(`infrastructure/virtual-machines/${id}/`, data).then(r => r.data);

export const deleteVirtualMachine = (id) =>
  infraAxios.delete(`infrastructure/virtual-machines/${id}/`).then(r => r.data);

export const initializeVM = (id, data) =>
  infraAxios.post(`infrastructure/virtual-machines/${id}/initialize/`, data).then(r => r.data);

export const getVMInitializationStatus = (id) =>
  infraAxios.get(`infrastructure/virtual-machines/${id}/initialization-status/`).then(r => r.data);

// --- Deployment Targets ---
export const getDeploymentTargets = () =>
  infraAxios.get('infrastructure/targets/').then(r => r.data);

export const createDeploymentTarget = (data) =>
  infraAxios.post('infrastructure/targets/', data).then(r => r.data);

export const deleteDeploymentTarget = (id) =>
  infraAxios.delete(`infrastructure/targets/${id}/`).then(r => r.data);

export const registerTargetFromVM = (data) =>
  infraAxios.post('infrastructure/targets/register-from-vm/', data).then(r => r.data);

export const validateTarget = (id) =>
  infraAxios.post(`infrastructure/targets/${id}/validate/`).then(r => r.data);

export const healthCheckTarget = (id) =>
  infraAxios.get(`infrastructure/targets/${id}/health-check/`).then(r => r.data);

export const disableTarget = (id) =>
  infraAxios.post(`infrastructure/targets/${id}/disable/`).then(r => r.data);

export const enableTarget = (id) =>
  infraAxios.post(`infrastructure/targets/${id}/enable/`).then(r => r.data);

export const getTargetInfo = (id) =>
  infraAxios.get(`infrastructure/targets/${id}/target-info/`).then(r => r.data);

// --- Docker ---
export const getDockerImages = () =>
  infraAxios.get('infrastructure/docker-images/').then(r => r.data);

export const getDockerContainers = () =>
  infraAxios.get('infrastructure/docker-containers/').then(r => r.data);
