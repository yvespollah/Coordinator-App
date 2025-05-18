import axios from 'axios';

// Configuration de l'URL de base de l'API
// Assurez-vous que cette URL correspond à celle de votre serveur Django
const API_URL = 'http://127.0.0.1:8000/api';

// Création d'une instance axios avec la configuration de base
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Service API pour communiquer avec le backend
const apiService = {
  // Méthodes pour les managers
  getManagers: () => apiClient.get('/managers/'),
  getManager: (id) => apiClient.get(`/managers/${id}/`),
  createManager: (data) => apiClient.post('/managers/', data),
  updateManager: (id, data) => apiClient.put(`/managers/${id}/`, data),
  deleteManager: (id) => apiClient.delete(`/managers/${id}/`),
  registerManager: (data) => apiClient.post('/auth/manager/register/', data),
  loginManager: (data) => apiClient.post('/auth/manager/login/', data),

  // Méthodes pour les workflows
  getWorkflows: () => apiClient.get('/workflows/'),
  getWorkflow: (id) => apiClient.get(`/workflows/${id}/`),
  createWorkflow: (data) => apiClient.post('/workflows/', data),
  updateWorkflow: (id, data) => apiClient.put(`/workflows/${id}/`, data),
  deleteWorkflow: (id) => apiClient.delete(`/workflows/${id}/`),

  // Méthodes pour les tâches
  getTasks: () => apiClient.get('/tasks/'),
  getTask: (id) => apiClient.get(`/tasks/${id}/`),
  createTask: (data) => apiClient.post('/tasks/', data),
  updateTask: (id, data) => apiClient.put(`/tasks/${id}/`, data),
  deleteTask: (id) => apiClient.delete(`/tasks/${id}/`),

  // Méthodes pour les volunteers
  getVolunteers: () => apiClient.get('/volunteers/'),
  getVolunteer: (id) => apiClient.get(`/volunteers/${id}/`),
  createVolunteer: (data) => apiClient.post('/volunteers/', data),
  updateVolunteer: (id, data) => apiClient.put(`/volunteers/${id}/`, data),
  deleteVolunteer: (id) => apiClient.delete(`/volunteers/${id}/`),

  // Méthodes pour les analytics et la santé du système
  getSystemHealth: () => apiClient.get('/system-health/'),
  getWorkflowsByStatus: () => apiClient.get('/analytics/workflows_by_status/'),
  getVolunteersByStatus: () => apiClient.get('/analytics/volunteers_by_status/'),
  getTaskPerformance: () => apiClient.get('/analytics/task_performance/'),
  getResourceUtilization: () => apiClient.get('/analytics/resource_utilization/'),
  getCommunicationStats: () => apiClient.get('/analytics/communication_stats/'),
};

export default apiService;
