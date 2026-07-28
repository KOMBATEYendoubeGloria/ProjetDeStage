import api from './axios';

export const getProjects = () => api.get('projets/');
export const getProject = (id) => api.get(`projets/${id}/`);
export const createProject = (data) => api.post('projets/', data);
export const updateProject = (id, data) => api.put(`projets/${id}/`, data);
export const deleteProject = (id) => api.delete(`projets/${id}/`);