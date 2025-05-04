import React, { useState } from 'react';
import { Box, Typography, Paper, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import MessageIcon from '@mui/icons-material/Message';
import SyncIcon from '@mui/icons-material/Sync';
import HistoryIcon from '@mui/icons-material/History';

// TabPanel component for the tabs
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
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

const Logs = () => {
  const [tabValue, setTabValue] = useState(0);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Exemple de données de communication simulées
  const recentMessages = [
    { id: 1, type: 'manager', title: 'Manager Status', content: 'Manager admin is now active', timestamp: '2025-05-04T19:30:00Z' },
    { id: 2, type: 'volunteer', title: 'Volunteer Status', content: 'Volunteer V-1001 is now available', timestamp: '2025-05-04T19:25:00Z' },
    { id: 3, type: 'task', title: 'New Task', content: 'Task T-2345: Data Processing', timestamp: '2025-05-04T19:20:00Z' },
    { id: 4, type: 'result', title: 'Task Result', content: 'Task T-2344 completed with status: success', timestamp: '2025-05-04T19:15:00Z' },
    { id: 5, type: 'manager', title: 'Manager Status', content: 'Manager user1 is now inactive', timestamp: '2025-05-04T19:10:00Z' }
  ];

  // Fonction pour formater les timestamps
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (e) {
      return 'Invalid date';
    }
  };

  // Fonction pour obtenir la couleur du chip en fonction du type de message
  const getChipColor = (type) => {
    switch (type) {
      case 'manager':
        return 'primary';
      case 'volunteer':
        return 'success';
      case 'task':
        return 'warning';
      case 'result':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, borderRadius: 3, background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Communication Logs
        </Typography>
        <Typography variant="subtitle1">
          Monitor real-time communication between managers and volunteers
        </Typography>
      </Paper>

      {/* Tabs for different log views */}
      <Paper elevation={1} sx={{ mb: 4, borderRadius: 2 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          variant="fullWidth"
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab icon={<SyncIcon />} label="Real-time Monitor" />
          <Tab icon={<HistoryIcon />} label="Historical Logs" />
          <Tab icon={<MessageIcon />} label="Message Archive" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {/* Real-time Monitor Content */}
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Communication Activity
            </Typography>
            
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Content</TableCell>
                    <TableCell>Timestamp</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentMessages.map((message) => (
                    <TableRow key={message.id}>
                      <TableCell>
                        <Chip 
                          label={message.type.charAt(0).toUpperCase() + message.type.slice(1)} 
                          color={getChipColor(message.type)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{message.title}</TableCell>
                      <TableCell>{message.content}</TableCell>
                      <TableCell>{formatTimestamp(message.timestamp)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Note: This is a static view. Real-time updates will be available in a future release.
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Historical Logs Content */}
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Historical Communication Logs
            </Typography>
            <Typography variant="body1" color="text.secondary">
              This feature will display historical logs of all communications between managers and volunteers.
              You'll be able to search, filter, and export logs for analysis.
            </Typography>
            <Typography variant="body2" color="primary" sx={{ mt: 2 }}>
              Coming soon in the next update.
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Message Archive Content */}
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Message Archive
            </Typography>
            <Typography variant="body1" color="text.secondary">
              This feature will allow you to browse and search through all messages exchanged in the system.
              You'll be able to view message details, track conversations, and analyze communication patterns.
            </Typography>
            <Typography variant="body2" color="primary" sx={{ mt: 2 }}>
              Coming soon in the next update.
            </Typography>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default Logs;
