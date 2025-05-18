import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, CircularProgress, Grid, Tab, Tabs, Card, CardContent, Divider } from '@mui/material';
import { 
  PieChart, Pie, Cell, Legend, Tooltip as RechartsTooltip, ResponsiveContainer, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, AreaChart, Area,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ScatterChart, Scatter
} from 'recharts';
import { 
  fetchWorkflowsByStatus, fetchVolunteersByStatus, fetchTaskPerformance,
  fetchResourceUtilization, fetchCommunicationStats
} from './apiHome';
import AssessmentIcon from '@mui/icons-material/Assessment';
import MemoryIcon from '@mui/icons-material/Memory';
import MessageIcon from '@mui/icons-material/Message';
import SpeedIcon from '@mui/icons-material/Speed';

// TabPanel component for the tabs
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

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
  const [tabValue, setTabValue] = useState(0);
  const [workflowStatusData, setWorkflowStatusData] = useState([]);
  const [volunteerStatusData, setVolunteerStatusData] = useState([]);
  const [taskPerformanceData, setTaskPerformanceData] = useState([]);
  const [resourceUtilizationData, setResourceUtilizationData] = useState([]);
  const [communicationStatsData, setCommunicationStatsData] = useState({
    hourlyData: [],
    messageTypes: []
  });
  const [loadingCharts, setLoadingCharts] = useState(true);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  useEffect(() => {
    setLoadingCharts(true);
    Promise.all([
      fetchWorkflowsByStatus(),
      fetchVolunteersByStatus(),
      fetchTaskPerformance(),
      fetchResourceUtilization(),
      fetchCommunicationStats()
    ]).then(([wfData, volData, taskData, resourceData, commData]) => {
      setWorkflowStatusData(wfData);
      setVolunteerStatusData(volData);
      setTaskPerformanceData(taskData);
      setResourceUtilizationData(resourceData);
      setCommunicationStatsData(commData);
      setLoadingCharts(false);
    }).catch(error => {
      console.error("Error fetching analytics data:", error);
      setLoadingCharts(false);
    });
  }, []);

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, borderRadius: 3, background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Performance & Analytics
        </Typography>
        <Typography variant="subtitle1">
          Visualize key system metrics, workflow status distribution, and volunteer status at a glance.
        </Typography>
      </Paper>

      {/* Tabs for different analytics views */}
      <Paper elevation={1} sx={{ mb: 4, borderRadius: 2 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          variant="fullWidth"
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab icon={<AssessmentIcon />} label="Status Overview" />
          <Tab icon={<SpeedIcon />} label="Performance Metrics" />
          <Tab icon={<MemoryIcon />} label="Resource Utilization" />
          <Tab icon={<MessageIcon />} label="Communication Analytics" />
        </Tabs>

        {/* Status Overview Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Workflows by Status</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
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
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Volunteers by Status</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
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
        </TabPanel>

        {/* Performance Metrics Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Task Execution Time by Type</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={taskPerformanceData}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis label={{ value: 'Minutes', angle: -90, position: 'insideLeft' }} />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="avgExecutionTime" name="Avg. Execution Time (min)" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Task Success Rate by Type</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={taskPerformanceData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="name" />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} />
                      <Radar name="Success Rate (%)" dataKey="successRate" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                      <Legend />
                      <RechartsTooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Task Count by Type</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart
                      data={taskPerformanceData}
                      margin={{
                        top: 10,
                        right: 30,
                        left: 0,
                        bottom: 0,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area type="monotone" dataKey="count" name="Number of Tasks" stroke="#82ca9d" fill="#82ca9d" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Resource Utilization Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Resource Utilization by Volunteer</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={resourceUtilizationData}
                      margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis label={{ value: 'Utilization (%)', angle: -90, position: 'insideLeft' }} />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="cpu" name="CPU %" fill="#8884d8" />
                      <Bar dataKey="ram" name="RAM %" fill="#82ca9d" />
                      <Bar dataKey="disk" name="Disk %" fill="#ffc658" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Resource Utilization Comparison</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={300}>
                    <ScatterChart
                      margin={{
                        top: 20,
                        right: 20,
                        bottom: 20,
                        left: 20,
                      }}
                    >
                      <CartesianGrid />
                      <XAxis type="number" dataKey="cpu" name="CPU %" unit="%" />
                      <YAxis type="number" dataKey="ram" name="RAM %" unit="%" />
                      <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                      <Scatter name="Resource Usage" data={resourceUtilizationData} fill="#8884d8">
                        {resourceUtilizationData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.cpu > 70 || entry.ram > 70 ? '#ff7300' : '#82ca9d'} />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Communication Analytics Tab */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Message Volume by Hour</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart
                      data={communicationStatsData.hourlyData || []}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Line type="monotone" dataKey="managerMessages" name="Manager Messages" stroke="#8884d8" activeDot={{ r: 8 }} />
                      <Line type="monotone" dataKey="volunteerMessages" name="Volunteer Messages" stroke="#82ca9d" />
                      <Line type="monotone" dataKey="systemMessages" name="System Messages" stroke="#ffc658" />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Message Types Distribution</Typography>
                {loadingCharts ? <CircularProgress size={20} /> : (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={communicationStatsData.messageTypes || []}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {(communicationStatsData.messageTypes || []).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={`#${Math.floor(Math.random()*16777215).toString(16)}`} />
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
              <Paper elevation={1} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
                <Typography variant="h6" fontWeight={600} mb={2}>Communication Summary</Typography>
                <Box sx={{ mt: 2 }}>
                  {loadingCharts ? (
                    <CircularProgress size={20} />
                  ) : (
                    <Grid container spacing={2}>
                      {[
                        { title: 'Total Messages Today', value: communicationStatsData.hourlyData?.reduce((sum, hour) => sum + hour.total, 0) || 0, color: '#1976d2' },
                        { title: 'Manager Messages', value: communicationStatsData.hourlyData?.reduce((sum, hour) => sum + hour.managerMessages, 0) || 0, color: '#8884d8' },
                        { title: 'Volunteer Messages', value: communicationStatsData.hourlyData?.reduce((sum, hour) => sum + hour.volunteerMessages, 0) || 0, color: '#82ca9d' },
                        { title: 'System Messages', value: communicationStatsData.hourlyData?.reduce((sum, hour) => sum + hour.systemMessages, 0) || 0, color: '#ffc658' }
                      ].map((stat, index) => (
                        <Grid item xs={6} key={index}>
                          <Card sx={{ bgcolor: '#f8f9fa', height: '100%' }}>
                            <CardContent>
                              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                {stat.title}
                              </Typography>
                              <Typography variant="h4" sx={{ color: stat.color, fontWeight: 'bold' }}>
                                {stat.value}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default Analytics;
