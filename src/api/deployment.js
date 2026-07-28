import api from './axios';

export const getDeployments = (params) => api.get('deploiements/', { params });
export const getDeployment = (id) => api.get(`deploiements/${id}/`);
export const createDeployment = (data) => api.post('deploiements/', data);
export const deleteDeployment = (id) => api.delete(`deploiements/${id}/`);
export const lancerDeployment = (id) => api.post(`deploiements/${id}/lancer/`);
export const terminerDeployment = (id, statut) => api.post(`deploiements/${id}/terminer/`, { statut });