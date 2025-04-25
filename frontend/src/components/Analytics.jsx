import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Grid } from '@mui/material';
import { PieChart, Pie, Cell, Legend, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { fetchWorkflowsByStatus, fetchVolunteersByStatus } from './apiHome';

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

const Analytics = () => {
  const [workflowStatusData, setWorkflowStatusData] = useState([]);
  const [volunteerStatusData, setVolunteerStatusData] = useState([]);
  const [loadingCharts, setLoadingCharts] = useState(true);

  useEffect(() => {
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
    <Box>
      <Typography variant="h4" fontWeight={700} mb={3}>
        Performance & Analytics
      </Typography>
      <Typography variant="body1" mb={4}>
        Visualize key system metrics, workflow status distribution, and volunteer status at a glance.
      </Typography>
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: 340 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>Workflows by Status</Typography>
            {loadingCharts ? <CircularProgress size={20} /> : (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={workflowStatusData} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} fill="#1976d2" label>
                    {workflowStatusData.map((entry, idx) => (
                      <Cell key={`cell-wf-${entry.status}`} fill={STATUS_COLORS[entry.status] || '#90caf9'} />
                    ))}
                  </Pie>
                  <Legend />
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: 340 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>Volunteers by Status</Typography>
            {loadingCharts ? <CircularProgress size={20} /> : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={volunteerStatusData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="current_status" />
                  <YAxis allowDecimals={false} />
                  <Bar dataKey="count">
                    {volunteerStatusData.map((entry, idx) => (
                      <Cell key={`cell-vol-${entry.current_status}`} fill={STATUS_COLORS[entry.current_status] || '#bdbdbd'} />
                    ))}
                  </Bar>
                  <Legend />
                  <RechartsTooltip />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
