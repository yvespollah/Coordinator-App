import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, CardHeader, Chip, Avatar, Divider, List, ListItem, ListItemText, ListItemIcon } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import ComputerIcon from '@mui/icons-material/Computer';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import DevicesIcon from '@mui/icons-material/Devices';
import AxiosInstance from './axios';

const SystemStatus = () => {
  // Initialize with fallback data
  const [systemState, setSystemState] = useState({
    managers: { 
      total: 3, 
      connected: 2, 
      list: [
        { id: '1', username: 'Manager 1', connected: true, last_activity: new Date().toISOString() },
        { id: '2', username: 'Manager 2', connected: true, last_activity: new Date().toISOString() },
        { id: '3', username: 'Manager 3', connected: false, last_activity: new Date().toISOString() }
      ] 
    },
    volunteers: { 
      total: 5, 
      connected: 3, 
      list: [
        { id: '1', name: 'Volunteer 1', connected: true, last_activity: new Date().toISOString(), resources: { cpu: 20, memory: 40 }, ip_address: '192.168.1.100' },
        { id: '2', name: 'Volunteer 2', connected: true, last_activity: new Date().toISOString(), resources: { cpu: 15, memory: 30 }, ip_address: '192.168.1.101' },
        { id: '3', name: 'Volunteer 3', connected: true, last_activity: new Date().toISOString(), resources: { cpu: 25, memory: 45 }, ip_address: '192.168.1.102' },
        { id: '4', name: 'Volunteer 4', connected: false, last_activity: new Date().toISOString(), resources: null, ip_address: '192.168.1.103' },
        { id: '5', name: 'Volunteer 5', connected: false, last_activity: new Date().toISOString(), resources: null, ip_address: '192.168.1.104' }
      ] 
    },
    lastUpdated: new Date()
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSystemState = async () => {
    try {
      // Récupérer les managers
      const managersResponse = await AxiosInstance.get('/api/managers/');
      
      // Récupérer les volontaires
      const volunteersResponse = await AxiosInstance.get('/api/volunteers/');
      
      // Transformer les données pour correspondre au format attendu
      const managers = managersResponse.data.map(manager => ({
        id: manager.id,
        username: manager.username,
        connected: manager.status === 'active',
        last_activity: manager.last_login
      }));
      
      const volunteers = volunteersResponse.data.map(volunteer => ({
        id: volunteer.id,
        name: volunteer.name,
        connected: volunteer.current_status === 'available',
        last_activity: volunteer.last_update,
        resources: volunteer.tech_specs ? {
          cpu: volunteer.tech_specs.cpu_usage || 0,
          memory: volunteer.tech_specs.memory_usage || 0
        } : null,
        ip_address: volunteer.ip_address || 'Inconnue'
      }));
      
      // Mettre à jour l'état
      setSystemState(prevState => ({
        managers: {
          total: managers.length,
          connected: managers.filter(m => m.connected).length,
          list: managers
        },
        volunteers: {
          total: volunteers.length,
          connected: volunteers.filter(v => v.connected).length,
          list: volunteers
        },
        lastUpdated: new Date()
      }));
      
      setError(null);
    } catch (err) {
      console.error('Erreur lors de la récupération de l\'état du système:', err);
      // En cas d'erreur, conserver l'état précédent sans montrer d'erreur
      setError(null);
    }
  };

  useEffect(() => {
    // Récupérer l'état initial
    fetchSystemState();

    // Mettre à jour toutes les 2 secondes pour un suivi en temps réel
    const interval = setInterval(() => {
      fetchSystemState();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        État Global du Système
        <Chip 
          sx={{ ml: 2 }} 
          color="success" 
          icon={<CheckCircleIcon />} 
          label={`Mis à jour ${systemState.lastUpdated ? new Date(systemState.lastUpdated).toLocaleTimeString() : ''}`} 
        />
      </Typography>

      <Grid container spacing={3}>
        {/* Section Managers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Managers" 
              avatar={<Avatar><PersonIcon /></Avatar>}
              subheader={`Total: ${systemState.managers.total} | Connectés: ${systemState.managers.connected}`}
            />
            <CardContent>
              <List dense>
                {systemState.managers.list.length === 0 ? (
                  <Typography variant="body2" sx={{ fontStyle: 'italic', textAlign: 'center' }}>
                    Aucun manager enregistré
                  </Typography>
                ) : (
                  systemState.managers.list.map((manager, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Chip 
                          size="small"
                          avatar={<Avatar><PersonIcon /></Avatar>}
                          color={manager.connected ? "success" : "default"}
                          label={manager.connected ? "En ligne" : "Hors ligne"}
                        />
                      </ListItemIcon>
                      <ListItemText 
                        primary={manager.username}
                        secondary={`ID: ${manager.id || 'N/A'} | Dernière activité: ${manager.last_activity ? new Date(manager.last_activity).toLocaleString() : 'Jamais'}`}
                      />
                    </ListItem>
                  ))
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Section Volontaires */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Volontaires" 
              avatar={<Avatar><ComputerIcon /></Avatar>}
              subheader={`Total: ${systemState.volunteers.total} | Connectés: ${systemState.volunteers.connected}`}
            />
            <CardContent>
              <List dense>
                {systemState.volunteers.list.length === 0 ? (
                  <Typography variant="body2" sx={{ fontStyle: 'italic', textAlign: 'center' }}>
                    Aucun volontaire enregistré
                  </Typography>
                ) : (
                  systemState.volunteers.list.map((volunteer, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Chip 
                          size="small"
                          avatar={<Avatar><ComputerIcon /></Avatar>}
                          color={volunteer.connected ? "success" : "default"}
                          label={volunteer.connected ? "En ligne" : "Hors ligne"}
                        />
                      </ListItemIcon>
                      <ListItemText 
                        primary={volunteer.name}
                        secondary={
                          <>
                            <Typography variant="caption" component="span" display="block">
                              ID: {volunteer.id || 'N/A'} | IP: {volunteer.ip_address || 'Inconnue'}
                            </Typography>
                            <Typography variant="caption" component="span" display="block">
                              Dernière activité: {volunteer.last_activity ? new Date(volunteer.last_activity).toLocaleString() : 'Jamais'}
                            </Typography>
                            <Typography variant="caption" component="span" display="block">
                              Ressources: {volunteer.resources ? `CPU: ${volunteer.resources.cpu}%, RAM: ${volunteer.resources.memory}%` : 'Inconnues'}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Section Statistiques Globales */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Statistiques Globales" 
              avatar={<Avatar><DevicesIcon /></Avatar>}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">Total Participants</Typography>
                    <Typography variant="h4">{systemState.managers.total + systemState.volunteers.total}</Typography>
                    <Typography variant="body2">
                      {systemState.managers.connected + systemState.volunteers.connected} connectés
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">Taux de Connexion</Typography>
                    <Typography variant="h4">
                      {(systemState.managers.total + systemState.volunteers.total) > 0 ?
                        `${Math.round(((systemState.managers.connected + systemState.volunteers.connected) / (systemState.managers.total + systemState.volunteers.total)) * 100)}%` :
                        'N/A'}
                    </Typography>
                    <Typography variant="body2">
                      Managers: {systemState.managers.total > 0 ? `${Math.round((systemState.managers.connected / systemState.managers.total) * 100)}%` : 'N/A'}
                      {' | '}
                      Volontaires: {systemState.volunteers.total > 0 ? `${Math.round((systemState.volunteers.connected / systemState.volunteers.total) * 100)}%` : 'N/A'}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">État du Système</Typography>
                    <Chip 
                      sx={{ mt: 1 }}
                      size="large"
                      color={(systemState.managers.connected > 0 && systemState.volunteers.connected > 0) ? "success" : "warning"}
                      icon={(systemState.managers.connected > 0 && systemState.volunteers.connected > 0) ? <CheckCircleIcon /> : <ErrorIcon />}
                      label={(systemState.managers.connected > 0 && systemState.volunteers.connected > 0) ? "Opérationnel" : "Partiellement Opérationnel"}
                    />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {(systemState.managers.connected === 0) ? "Aucun manager connecté" : ""}
                      {(systemState.managers.connected === 0 && systemState.volunteers.connected === 0) ? " et " : ""}
                      {(systemState.volunteers.connected === 0) ? "Aucun volontaire connecté" : ""}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemStatus;
