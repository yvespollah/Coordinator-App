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
  // Initialize with fallback data
  const [stats, setStats] = useState({
    managers: 2,
    volunteers: 5,
    workflows: 3,
    tasks: 10
  });
  const [loadingStats, setLoadingStats] = useState(true);
  const [activeVolunteers, setActiveVolunteers] = useState([
    { id: '1', name: 'Volunteer 1', status: 'available', last_update: new Date().toISOString() },
    { id: '2', name: 'Volunteer 2', status: 'available', last_update: new Date().toISOString() },
    { id: '3', name: 'Volunteer 3', status: 'available', last_update: new Date().toISOString() },
    { id: '4', name: 'Volunteer 4', status: 'available', last_update: new Date().toISOString() },
    { id: '5', name: 'Volunteer 5', status: 'available', last_update: new Date().toISOString() }
  ]);
  const [loadingVolunteers, setLoadingVolunteers] = useState(true);
  const [errorVolunteers, setErrorVolunteers] = useState(null);
  const [runningWorkflows, setRunningWorkflows] = useState([
    { id: '1', name: 'Data Processing', status: 'RUNNING', owner: { username: 'admin' }, created_at: new Date().toISOString() },
    { id: '2', name: 'Image Analysis', status: 'RUNNING', owner: { username: 'yves' }, created_at: new Date().toISOString() }
  ]);
  const [loadingRunningWorkflows, setLoadingRunningWorkflows] = useState(true);
  const [errorRunningWorkflows, setErrorRunningWorkflows] = useState(null);
  const [systemHealth, setSystemHealth] = useState({
    status: 'ok',
    details: {
      database: 'connected',
      active_volunteers: 3,
      recent_errors: 0,
      redis_connection: 'connected'
    }
  });
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [errorHealth, setErrorHealth] = useState(null);
  const [workflowStatusData, setWorkflowStatusData] = useState({
    CREATED: 2,
    RUNNING: 3,
    COMPLETED: 5,
    FAILED: 1
  });
  const [volunteerStatusData, setVolunteerStatusData] = useState({
    available: 3,
    busy: 2,
    offline: 1
  });
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

  // Function to fetch all dashboard data
  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [statsData, volunteerData, workflowsData, healthData, chartsData] = await Promise.all([
        Promise.all([
          fetchManagersCount(),
          fetchVolunteersCount(),
          fetchWorkflowsCount(),
          fetchTasksCount()
        ]),
        fetchActiveVolunteers(),
        fetchRunningWorkflows(),
        fetchSystemHealth(),
        Promise.all([
          fetchWorkflowsByStatus(),
          fetchVolunteersByStatus()
        ])
      ]);

      // Compare and update stats only if changed
      const [managers, volunteers, workflows, tasks] = statsData;
      const currentStats = { managers, volunteers, workflows, tasks };
      if (JSON.stringify(currentStats) !== JSON.stringify(stats)) {
        setStats(currentStats);
      }

      // Compare and update volunteers only if changed
      if (JSON.stringify(volunteerData) !== JSON.stringify(activeVolunteers)) {
        setActiveVolunteers(volunteerData);
      }

      // Compare and update workflows only if changed
      if (JSON.stringify(workflowsData) !== JSON.stringify(runningWorkflows)) {
        setRunningWorkflows(workflowsData);
      }

      // Compare and update health only if changed
      if (JSON.stringify(healthData) !== JSON.stringify(systemHealth)) {
        setSystemHealth(healthData);
      }

      // Compare and update charts data only if changed
      const [workflowsChartData, volunteersChartData] = chartsData;
      if (JSON.stringify(workflowsChartData) !== JSON.stringify(workflowStatusData)) {
        setWorkflowStatusData(workflowsChartData);
      }
      if (JSON.stringify(volunteersChartData) !== JSON.stringify(volunteerStatusData)) {
        setVolunteerStatusData(volunteersChartData);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set fallback data only if current state is empty
      if (!stats.managers) {
        setStats({ managers: 2, volunteers: 5, workflows: 3, tasks: 10 });
      }
      if (!activeVolunteers.length) {
        setActiveVolunteers([]);
      }
      if (!runningWorkflows.length) {
        setRunningWorkflows([
          { id: '1', name: 'Data Processing', status: 'RUNNING', owner: { username: 'admin' }, created_at: new Date().toISOString() },
          { id: '2', name: 'Image Analysis', status: 'RUNNING', owner: { username: 'yves' }, created_at: new Date().toISOString() }
        ]);
      }
      if (!systemHealth) {
        setSystemHealth({
          status: 'error',
          details: {
            database: 'disconnected',
            active_volunteers: 0,
            recent_errors: 1,
            redis_connection: 'disconnected'
          }
        });
      }
      if (!workflowStatusData.length) {
        setWorkflowStatusData({
          CREATED: 2,
          RUNNING: 3,
          COMPLETED: 5,
          FAILED: 1
        });
      }
      if (!volunteerStatusData.length) {
        setVolunteerStatusData({
          available: 3,
          busy: 2,
          offline: 1
        });
      }
    }
  };

  // Set up real-time updates
  useEffect(() => {
    // Initial fetch
    fetchAllData();

    // Set up interval for real-time updates every 2 seconds
    const interval = setInterval(fetchAllData, 2000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
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
        {[
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
        ))}
      </Grid>
      
      {/* Running Workflows Widget */}
      <Paper elevation={1} sx={{ p: 3, mb: 4, borderRadius: 2, background: '#fffbea' }}>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <PlayArrowIcon color="warning" />
          <Typography variant="h6" fontWeight={600}>Running Workflows</Typography>
        </Stack>
        {runningWorkflows.length === 0 ? (
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
          {/* <Button variant="contained" component={Link} to="/logs" color="secondary">Communication Logs</Button> */}
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
          <Typography color="textSecondary">Workflows</Typography>
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