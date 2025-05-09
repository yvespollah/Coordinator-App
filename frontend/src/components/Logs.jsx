import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, CircularProgress, Alert, Button } from '@mui/material';
import SettingsInputAntennaIcon from '@mui/icons-material/SettingsInputAntenna';
import RefreshIcon from '@mui/icons-material/Refresh';
import { fetchChannels } from './apiLogs';

const Logs = () => {
  const [channels, setChannels] = useState([]);
  const [loadingChannels, setLoadingChannels] = useState(false);
  const [errorChannels, setErrorChannels] = useState(null);

  // Fetch channels data when component mounts
  useEffect(() => {
    fetchChannelsData();
  }, []);

  // Function to fetch channels data
  const fetchChannelsData = async () => {
    setLoadingChannels(true);
    setErrorChannels(null);
    try {
      const channelsData = await fetchChannels();
      console.log('Channels data:', channelsData);
      setChannels(channelsData);
    } catch (error) {
      console.error('Error fetching channels:', error);
      setErrorChannels('Failed to load communication channels. Please try again later.');
    } finally {
      setLoadingChannels(false);
    }
  };

  // Exemple de données de canaux simulées (utilisées si l'API ne retourne pas de données)
  const sampleChannels = channels.length > 0 ? channels : [
    { name: 'auth/register', description: 'Inscription des managers et volunteers', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 3 },
    { name: 'auth/response', description: 'Réponses d\'authentification', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 2 },
    { name: 'tasks/new', description: 'Nouvelles tâches des managers', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 5 },
    { name: 'tasks/assign', description: 'Attribution des tâches aux volunteers', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 4 },
    { name: 'tasks/status/#', description: 'État des tâches en cours', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 7 },
    { name: 'tasks/result/#', description: 'Résultats des tâches terminées', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 6 },
    { name: 'coord/heartbeat/#', description: 'Signaux de vie des participants', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 8 },
    { name: 'coord/status', description: 'État global du système', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 2 },
    { name: 'volunteer/available', description: 'Liste des volunteers disponibles', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 3 },
    { name: 'volunteer/resources', description: 'Ressources des volunteers', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 2 },
    { name: 'manager/status', description: 'État des managers', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 4 },
    { name: 'manager/requests', description: 'Requêtes spéciales des managers', created_at: '2025-05-01T10:00:00Z', active: true, subscribers: 3 }
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

  // Fonction pour obtenir la couleur du chip en fonction du nom du canal
  const getChannelChipColor = (channelName) => {
    if (channelName.startsWith('auth/')) return 'secondary';
    if (channelName.startsWith('tasks/')) return 'warning';
    if (channelName.startsWith('coord/')) return 'info';
    if (channelName.startsWith('volunteer/')) return 'success';
    if (channelName.startsWith('manager/')) return 'primary';
    return 'default';
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, borderRadius: 3, background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SettingsInputAntennaIcon fontSize="large" />
          <div>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Communication Channels
            </Typography>
            <Typography variant="subtitle1">
              View all available communication channels in the system
            </Typography>
          </div>
        </Box>
      </Paper>

      {/* Channels Content */}
      <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsInputAntennaIcon fontSize="small" />
            Available Channels
          </Typography>
          <Button 
            startIcon={<RefreshIcon />} 
            variant="outlined" 
            size="small"
            onClick={fetchChannelsData}
            disabled={loadingChannels}
          >
            Refresh
          </Button>
        </Box>
        
        {loadingChannels ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : errorChannels ? (
          <Alert severity="error" sx={{ my: 2 }}>{errorChannels}</Alert>
        ) : (
          <TableContainer component={Paper} variant="outlined" sx={{ mt: 2 }}>
            <Table>
              <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell><strong>Channel</strong></TableCell>
                  <TableCell><strong>Description</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell><strong>Subscribers</strong></TableCell>
                  <TableCell><strong>Created</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sampleChannels.map((channel) => (
                  <TableRow key={channel.name} hover>
                    <TableCell>
                      <Chip 
                        label={channel.name} 
                        color={getChannelChipColor(channel.name)}
                        size="small"
                        sx={{ fontFamily: 'monospace', fontWeight: 500 }}
                      />
                    </TableCell>
                    <TableCell>{channel.description}</TableCell>
                    <TableCell>
                      <Chip 
                        label={channel.active ? 'Active' : 'Inactive'} 
                        color={channel.active ? 'success' : 'default'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{channel.subscribers}</TableCell>
                    <TableCell>{formatTimestamp(channel.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        
        <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
          These channels are used for communication between managers and volunteers in the Coordinator system.
          Each channel has a specific purpose and is used for different types of messages.
        </Typography>
        
        {channels.length === 0 && !loadingChannels && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Currently showing sample data. Click Refresh to fetch real channel data from the server.
          </Alert>
        )}
      </Paper>
    </Box>
  );
};

export default Logs;
