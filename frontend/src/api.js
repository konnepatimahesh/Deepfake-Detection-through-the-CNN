import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  verify: () => api.get('/auth/verify'),
};

export const detectionAPI = {
  analyzeImage: (formData) =>
    api.post('/detection/analyze/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  analyzeVideo: (formData) =>
    api.post('/detection/analyze/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getHistory: (page = 1, perPage = 10) =>
    api.get(`/detection/history?page=${page}&per_page=${perPage}`),
  getStats: () => api.get('/detection/stats'),
  deleteAnalysis: (id) => api.delete(`/detection/history/${id}`),
};

export const adminAPI = {
  getUsers: (page = 1, perPage = 20) =>
    api.get(`/admin/users?page=${page}&per_page=${perPage}`),
  getAllHistory: (page = 1, perPage = 20) =>
    api.get(`/admin/all-history?page=${page}&per_page=${perPage}`),
  getStats: () => api.get('/admin/stats'),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  updateUserRole: (id, role) => api.put(`/admin/users/${id}/role`, { role }),
};

export default api;