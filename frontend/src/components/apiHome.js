// Utility functions to fetch homepage data
import AxiosInstance from './axios';

export const fetchManagersCount = async () => {
  const res = await AxiosInstance.get('api/managers/');
  return Array.isArray(res.data) ? res.data.length : 0;
};

export const fetchVolunteersCount = async () => {
  const res = await AxiosInstance.get('api/volunteers/');
  return Array.isArray(res.data) ? res.data.length : 0;
};


export const fetchWorkflowsCount = async () => {
  const res = await AxiosInstance.get('api/workflows/');
  return Array.isArray(res.data) ? res.data.length : 0;
};

export const fetchTasksCount = async () => {
  const res = await AxiosInstance.get('api/tasks/');
  return Array.isArray(res.data) ? res.data.length : 0;
};

export const fetchRecentLogs = async () => {
  const res = await AxiosInstance.get('api/logs/?limit=5');
  return Array.isArray(res.data) ? res.data : [];
};

export const fetchAnnouncements = async () => {
  const res = await AxiosInstance.get('api/announcements/?limit=3');
  return Array.isArray(res.data) ? res.data : [];
};

export const fetchActiveVolunteers = async () => {
  const res = await AxiosInstance.get('api/volunteers/?active=true&limit=5');
  return Array.isArray(res.data) ? res.data : [];
};

export const fetchRunningWorkflows = async () => {
  // Adjust endpoint or params if your backend uses a different filter for running workflows
  const res = await AxiosInstance.get('api/workflows/?status=running');
  return Array.isArray(res.data) ? res.data : [];
};

export async function fetchSystemHealth() {
  const res = await AxiosInstance.get('api/system-health/');
  return res.data;
}

export async function fetchWorkflowsByStatus() {
  const res = await AxiosInstance.get('api/analytics/workflows_by_status/');
  return res.data;
}

export async function fetchVolunteersByStatus() {
  const res = await AxiosInstance.get('api/analytics/volunteers_by_status/');
  return res.data;
}

// Nouvelles fonctions pour les analytics supplémentaires
export async function fetchTaskPerformance() {
  const res = await AxiosInstance.get('api/analytics/task_performance/');
  return res.data;
}

export async function fetchResourceUtilization() {
  const res = await AxiosInstance.get('api/analytics/resource_utilization/');
  return res.data;
}

export async function fetchCommunicationStats() {
  const res = await AxiosInstance.get('api/analytics/communication_stats/');
  return res.data;
}
