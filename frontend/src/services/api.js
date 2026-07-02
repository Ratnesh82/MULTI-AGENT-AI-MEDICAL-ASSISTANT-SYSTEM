import axios from 'axios';

const API = axios.create({ baseURL: '/api/v1' });

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-logout on 401 (expired / invalid token)
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('userName');
      // Reload → App.jsx detects no token and shows login screen
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => API.post('/auth/register', data),
  login: (email, password) => {
    const form = new FormData();
    form.append('username', email);
    form.append('password', password);
    return API.post('/auth/login', form);
  },
};

export const scheduleAPI = {
  request: (text) => API.post('/schedule/request', { text }),
  slots: (specialty = 'General') => API.get(`/schedule/slots?specialty=${specialty}`),
  myAppointments: () => API.get('/schedule/my-appointments'),
  cancel: (id) => API.delete(`/schedule/${id}`),
  explain: (id) => API.get(`/schedule/${id}/explain`),
};

export const wellnessAPI = {
  conditions: () => API.get('/wellness/conditions'),
  diet: (condition, preferences, region) => API.post('/wellness/diet', { condition, preferences, region }),
  dietPdf: (condition, preferences, region) =>
    API.post('/wellness/diet/pdf', { condition, preferences, region }, { responseType: 'blob' }),
  yoga: (condition, severity) => API.post('/wellness/yoga', { condition, severity }),
  meditation: (goal, feedback) => API.post('/wellness/meditation', { goal, feedback }),
  feedback: (module, rating, comment) => API.post('/wellness/feedback', { module, rating, comment }),
  analyzeText: (text) => API.post('/wellness/analyze-text', { text }),
};

export const adminAPI = {
  stats: () => API.get('/admin/stats'),
  appointments: (status = null) => API.get('/admin/appointments' + (status ? `?status=${status}` : '')),
  patients: () => API.get('/admin/patients'),
  doctors: () => API.get('/admin/doctors'),
  addDoctor: (name, specialty) => API.post('/admin/doctors/add', { name, specialty }),
  feedback: () => API.get('/admin/wellness-feedback'),
  fairnessAnalytics: () => API.get('/admin/analytics/fairness'),
};

export const profileAPI = {
  me: () => API.get('/profile/me'),
  healthScore: () => API.get('/profile/health-score'),
  notifications: () => API.get('/profile/notifications'),
  markRead: (id) => API.post(`/profile/notifications/${id}/read`),
  reportPdf: () => API.get('/profile/report/pdf', { responseType: 'blob' }),
};

export default API;
