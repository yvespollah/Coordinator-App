import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, Button, Avatar, Stack, Divider, CircularProgress, Tooltip } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import GroupIcon from '@mui/icons-material/Group';
import AssignmentIcon from '@mui/icons-material/Assignment';
import ListAltIcon from '@mui/icons-material/ListAlt';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { Link } from 'react-router-dom';
import {
  fetchManagersCount,
  fetchVolunteersCount,
  fetchWorkflowsCount,
  fetchTasksCount,
  fetchActiveVolunteers,
  fetchRunningWorkflows,
  fetchSystemHealth,
  fetchWorkflowsByStatus,
  fetchVolunteersByStatus
} from './apiHome';
import { PieChart, Pie, Cell, Legend, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const Home = () => {
  // State for dashboard stats
  const [stats, setStats] = useState({ managers: 0, volunteers: 0, workflows: 0, tasks: 0 });
  const [loadingStats, setLoadingStats] = useState(true);
  const [activeVolunteers, setActiveVolunteers] = useState([]);
  const [loadingVolunteers, setLoadingVolunteers] = useState(true);
  const [errorVolunteers, setErrorVolunteers] = useState(null);
  const [runningWorkflows, setRunningWorkflows] = useState([]);
  const [loadingRunningWorkflows, setLoadingRunningWorkflows] = useState(true);
  const [errorRunningWorkflows, setErrorRunningWorkflows] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [errorHealth, setErrorHealth] = useState(null);
  const [workflowStatusData, setWorkflowStatusData] = useState([]);
  const [volunteerStatusData, setVolunteerStatusData] = useState([]);
  const [loadingCharts, setLoadingCharts] = useState(true);

  // Color mapping for statuses
  const STATUS_COLORS = {
    CREATED: '#1976d2',
    VALIDATED: '#0288d1',
    SUBMITTED: '#42a5f5',
    SPLITTING: '#7e57c2',
    ASSIGNING: '#8d6e63',
    PENDING: '#ed6c02',
    RUNNING: '#2e7d32',
    PAUSED: '#ffd600',
    PARTIAL_FAILURE: '#fbc02d',
    REASSIGNING: '#00bcd4',
    AGGREGATING: '#ab47bc',
    COMPLETED: '#00e676',
    FAILED: '#d32f2f',
    available: '#00e676',
    busy: '#ed6c02',
    offline: '#757575',
    maintenance: '#ffd600',
  };

  // Fetch all dashboard data on mount
  useEffect(() => {
    // Stats
    setLoadingStats(true);
    Promise.all([
      fetchManagersCount(),
      fetchVolunteersCount(),
      fetchWorkflowsCount(),
      fetchTasksCount()
    ]).then(([managers, volunteers, workflows, tasks]) => {
      setStats({ managers, volunteers, workflows, tasks });
      setLoadingStats(false);
    });

    // Active Volunteers
    setLoadingVolunteers(true);
    fetchActiveVolunteers().then(
      (volunteerData) => {
        setActiveVolunteers(volunteerData);
        setLoadingVolunteers(false);
      },
      (err) => {
        setErrorVolunteers('Failed to load volunteers');
        setLoadingVolunteers(false);
      }
    );

    // Running Workflows
    setLoadingRunningWorkflows(true);
    fetchRunningWorkflows().then(
      (data) => {
        setRunningWorkflows(data);
        setLoadingRunningWorkflows(false);
      },
      (err) => {
        setErrorRunningWorkflows('Failed to load running workflows');
        setLoadingRunningWorkflows(false);
      }
    );

    // System Health
    fetchSystemHealth().then(
      (data) => {
        setSystemHealth(data);
        setLoadingHealth(false);
      },
      (err) => {
        setErrorHealth('Failed to load system health');
        setLoadingHealth(false);
      }
    );
    
    // Analytics (Charts)
    setLoadingCharts(true);
    Promise.all([
      fetchWorkflowsByStatus(),
      fetchVolunteersByStatus()
    ]).then(([wfData, volData]) => {
      setWorkflowStatusData(wfData);
      setVolunteerStatusData(volData);
      setLoadingCharts(false);
    });
  }, []);

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      {/* Welcome Section */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, borderRadius: 3, textAlign: 'center', background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Welcome to Coordinator App
        </Typography>
        <Typography variant="subtitle1">
          Manage distributed volunteers, workflows, and tasks with ease.
        </Typography>
      </Paper>

      {/* Dashboard Content */}
      {/* Quick Stats Section */}
      <Grid container spacing={3} justifyContent="center" mb={4}>
        {loadingStats ? (
          <Grid item xs={12} sx={{ textAlign: 'center' }}>
            <CircularProgress />
          </Grid>
        ) : (
          [
            { label: 'Managers', value: stats.managers, icon: <DashboardIcon color="primary" /> },
            { label: 'Volunteers', value: stats.volunteers, icon: <GroupIcon color="success" /> }, 
            { label: 'Workflows', value: stats.workflows, icon: <AssignmentIcon color="info" /> },
            { label: 'Tasks', value: stats.tasks, icon: <ListAltIcon color="warning" /> },
          ].map((stat) => (
            <Grid item xs={6} sm={3} key={stat.label}>
              <Paper elevation={2} sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', borderRadius: 2 }}>
                <Avatar sx={{ bgcolor: 'white', color: 'primary.main', mb: 1, width: 48, height: 48 }}>
                  {stat.icon}
                </Avatar>
                <Typography variant="h5" fontWeight={600}>{stat.value}</Typography>
                <Typography variant="body2" color="text.secondary">{stat.label}</Typography>
              </Paper>
            </Grid>
          ))
        )}
      </Grid>
      
      {/* Running Workflows Widget */}
      <Paper elevation={1} sx={{ p: 3, mb: 4, borderRadius: 2, background: '#fffbea' }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <PlayArrowIcon color="warning" />
          <Typography variant="h6" fontWeight={600}>Running Workflows</Typography>
        </Stack>
        {loadingRunningWorkflows ? <CircularProgress size={20} /> : errorRunningWorkflows ? (
          <Typography variant="body2" color="error">{errorRunningWorkflows}</Typography>
        ) : runningWorkflows.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No workflows currently running.</Typography>
        ) : (
          <Stack spacing={1}>
            {runningWorkflows.map((wf, idx) => (
              <Typography key={idx} variant="body2">
                {wf.name || wf.title || wf.id || JSON.stringify(wf)}
              </Typography>
            ))}
          </Stack>
        )}
      </Paper>

      {/* Quick Actions Section */}
      <Paper elevation={1} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Typography variant="h6" fontWeight={600} mb={2}>
          Quick Actions
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button variant="contained" component={Link} to="/manager" color="primary">View Managers</Button>
          <Button variant="contained" component={Link} to="/volunteer" color="success">View Volunteers</Button>
          <Button variant="contained" component={Link} to="/workflows" color="info">View Workflows</Button>
          <Button variant="contained" component={Link} to="/logs" color="secondary">Communication Logs</Button>
        </Stack>
      </Paper>

      {/* System Health */}
      <Paper elevation={1} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <HealthAndSafetyIcon color={loadingHealth ? 'disabled' : systemHealth?.status === 'ok' ? 'success' : 'warning'} />
          <Typography variant="h6" fontWeight={600}>System Health</Typography>
        </Stack>
        {loadingHealth ? <CircularProgress size={20} /> : errorHealth ? (
          <Typography variant="body2" color="error">{errorHealth}</Typography>
        ) : (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                <Typography variant="body2" color="text.secondary">Database</Typography>
                <Typography variant="body1" fontWeight={500} color={systemHealth?.details?.database === 'connected' ? 'success.main' : 'error.main'}>
                  {systemHealth?.details?.database || 'Unknown'}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                <Typography variant="body2" color="text.secondary">Active Volunteers</Typography>
                <Typography variant="body1" fontWeight={500}>
                  {systemHealth?.details?.active_volunteers || 0}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                <Typography variant="body2" color="text.secondary">Recent Errors</Typography>
                <Typography variant="body1" fontWeight={500} color={systemHealth?.details?.recent_errors > 0 ? 'error.main' : 'text.primary'}>
                  {systemHealth?.details?.recent_errors || 0}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                <Typography variant="body2" color="text.secondary">Overall Status</Typography>
                <Typography variant="body1" fontWeight={500} color={systemHealth?.status === 'ok' ? 'success.main' : 'warning.main'}>
                  {systemHealth?.status || 'Unknown'}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Analytics Section */}
      <Grid container spacing={3} mb={4}>
        {/* Workflow Status Chart */}
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" fontWeight={600} mb={2}>Workflow Status Distribution</Typography>
            {loadingCharts ? <CircularProgress size={20} /> : workflowStatusData.length === 0 ? (
              <Typography variant="body2" color="text.secondary">No workflow data available.</Typography>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={workflowStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {workflowStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || `#${Math.floor(Math.random()*16777215).toString(16)}`} />
                    ))}
                  </Pie>
                  <Legend />
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Volunteer Status Chart */}
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" fontWeight={600} mb={2}>Volunteer Status Distribution</Typography>
            {loadingCharts ? <CircularProgress size={20} /> : volunteerStatusData.length === 0 ? (
              <Typography variant="body2" color="text.secondary">No volunteer data available.</Typography>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={volunteerStatusData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="value" name="Count" fill="#8884d8">
                    {volunteerStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || `#${Math.floor(Math.random()*16777215).toString(16)}`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Home;