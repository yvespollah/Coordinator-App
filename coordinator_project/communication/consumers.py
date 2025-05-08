"""
Consommateurs Redis pour le traitement des messages.
Ces consommateurs écoutent les canaux Redis et réagissent aux messages entrants.
"""

import json
import logging
import threading
import time
from datetime import datetime
import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

from manager.models import Manager
from volunteer.models import Volunteer
from manager.auth import generate_manager_token
from .broker import MessageBroker
from .messages import (
    ManagerRegistrationResponseMessage,
    ManagerLoginResponseMessage,
    VolunteerRegistrationResponseMessage,
    VolunteerLoginResponseMessage
)

logger = logging.getLogger(__name__)

class RedisConsumer:
    """
    Classe de base pour les consommateurs Redis.
    """
    
    def __init__(self, broker=None):
        """
        Initialise le consommateur Redis.
        
        Args:
            broker: Instance du MessageBroker (si None, en crée une nouvelle)
        """
        self.broker = broker or MessageBroker(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        self.running = False
        self.thread = None
    
    def start(self):
        """Démarre le consommateur dans un thread séparé."""
        if self.running:
            logger.warning("Le consommateur est déjà en cours d'exécution")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Consommateur {self.__class__.__name__} démarré")
    
    def stop(self):
        """Arrête le consommateur."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        logger.info(f"Consommateur {self.__class__.__name__} arrêté")
    
    def _run(self):
        """
        Méthode principale du thread.
        À implémenter dans les classes dérivées.
        """
        raise NotImplementedError("Les classes dérivées doivent implémenter _run()")


class ManagerRegistrationConsumer(RedisConsumer):
    """
    Consommateur pour l'enregistrement des managers.
    Écoute le canal auth/register et traite les demandes d'enregistrement.
    """
    
    def __init__(self, broker=None):
        super().__init__(broker)
        self.channel = 'auth/register'
    
    def _run(self):
        """Écoute le canal d'enregistrement et traite les messages."""
        # S'abonner au canal
        pubsub = self.broker.redis_client.pubsub()
        pubsub.subscribe(self.channel)
        
        logger.info(f"Écoute du canal {self.channel}")
        
        try:
            while self.running:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        # Décoder le message
                        data = json.loads(message['data'])
                        logger.info(f"Message reçu sur {self.channel}: {data}")
                        
                        # Traiter le message d'enregistrement
                        self._handle_registration(data)
                    except json.JSONDecodeError:
                        logger.error(f"Message non JSON sur {self.channel}: {message['data']}")
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du message: {e}")
                
                # Petite pause pour éviter de surcharger le CPU
                time.sleep(0.1)
        
        finally:
            # Se désabonner du canal
            pubsub.unsubscribe(self.channel)
            logger.info(f"Désabonnement du canal {self.channel}")
    
    def _handle_registration(self, data):
        """
        Traite une demande d'enregistrement de manager.
        
        Args:
            data: Données du message
        """
        request_id = data.get('request_id')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not request_id or not username or not email or not password:
            logger.error(f"Données d'enregistrement incomplètes: {data}")
            
            # Envoyer une réponse d'erreur
            response = ManagerRegistrationResponseMessage(
                request_id=request_id or '',
                status='error',
                message="Données d'enregistrement incomplètes"
            )
            
            self.broker.publish('auth/register_response', response.to_dict())
            return
        
        try:
            # Vérifier si le manager existe déjà
            existing_manager = Manager.objects(username=username).first()
            if existing_manager:
                logger.warning(f"Le manager {username} existe déjà")
                
                # Envoyer une réponse d'erreur
                response = ManagerRegistrationResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Ce nom d\'utilisateur est déjà utilisé'
                )
                
                self.broker.publish('auth/register_response', response.to_dict())
                return
            
            existing_email = Manager.objects(email=email).first()
            if existing_email:
                logger.warning(f"L'email {email} est déjà utilisé")
                
                # Envoyer une réponse d'erreur
                response = ManagerRegistrationResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Cet email est déjà utilisé'
                )
                
                self.broker.publish('auth/register_response', response.to_dict())
                return
            
            # Créer le manager
            from django.contrib.auth.hashers import make_password
            
            # Hacher le mot de passe avant de le stocker
            hashed_password = make_password(password)
            
            manager = Manager(
                username=username,
                email=email,
                password=hashed_password,  # Stockage sécurisé du mot de passe
                status='active'  # Activer directement le compte pour simplifier
            )
            manager.save()
            
            logger.info(f"Manager {username} enregistré avec succès (ID: {manager.id})")
            
            # Envoyer une réponse de succès
            response = ManagerRegistrationResponseMessage(
                request_id=request_id,
                status='success',
                message='Manager enregistré avec succès',
                manager_id=str(manager.id),
                username=manager.username,
                email=manager.email
            )
            
            self.broker.publish('auth/register_response', response.to_dict())
            
            # Publier un message sur le canal des managers
            self.broker.publish('manager/status', {
                'id': str(manager.id),
                'username': manager.username,
                'email': manager.email,
                'status': 'registered',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du manager: {e}")
            
            # Envoyer une réponse d'erreur
            response = ManagerRegistrationResponseMessage(
                request_id=request_id,
                status='error',
                message=str(e)
            )
            
            self.broker.publish('auth/register_response', response.to_dict())


class ManagerLoginConsumer(RedisConsumer):
    """
    Consommateur pour l'authentification des managers.
    Écoute le canal auth/login et traite les demandes d'authentification.
    """
    
    def __init__(self, broker=None):
        super().__init__(broker)
        self.channel = 'auth/login'
    
    def _run(self):
        """Écoute le canal d'authentification et traite les messages."""
        # S'abonner au canal
        pubsub = self.broker.redis_client.pubsub()
        pubsub.subscribe(self.channel)
        
        logger.info(f"Écoute du canal {self.channel}")
        
        try:
            while self.running:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        # Décoder le message
                        data = json.loads(message['data'])
                        logger.info(f"Message reçu sur {self.channel}: {data}")
                        
                        # Traiter le message d'authentification
                        self._handle_login(data)
                    except json.JSONDecodeError:
                        logger.error(f"Message non JSON sur {self.channel}: {message['data']}")
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du message: {e}")
                
                # Petite pause pour éviter de surcharger le CPU
                time.sleep(0.01)
        
        finally:
            # Se désabonner du canal
            pubsub.unsubscribe(self.channel)
            logger.info(f"Désabonnement du canal {self.channel}")
    
    def _handle_login(self, data):
        """
        Traite une demande d'authentification de manager.
        
        Args:
            data: Données du message
        """
        request_id = data.get('request_id')
        username = data.get('username')
        password = data.get('password')
        
        if not request_id or not username or not password:
            logger.error(f"Données d'authentification incomplètes: {data}")
            
            # Envoyer une réponse d'erreur
            response = ManagerLoginResponseMessage(
                request_id=request_id or '',
                status='error',
                message='Données d\'authentification incomplètes'
            )
            
            self.broker.publish('auth/login_response', response.to_dict())
            return
        
        try:
            # Rechercher le manager
            manager = Manager.objects(username=username).first()
            if not manager:
                logger.warning(f"Manager {username} introuvable")
                
                # Envoyer une réponse d'erreur
                response = ManagerLoginResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Identifiants invalides'
                )
                
                self.broker.publish('auth/login_response', response.to_dict())
                return
            
            # Vérifier le mot de passe
            from django.contrib.auth.hashers import check_password
            if not check_password(password, manager.password):
                logger.warning(f"Mot de passe incorrect pour {username}")
                
                # Envoyer une réponse d'erreur
                response = ManagerLoginResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Identifiants invalides'
                )
                
                self.broker.publish('auth/login_response', response.to_dict())
                return
            
            # Vérifier que le compte est actif
            if manager.status != 'active':
                logger.warning(f"Le compte {username} n'est pas actif")
                
                # Envoyer une réponse d'erreur
                response = ManagerLoginResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Ce compte n\'est pas actif'
                )
                
                self.broker.publish('auth/login_response', response.to_dict())
                return
            
            # Générer un token JWT et un refresh token
            token = generate_manager_token(str(manager.id))
            refresh_token = generate_manager_token(str(manager.id), expiration_hours=168)  # 7 jours
            
            # Mettre à jour la date de dernière connexion
            manager.last_login = datetime.utcnow()
            manager.save()
            
            logger.info(f"Manager {username} authentifié avec succès")
            
            # Envoyer une réponse de succès
            response = ManagerLoginResponseMessage(
                request_id=request_id,
                status='success',
                message='Authentification réussie',
                token=token,
                refresh_token=refresh_token,
                manager_id=str(manager.id),
                username=manager.username,
                email=manager.email
            )
            
            self.broker.publish('auth/login_response', response.to_dict())
            
            # Publier un message sur le canal des managers
            self.broker.publish('manager/status', {
                'id': str(manager.id),
                'username': manager.username,
                'status': 'online',
                'timestamp': datetime.utcnow().isoformat(),
                'token': token  # Le token sera retiré par le proxy
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification du manager: {e}")
            
            # Envoyer une réponse d'erreur
            response = ManagerLoginResponseMessage(
                request_id=request_id,
                status='error',
                message=str(e)
            )
            
            self.broker.publish('auth/login_response', response.to_dict())


class VolunteerRegistrationConsumer(RedisConsumer):
    """
    Consommateur pour l'enregistrement des volunteers.
    Écoute le canal volunteer/register et traite les demandes d'enregistrement.
    """
    
    def __init__(self, broker=None):
        super().__init__(broker)
        self.channel = 'volunteer/register'
    
    def _run(self):
        """Écoute le canal d'enregistrement et traite les messages."""
        # S'abonner au canal
        pubsub = self.broker.redis_client.pubsub()
        pubsub.subscribe(self.channel)
        
        logger.info(f"Écoute du canal {self.channel}")
        
        try:
            while self.running:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        # Décoder le message
                        data = json.loads(message['data'])
                        logger.info(f"Message reçu sur {self.channel}: {data}")
                        
                        # Traiter le message d'enregistrement
                        self._handle_registration(data)
                    except json.JSONDecodeError:
                        logger.error(f"Message non JSON sur {self.channel}: {message['data']}")
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du message: {e}")
                
                # Petite pause pour éviter de surcharger le CPU
                time.sleep(0.01)
        
        finally:
            # Se désabonner du canal
            pubsub.unsubscribe(self.channel)
            logger.info(f"Désabonnement du canal {self.channel}")
    
    def _handle_registration(self, data):
        """
        Traite une demande d'enregistrement de volunteer.
        
        Args:
            data: Données du message
        """
        request_id = data.get('request_id')
        name = data.get('name')
        
        if not request_id or not name:
            logger.error(f"Données d'enregistrement incomplètes: {data}")
            
            # Envoyer une réponse d'erreur
            response = VolunteerRegistrationResponseMessage(
                request_id=request_id or '',
                status='error',
                message='Données d\'enregistrement incomplètes'
            )
            
            self.broker.publish('volunteer/register_response', response.to_dict())
            return
        
        try:
            # Créer le volunteer
            volunteer = Volunteer(
                name=name,
                cpu_model=data.get('cpu_model', 'Unknown'),
                cpu_cores=data.get('cpu_cores', 1),
                total_ram=data.get('total_ram', 1024),
                available_storage=data.get('available_storage', 10),
                operating_system=data.get('operating_system', 'Unknown'),
                gpu_available=data.get('gpu_available', False),
                gpu_model=data.get('gpu_model'),
                gpu_memory=data.get('gpu_memory'),
                ip_address=data.get('ip_address', '0.0.0.0'),
                communication_port=data.get('communication_port', 8000),
                current_status='available'
            )
            volunteer.save()
            
            logger.info(f"Volunteer {name} enregistré avec succès (ID: {volunteer.id})")
            
            # Envoyer une réponse de succès
            response = VolunteerRegistrationResponseMessage(
                request_id=request_id,
                status='success',
                message='Volunteer enregistré avec succès',
                volunteer_id=str(volunteer.id),
                name=volunteer.name
            )
            
            self.broker.publish('volunteer/register_response', response.to_dict())
            
            # Publier un message sur le canal des volunteers
            self.broker.publish('volunteer/available', {
                'id': str(volunteer.id),
                'name': volunteer.name,
                'status': 'registered',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du volunteer: {e}")
            
            # Envoyer une réponse d'erreur
            response = VolunteerRegistrationResponseMessage(
                request_id=request_id,
                status='error',
                message=str(e)
            )
            
            self.broker.publish('volunteer/register_response', response.to_dict())


# Classe principale pour gérer tous les consommateurs
class CommunicationService:
    """
    Service de communication qui gère tous les consommateurs Redis.
    """
    
    def __init__(self):
        """Initialise le service de communication."""
        # Créer une instance du broker
        self.broker = MessageBroker(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        
        # Créer les consommateurs
        self.consumers = [
            ManagerRegistrationConsumer(self.broker),
            ManagerLoginConsumer(self.broker),
            VolunteerRegistrationConsumer(self.broker)
        ]
        
        self.running = False
    
    def start(self):
        """Démarre tous les consommateurs."""
        if self.running:
            logger.warning("Le service de communication est déjà en cours d'exécution")
            return
        
        self.running = True
        
        # Démarrer tous les consommateurs
        for consumer in self.consumers:
            consumer.start()
        
        logger.info("Service de communication démarré")
    
    def stop(self):
        """Arrête tous les consommateurs."""
        if not self.running:
            logger.warning("Le service de communication n'est pas en cours d'exécution")
            return
        
        self.running = False
        
        # Arrêter tous les consommateurs
        for consumer in self.consumers:
            consumer.stop()
        
        logger.info("Service de communication arrêté")


# Instance globale du service de communication
communication_service = CommunicationService()
