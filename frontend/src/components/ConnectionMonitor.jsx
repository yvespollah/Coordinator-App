import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  Chip, 
  Stack,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  Badge
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import ComputerIcon from '@mui/icons-material/Computer';
import CircleIcon from '@mui/icons-material/Circle';
import DnsIcon from '@mui/icons-material/Dns';
import communicationService from '../services/communicationService';

const ConnectionMonitor = () => {
  const [connections, setConnections] = useState({
    managers: [],
    volunteers: [],
    total: 0,
    connected: 0
  });
  const [recentMessages, setRecentMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Récupérer les statistiques initiales
    fetchConnectionStats();

    // Connecter au WebSocket avec un token temporaire (à remplacer par le vrai token)
    const userToken = localStorage.getItem('userToken') || 'temp_token';
    const userType = localStorage.getItem('userType') || 'manager';
    
    communicationService.connect(userToken, userType)
      .then(() => {
        setIsConnected(true);
        
        // S'abonner aux canaux pertinents
        communicationService.subscribe('coord/status', handleStatusUpdate);
        communicationService.subscribe('manager/status', handleManagerUpdate);
        communicationService.subscribe('volunteer/available', handleVolunteerUpdate);
        communicationService.subscribe('tasks/new', handleNewTask);
        communicationService.subscribe('tasks/result/#', handleTaskResult);
      })
      .catch(error => {
        console.error('Failed to connect:', error);
      });

    // Envoyer un heartbeat toutes les 30 secondes
    const heartbeatInterval = setInterval(() => {
      if (isConnected) {
        communicationService.sendHeartbeat();
      }
    }, 30000);

    // Rafraîchir les statistiques toutes les 10 secondes
    const statsInterval = setInterval(fetchConnectionStats, 10000);

    return () => {
      // Nettoyage
      clearInterval(heartbeatInterval);
      clearInterval(statsInterval);
      communicationService.disconnect();
    };
  }, []);

  const fetchConnectionStats = () => {
    communicationService.getConnectionStats()
      .then(response => {
        const data = response.data;
        setConnections({
          total: data.total_participants || 0,
          connected: data.connected || 0,
          managers: data.managers || 0,
          volunteers: data.volunteers || 0
        });
      })
      .catch(error => {
        console.error('Error fetching connection stats:', error);
      });
  };

  // Gestionnaires d'événements pour les messages Redis
  const handleStatusUpdate = (data) => {
    // Mise à jour du statut global
    console.log('System status update:', data);
    fetchConnectionStats();
  };

  const handleManagerUpdate = (data) => {
    console.log('Manager status update:', data);
    addMessage({
      type: 'manager',
      title: 'Manager Status',
      content: `Manager ${data.username} is now ${data.status}`,
      timestamp: new Date().toISOString()
    });
    fetchConnectionStats();
  };

  const handleVolunteerUpdate = (data) => {
    console.log('Volunteer update:', data);
    addMessage({
      type: 'volunteer',
      title: 'Volunteer Status',
      content: `Volunteer ${data.id} is now ${data.status}`,
      timestamp: new Date().toISOString()
    });
    fetchConnectionStats();
  };

  const handleNewTask = (data) => {
    console.log('New task:', data);
    addMessage({
      type: 'task',
      title: 'New Task',
      content: `Task ${data.task_id}: ${data.name}`,
      timestamp: new Date().toISOString()
    });
  };

  const handleTaskResult = (data, channel) => {
    console.log('Task result:', data, 'on channel:', channel);
    addMessage({
      type: 'result',
      title: 'Task Result',
      content: `Task ${data.task_id} completed with status: ${data.status}`,
      timestamp: data.completed_at || new Date().toISOString()
    });
  };

  const addMessage = (message) => {
    setRecentMessages(prev => {
      const newMessages = [message, ...prev].slice(0, 10); // Garder seulement les 10 derniers messages
      return newMessages;
    });
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'manager':
        return <PersonIcon />;
      case 'volunteer':
        return <ComputerIcon />;
      case 'task':
        return <DnsIcon />;
      case 'result':
        return <DnsIcon color="success" />;
      default:
        return <CircleIcon />;
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (e) {
      return 'Invalid date';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Connection Monitor
        <Chip 
          label={isConnected ? "Connected" : "Disconnected"} 
          color={isConnected ? "success" : "error"} 
          size="small" 
          sx={{ ml: 2 }} 
        />
      </Typography>
      
      <Grid container spacing={3}>
        {/* Statistiques */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Connection Statistics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Total Participants</Typography>
                    <Typography variant="h4">{connections.total}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Connected: {connections.connected}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Managers</Typography>
                    <Typography variant="h4">{connections.managers}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Volunteers</Typography>
                    <Typography variant="h4">{connections.volunteers}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Active Tasks</Typography>
                    <Typography variant="h4">-</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        {/* Messages récents */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>Recent Messages</Typography>
            <List>
              {recentMessages.length > 0 ? (
                recentMessages.map((message, index) => (
                  <React.Fragment key={index}>
                    <ListItem alignItems="flex-start">
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: message.type === 'result' ? 'success.main' : 'primary.main' }}>
                          {getMessageIcon(message.type)}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="subtitle1">
                            {message.title}
                            <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                              {formatTimestamp(message.timestamp)}
                            </Typography>
                          </Typography>
                        }
                        secondary={message.content}
                      />
                    </ListItem>
                    {index < recentMessages.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                  No recent messages
                </Typography>
              )}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ConnectionMonitor;
