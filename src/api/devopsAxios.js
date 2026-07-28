import axios from 'axios';

const devopsApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/devops/api/',
});

devopsApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

devopsApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Les endpoints devops/api/* renvoient toujours {success, message, data, errors}
// unwrap() extrait directement "data" et transforme les échecs en vraies erreurs JS
export async function unwrap(promise) {
  const { data } = await promise;
  if (!data.success) {
    throw new Error((data.errors && data.errors.join(', ')) || data.message);
  }
  return data.data;
}

export default devopsApi;
