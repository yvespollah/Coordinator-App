/**
 * Service de communication en temps réel avec Redis
 * Version minimale pour éviter les erreurs
 */

import axios from 'axios';

const API_URL = 'http://127.0.0.1:8090';

// Classe simplifiée pour gérer la communication
class CommunicationService {
  constructor() {
    this.isConnected = false;
  }

  // Méthode factice pour la connexion
  connect() {
    return Promise.resolve(false);
  }

  // Méthode factice pour l'abonnement
  subscribe() {
    return () => {};
  }

  // Méthode factice pour la publication
  publish() {
    return false;
  }

  // Méthode factice pour le heartbeat
  sendHeartbeat() {
    // Ne fait rien
  }

  // Méthode factice pour la déconnexion
  disconnect() {
    // Ne fait rien
  }

  // Méthode factice pour les statistiques
  getConnectionStats() {
    return Promise.resolve({
      data: {
        total_participants: 0,
        connected: 0,
        managers: {
          total: 0,
          connected: 0
        },
        volunteers: {
          total: 0,
          connected: 0
        },
        recent_messages: []
      }
    });
  }
}

// Singleton
const communicationService = new CommunicationService();
export default communicationService;