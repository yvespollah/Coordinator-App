// Utility functions to fetch homepage data
import AxiosInstance from './axios';

export const fetchManagersCount = async () => {
  const res = await AxiosInstance.get('managers/');
  return Array.isArray(res.data) ? res.data.length : 0;
};

export const fetchVolunteersCount = async () => {
  const res = await AxiosInstance.get('api/volunteers/');
  return Array.isArray(res.data) ? res.data.length : 0;
};


export const fetchWorkflowsCount = async () => {
  const res = await AxiosInstance.get('workflows/');
  return Array.isArray(res.data) ? res.data.length : 0;
};

export const fetchTasksCount = async () => {
  const res = await AxiosInstance.get('tasks/');
  return Array.isArray(res.data) ? res.data.length : 0;
};

export const fetchRecentLogs = async () => {
  const res = await AxiosInstance.get('logs/?limit=5');
  return Array.isArray(res.data) ? res.data : [];
};

export const fetchAnnouncements = async () => {
  const res = await AxiosInstance.get('announcements/?limit=3');
  return Array.isArray(res.data) ? res.data : [];
};

export const fetchActiveVolunteers = async () => {
  const res = await AxiosInstance.get('api/volunteers/?active=true&limit=5');
  return Array.isArray(res.data) ? res.data : [];
};

export const fetchRunningWorkflows = async () => {
  // Adjust endpoint or params if your backend uses a different filter for running workflows
  const res = await AxiosInstance.get('workflows/?status=running');
  return Array.isArray(res.data) ? res.data : [];
};

export async function fetchSystemHealth() {
  const res = await AxiosInstance.get('system-health/');
  return res.data;
}

export async function fetchWorkflowsByStatus() {
  const res = await AxiosInstance.get('analytics/workflows_by_status/');
  return res.data;
}

export async function fetchVolunteersByStatus() {
  const res = await AxiosInstance.get('analytics/volunteers_by_status/');
  return res.data;
}
