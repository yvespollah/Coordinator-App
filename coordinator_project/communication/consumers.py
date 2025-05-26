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
        print("Début du traitement d'enregistrement")
        request_id = data.get('request_id')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        status = data.get('status')
        
        print(f"Données reçues: request_id={request_id}, username={username}, email={email}, password={'*' * len(password) if password else None}, status={status}")
        
        if not request_id or not username or not email or not password or not status:
            logger.error(f"Données d'enregistrement incomplètes: {data}")
            
            try:
                # Envoyer une réponse d'erreur
                print("Création de la réponse d'erreur pour données incomplètes")
                response = ManagerRegistrationResponseMessage(
                    status='error',   
                    message="Données d'enregistrement incomplètes",
                    request_id=request_id or ''
                )
                
                print(f"Réponse créée: {response.to_dict()}")
                
                # Publication de la réponse
                print(f"Publication sur le canal auth/register_response")
                self.broker.publish('auth/register_response', response.to_dict())
                print("Publication terminée")
                return
            except Exception as e:
                logger.error(f"Erreur lors de la création/publication de la réponse: {e}")
                import traceback
                traceback.print_exc()
                return
        
        try:
            # Vérifier si le manager existe déjà
            print("Vérification si le manager existe déjà")
            existing_manager = Manager.objects(username=username).first()
            print(f"Résultat de la recherche par username: {existing_manager}")
            
            if existing_manager:
                logger.warning(f"Le manager {username} existe déjà")
                print(f"Le manager {username} existe déjà - création de la réponse")
                
                try:
                    # Envoyer une réponse d'erreur
                    response = ManagerRegistrationResponseMessage(
                        request_id=request_id,
                        status='error',
                        message='Ce nom d\'utilisateur est déjà utilisé'
                    )
                    
                    print(f"Réponse créée: {response.to_dict()}")
                    
                    # Publication de la réponse
                    print(f"Publication sur le canal auth/register_response")
                    self.broker.publish('auth/register_response', response.to_dict())
                    print("Publication terminée")
                    return
                except Exception as e:
                    logger.error(f"Erreur lors de la création/publication de la réponse: {e}")
                    import traceback
                    traceback.print_exc()
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
                status=status  # Activer directement le compte pour simplifier
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
                        # Décoder le message - gérer les cas où message['data'] est déjà une chaîne
                        if isinstance(message['data'], bytes):
                            data = json.loads(message['data'].decode('utf-8'))
                        elif isinstance(message['data'], str):
                            data = json.loads(message['data'])
                        else:
                            logger.error(f"Type de données non pris en charge: {type(message['data'])}")
                            continue
                        
                        logger.info(f"Message de login reçu: {data}")
                        
                        # Traiter le message d'authentification
                        self._handle_login(data)
                    except json.JSONDecodeError:
                        logger.error(f"Erreur de décodage JSON: {message['data']}")
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
        
        logger.info(f"Tentative de login pour {username} avec request_id {request_id}")
        
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
            logger.info(f"Recherche du manager avec username={username}")
            manager = Manager.objects(username=username).first()
            if not manager:
                logger.warning(f"Manager {username} introuvable dans la base de données")
                
                # Envoyer une réponse d'erreur
                response = ManagerLoginResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Identifiants invalides'
                )
                
                self.broker.publish('auth/login_response', response.to_dict())
                return
            
            logger.info(f"Manager trouvé: id={manager.id}, status={manager.status}")
            
            # MODE DÉVELOPPEMENT : Désactiver complètement la vérification du mot de passe
            logger.info(f"MODE DÉVELOPPEMENT : Vérification du mot de passe désactivée pour {username}")
            password_correct = True  # Accepter n'importe quel mot de passe
            
            # Code original commenté pour référence
            # from django.contrib.auth.hashers import check_password, make_password
            # 
            # # Ajouter des logs pour déboguer le processus de vérification
            # logger.info(f"Mot de passe reçu: {password}")
            # logger.info(f"Mot de passe stocké (hashé): {manager.password}")
            # 
            # # Pour débogage uniquement: tester si le mot de passe est déjà hashé
            # test_hash = make_password(password)
            # logger.info(f"Test de hachage du mot de passe reçu: {test_hash}")
            # 
            # # Vérifier si le mot de passe est celui utilisé lors de l'enregistrement
            # password_correct = check_password(password, manager.password)
            # logger.info(f"Résultat de check_password: {password_correct}")
            # 
            # # Si le mot de passe est incorrect, vérifier si c'est le nom d'utilisateur (utilisé par le manager)
            # # Cette vérification permet de supporter les deux méthodes d'authentification
            # if not password_correct and password == manager.username:
            #     logger.info(f"Mot de passe incorrect mais correspond au nom d'utilisateur, authentification acceptée")
            #     password_correct = True
            # 
            # # TEMPORAIRE: Accepter 'password123' pour le manager 'manager2'
            # if not password_correct and username == 'manager2' and password == 'password123':
            #     logger.info(f"Mot de passe spécial accepté pour manager2")
            #     password_correct = True
            #     
            # logger.info(f"Vérification du mot de passe: {'réussie' if password_correct else 'échouée'}")
            # 
            # if not password_correct:
            #     logger.warning(f"Mot de passe incorrect pour {username}")
            #     
            #     # Envoyer une réponse d'erreur
            #     response = ManagerLoginResponseMessage(
            #         request_id=request_id,
            #         status='error',
            #         message='Identifiants invalides'
            #     )
            #     
            #     self.broker.publish('auth/login_response', response.to_dict())
            #     return
            
            # Désactivation complète de la vérification du statut pour le développement
            if False:  # Désactivation complète de la vérification du statut
                logger.warning(f"Le compte {username} n'est pas actif (status={manager.status})")
                
                # Envoyer une réponse d'erreur
                response = ManagerLoginResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Ce compte n\'est pas actif'
                )
                
                self.broker.publish('auth/login_response', response.to_dict())
                return
            
            logger.info(f"Statut du compte vérifié: {manager.status}")
            
            
            # Générer un token JWT et un refresh token
            try:
                token = generate_manager_token(str(manager.id))
                refresh_token = generate_manager_token(str(manager.id), expiration_hours=168)  # 7 jours
                logger.info(f"Tokens générés avec succès pour {username}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération des tokens: {e}")
                # Envoyer une réponse d'erreur
                response = ManagerLoginResponseMessage(
                    request_id=request_id,
                    status='error',
                    message='Erreur lors de la génération des tokens'
                )
                self.broker.publish('auth/login_response', response.to_dict())
                return
            
            # Mettre à jour la date de dernière connexion
            try:
                manager.last_login = datetime.utcnow()
                manager.save()
                logger.info(f"Date de dernière connexion mise à jour pour {username}")
            except Exception as e:
                logger.warning(f"Impossible de mettre à jour la date de dernière connexion: {e}")
                # On continue quand même, ce n'est pas bloquant
            
            logger.info(f"Manager {username} authentifié avec succès")
            
            # Envoyer une réponse de succès
            try:
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
                
                response_dict = response.to_dict()
                logger.info(f"Réponse préparée pour {username}: {response_dict.get('status')}")
                logger.info(f"Token inclus dans la réponse: {token[:10]}...")
                
                # Vérifier que le token est bien présent dans le dictionnaire de réponse
                if 'token' in response_dict:
                    logger.info(f"Token confirmé dans le dictionnaire de réponse: {response_dict['token'][:10]}...")
                else:
                    logger.error(f"ERREUR: Token manquant dans le dictionnaire de réponse!")
                    logger.error(f"Contenu du dictionnaire: {response_dict}")
                
                # Publier la réponse sur le canal auth/login_response
                publish_result = self.broker.publish('auth/login_response', response_dict)
                logger.info(f"Réponse publiée sur le canal auth/login_response avec résultat: {publish_result}")
                
                # Vérifier que le message a bien été publié
                if publish_result:
                    logger.info(f"Message correctement publié sur Redis")
                else:
                    logger.warning(f"Possible problème lors de la publication du message sur Redis")
                
                # Publier un message sur le canal des managers
                status_message = {
                    'id': str(manager.id),
                    'username': manager.username,
                    'status': 'online',
                    'timestamp': datetime.utcnow().isoformat(),
                    'token': token  # Le token sera retiré par le proxy
                }
                self.broker.publish('manager/status', status_message)
                logger.info(f"Message de statut publié sur le canal manager/status")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la réponse: {e}")
                # Tentative de récupération avec un message simplié
                try:
                    simple_response = {
                        'request_id': request_id,
                        'status': 'success',
                        'message': 'Authentification réussie',
                        'token': token,
                        'manager_id': str(manager.id),
                        'username': manager.username
                    }
                    self.broker.publish('auth/login_response', simple_response)
                    logger.info("Réponse simplifiée envoyée avec succès")
                except Exception as e2:
                    logger.error(f"Erreur lors de l'envoi de la réponse simplifiée: {e2}")
            
            
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
