"""
Proxy Redis pour le contrôle des messages et souscriptions.
Intercepte toutes les commandes Redis pour appliquer des règles d'autorisation.
"""

import socket
import threading
import logging
import json
import re
import traceback
from datetime import datetime
import jwt
from django.conf import settings
from .models import Channel
from .broker import MessageBroker
import redis

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RedisProxy')

class RedisCommand:
    """Classe pour analyser et représenter une commande Redis"""
    
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.command_type = None
        self.args = []
        self.parse()
    
    def parse(self):
        """Parse le format RESP (Redis Serialization Protocol)"""
        try:
            # Format simplifié pour l'exemple
            # Un parseur RESP complet serait plus complexe
            text = self.raw_data.decode('utf-8')
            
            # Afficher les données brutes pour le débogage
            logger.debug(f"Données brutes RESP: {text}")
            
            # Recherche des commandes pub/sub
            if '*' in text:  # Format Array RESP
                parts = text.split('\r\n')
                cmd_parts = []
                
                i = 1  # Sauter le premier élément (*n)
                while i < len(parts):
                    if parts[i].startswith('$'):
                        # Extraire la longueur
                        length = int(parts[i][1:])
                        i += 1  # Passer à la valeur
                        if i < len(parts):
                            cmd_parts.append(parts[i])
                    i += 1
                
                if cmd_parts:
                    self.command_type = cmd_parts[0].upper()
                    self.args = cmd_parts[1:]
                    logger.debug(f"Commande parsée: type={self.command_type}, args={self.args}")
        except Exception as e:
            logger.error(f"Erreur lors du parsing de la commande: {e}")
            traceback.print_exc()
    
    def is_pubsub_command(self):
        """Vérifie si la commande est liée à pub/sub"""
        result = self.command_type in ['PUBLISH', 'SUBSCRIBE', 'PSUBSCRIBE', 'UNSUBSCRIBE', 'PUNSUBSCRIBE']
        logger.debug(f"is_pubsub_command: {result} pour {self.command_type}")
        return result
    
    def get_channel(self):
        """Récupère le canal pour les commandes pub/sub"""
        if self.command_type == 'PUBLISH' and len(self.args) >= 1:
            return self.args[0]
        elif self.command_type in ['SUBSCRIBE', 'UNSUBSCRIBE'] and self.args:
            return self.args
        return None
    
    def get_message(self):
        """Récupère le message pour la commande PUBLISH"""
        if self.command_type == 'PUBLISH' and len(self.args) >= 2:
            return self.args[1]
        return None
    
    def __str__(self):
        return f"RedisCommand(type={self.command_type}, args={self.args})"


class RedisProxy:
    """
    Proxy pour intercepter et contrôler les commandes Redis.
    Gère l'authentification JWT et les permissions des canaux.
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, proxy_port=6380):
        """
        Initialise le proxy Redis.
        
        Args:
            redis_host: Hôte Redis (défaut: localhost)
            port: Port Redis (défaut: 6379)
            proxy_port: Port sur lequel le proxy écoute (défaut: 6380)
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.proxy_port = proxy_port
        self.server_socket = None
        self.running = False
        self.client_connections = {}  # Pour suivre les connexions client
        
        # Canaux d'enregistrement et d'authentification (toujours autorisés)
        self.open_channels = {
            'auth/register': True,
            'auth/register_response': True,
            'auth/login': True,
            'auth/login_response': True,
            'coord/heartbeat/#': True,
            'coord/emergency': True,
            "volunteer/register": True,
            "volunteer/login": True,
            "volunteer/register_response": True,
            "volunteer/login_response": True,
          
        }
        
        # Canaux réservés aux managers
        self.manager_channels = {
            'tasks/new': True,
            'tasks/assign': True,
            'tasks/status/#': True,
            'manager/status': True,
            'manager/requests': True
        }
        
        # Canaux réservés aux volunteers
        self.volunteer_channels = {
            'volunteer/available': True,
            'volunteer/resources': True,
            'tasks/result/#': True
        }
        
        # Broker pour la communication interne
        self.message_broker = MessageBroker(host=redis_host, port=redis_port)
        
        # Transformateurs de messages
        self.message_transformers = [
            self.add_metadata,
            self.filter_sensitive_data
        ]
    
    def start(self):
        """Démarre le proxy"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.proxy_port))
        self.server_socket.listen(100)
        
        self.running = True
        logger.info(f"Proxy Redis démarré sur le port {self.proxy_port}")
        
        # Démarrer un thread pour écouter les messages publiés sur Redis
        # et les transmettre aux clients abonnés
        self.pubsub_thread = threading.Thread(target=self._listen_for_published_messages)
        self.pubsub_thread.daemon = True
        self.pubsub_thread.start()
        
        try:
            while self.running:
                client_socket, client_address = self.server_socket.accept()
                client_id = f"{client_address[0]}:{client_address[1]}"
                logger.info(f"Nouvelle connexion: {client_id}")
                
                # Créer un thread pour gérer ce client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_id)
                )
                client_thread.daemon = True
                client_thread.start()
                
                # Suivre la connexion
                self.client_connections[client_id] = {
                    'socket': client_socket,
                    'thread': client_thread,
                    'authenticated': False,
                    'user_id': None,
                    'role': None,
                    'token': None,
                    'subscribed_channels': set()
                }
        except KeyboardInterrupt:
            logger.info("Arrêt du proxy...")
        finally:
            self.stop()
    
    def stop(self):
        """Arrête le proxy"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Fermer toutes les connexions client
        for client_id, client_info in self.client_connections.items():
            try:
                client_info['socket'].close()
            except:
                pass
        
        logger.info("Proxy Redis arrêté")
    
    def handle_client(self, client_socket, client_id):
        """Gère une connexion client"""
        # Connexion au serveur Redis réel
        redis_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            redis_socket.connect((self.redis_host, self.redis_port))
            
            while self.running:
                # Recevoir des données du client
                data = client_socket.recv(4096)
                if not data:
                    logger.debug(f"Pas de donnees recues")
                    break
                
                # Analyser la commande Redis
                command = RedisCommand(data)
                logger.debug(f"Commande reçue: {command}")
                
                # Traiter les commandes pub/sub
                if command.is_pubsub_command():
                    if self.handle_pubsub_command(client_id, command, client_socket, redis_socket, data):
                        continue  # Commande déjà traitée
                else:
                    logger.info(f"Le message n'est pas pub/sub: {command.command_type},{client_id}")
                
                logger.info(f"=new message{data}")
                redis_socket.send(data)
                response = redis_socket.recv(4096)
                client_socket.send(response)
        
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Erreur pour le client {client_id}: {e}")
        
        finally:
            # Nettoyage
            try:
                redis_socket.close()
            except:
                pass
            
            try:
                client_socket.close()
            except:
                pass
            
            # Supprimer la connexion
            if client_id in self.client_connections:
                del self.client_connections[client_id]
            
            logger.info(f"Client déconnecté: {client_id}")
    
    def handle_pubsub_command(self, client_id, command, client_socket, redis_socket, raw_data):
        """Gère les commandes pub/sub"""
        
        if command.command_type == 'PUBLISH':
            return self.handle_publish(client_id, command, client_socket, redis_socket, raw_data)
        elif command.command_type in ['SUBSCRIBE', 'PSUBSCRIBE']:
            return self.handle_subscribe(client_id, command, client_socket, redis_socket, raw_data)
        elif command.command_type in ['UNSUBSCRIBE', 'PUNSUBSCRIBE']:
            # Gérer les désabonnements
            channels = command.get_channel()
            if channels and client_id in self.client_connections:
                for channel in channels:
                    if channel in self.client_connections[client_id]['subscribed_channels']:
                        self.client_connections[client_id]['subscribed_channels'].remove(channel)
            
            # Transmettre la commande telle quelle
            redis_socket.send(raw_data)
            response = redis_socket.recv(4096)
            client_socket.send(response)
            return True
        
        return False
    
    def handle_publish(self, client_id, command, client_socket, redis_socket, raw_data):
        logger.info(f"piko------------------")
        """Gère la commande PUBLISH"""
        channel = command.get_channel()
        message_str = command.get_message()
        
        if not channel or not message_str:
            logger.warning(f"Canal ou message manquant dans la commande PUBLISH: {command}")
            return False
        
        logger.info(f"PUBLISH sur le canal {channel}: {message_str}")
        
        try:
            # Tenter de parser le message JSON
            message = json.loads(message_str)
            
            # Vérifier si un token est présent
            token = message.get('token')
            user_id = None
            role = None
            
            # Vérifier l'autorisation pour ce canal
            authorized = False
            
            # Canaux ouverts (pas besoin d'authentification)
            if channel in self.open_channels:
                authorized = True
            # Canaux nécessitant une authentification
            elif token:
                try:
                    # Vérifier le token JWT
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    user_id = payload.get('user_id')
                    role = payload.get('role')
                    
                    # Vérifier les permissions selon le rôle
                    if role == 'manager' and channel in self.manager_channels:
                        authorized = True
                    elif role == 'volunteer' and channel in self.volunteer_channels:
                        authorized = True
                    elif role == 'coordinator':  # Le coordinateur peut accéder à tous les canaux
                        authorized = True
                    
                    # Mettre à jour les informations de connexion
                    if client_id in self.client_connections:
                        self.client_connections[client_id]['authenticated'] = True
                        self.client_connections[client_id]['user_id'] = user_id
                        self.client_connections[client_id]['role'] = role
                        self.client_connections[client_id]['token'] = token
                except jwt.InvalidTokenError:
                    logger.warning(f"Token JWT invalide pour {client_id}")
                    authorized = False
            
            # Si non autorisé, renvoyer une erreur
            if not authorized:
                logger.warning(f"Accès non autorisé au canal {channel} pour {client_id}")
                error_response = b'-ERR NOAUTH Permission denied\r\n'
                client_socket.send(error_response)
                return True
            
            # Appliquer les transformateurs de messages
            for transformer in self.message_transformers:
                message = transformer(client_id, channel, message, user_id, role)
            
            # Supprimer le token du message avant de le transmettre
            if 'token' in message:
                del message['token']
            
            # Reconstruire la commande PUBLISH avec le message transformé
            new_message_str = json.dumps(message)
            new_command = f"*3\r\n$7\r\nPUBLISH\r\n${len(channel)}\r\n{channel}\r\n${len(new_message_str)}\r\n{new_message_str}\r\n"
            
            # Envoyer la commande modifiée à Redis
            redis_socket.send(new_command.encode('utf-8'))
            response = redis_socket.recv(4096)
            client_socket.send(response)
            
            return True
        except json.JSONDecodeError:
            logger.warning(f"Format JSON invalide dans le message: {message_str}")
            error_response = b'-ERR WRONGTYPE Invalid JSON format\r\n'
            client_socket.send(error_response)
            return True
        except Exception as e:
            logger.error(f"Erreur lors du traitement de PUBLISH: {e}")
            traceback.print_exc()
            return False
    
    def handle_subscribe(self, client_id, command, client_socket, redis_socket, raw_data):
        """Gère la commande SUBSCRIBE"""
        channels = command.get_channel()
        
        if not channels:
            logger.warning(f"Canaux manquants dans la commande SUBSCRIBE: {command}")
            return False
        
        logger.info(f"SUBSCRIBE aux canaux {channels}")
        
        # Vérifier l'autorisation pour chaque canal
        client_info = self.client_connections.get(client_id, {})
        role = client_info.get('role')
        
        authorized_channels = []
        unauthorized_channels = []
        
        for channel in channels:
            # Canaux ouverts (pas besoin d'authentification)
            if channel in self.open_channels:
                authorized_channels.append(channel)
            # Canaux nécessitant une authentification
            elif client_info.get('authenticated'):
                if role == 'manager' and channel in self.manager_channels:
                    authorized_channels.append(channel)
                elif role == 'volunteer' and channel in self.volunteer_channels:
                    authorized_channels.append(channel)
                elif role == 'coordinator':  # Le coordinateur peut accéder à tous les canaux
                    authorized_channels.append(channel)
                else:
                    unauthorized_channels.append(channel)
            else:
                unauthorized_channels.append(channel)
        
        # Si aucun canal autorisé, renvoyer une erreur
        if not authorized_channels:
            logger.warning(f"Accès non autorisé aux canaux {channels} pour {client_id}")
            error_response = b'-ERR NOAUTH Permission denied\r\n'
            client_socket.send(error_response)
            return True
        
        # Mettre à jour les canaux souscrits
        if client_id in self.client_connections:
            self.client_connections[client_id]['subscribed_channels'].update(authorized_channels)
        
        # S'abonner uniquement aux canaux autorisés
        if len(authorized_channels) == len(channels):
            # Tous les canaux sont autorisés, transmettre la commande telle quelle
            redis_socket.send(raw_data)
        else:
            # Reconstruire la commande SUBSCRIBE avec seulement les canaux autorisés
            parts = [f"*{len(authorized_channels) + 1}", "$9", "SUBSCRIBE"]
            for channel in authorized_channels:
                parts.append(f"${len(channel)}")
                parts.append(channel)
            
            new_command = "\r\n".join(parts) + "\r\n"
            redis_socket.send(new_command.encode('utf-8'))
        
        # Transmettre la réponse au client
        response = redis_socket.recv(4096)
        client_socket.send(response)
        
        # Informer le client des canaux non autorisés
        if unauthorized_channels:
            for channel in unauthorized_channels:
                error_msg = f"Accès non autorisé au canal {channel}"
                error_response = f"$5\r\nerror\r\n${len(channel)}\r\n{channel}\r\n${len(error_msg)}\r\n{error_msg}\r\n"
                client_socket.send(error_response.encode('utf-8'))
        
        return True
    
    def add_metadata(self, client_id, channel, message, user_id=None, role=None):
        """Ajoute des métadonnées au message"""
        # Ajouter des informations sur l'expéditeur
        if user_id:
            message['_sender_id'] = user_id
        if role:
            message['_sender_role'] = role
        
        # Ajouter un timestamp
        message['_timestamp'] = datetime.utcnow().isoformat()
        
        # Ajouter l'adresse IP du client
        if client_id:
            message['_client_ip'] = client_id.split(':')[0]
        
        return message
    
    def filter_sensitive_data(self, client_id, channel, message, user_id=None, role=None):
        """Filtre les données sensibles des messages"""
        # Pour le canal d'enregistrement, on conserve le mot de passe (nécessaire pour créer le compte)
        if channel == 'auth/register':
            # Garder les informations nécessaires à l'enregistrement
            safe_keys = ['username', 'email', 'password', 'request_id', 'client_ip', 'client_info']
            return {k: v for k, v in message.items() if k in safe_keys or k.startswith('_')}
        
        # Pour les autres canaux, masquer les mots de passe
        if 'password' in message:
            message['password'] = '********'
        
        return message

    def _listen_for_published_messages(self):
        """Écoute les messages publiés sur Redis et les transmet aux clients abonnés"""
        try:
            # Utiliser redis-py pour s'abonner aux canaux
            redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            pubsub = redis_client.pubsub()
            
            # S'abonner à tous les canaux connus
            all_channels = list(self.open_channels.keys()) + list(self.manager_channels.keys()) + list(self.volunteer_channels.keys())
            # Filtrer les canaux avec des jokers (#)
            channels_to_subscribe = [channel for channel in all_channels if '#' not in channel]
            
            if channels_to_subscribe:
                logger.info(f"Proxy s'abonne aux canaux: {', '.join(channels_to_subscribe)}")
                pubsub.subscribe(*channels_to_subscribe)
            
            # Boucle d'écoute des messages
            for message in pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = message['data']
                    
                    logger.info(f"Message reçu sur {channel} à transmettre aux clients abonnés")
                    
                    # Convertir le message au format RESP pour le transmettre aux clients
                    resp_message = self._format_pubsub_message(channel, data)
                    
                    # Transmettre le message aux clients abonnés
                    for client_id, client_info in list(self.client_connections.items()):
                        if channel in client_info.get('subscribed_channels', set()):
                            try:
                                client_socket = client_info['socket']
                                client_socket.send(resp_message)
                                logger.debug(f"Message transmis au client {client_id}")
                            except Exception as e:
                                logger.error(f"Erreur lors de la transmission au client {client_id}: {e}")
        
        except Exception as e:
            logger.error(f"Erreur dans le thread d'écoute des messages publiés: {e}")
            import traceback
            traceback.print_exc()
    
    def _format_pubsub_message(self, channel, data):
        """Formate un message pub/sub au format RESP"""
        # Format: *3\r\n$7\r\nmessage\r\n$<len(channel)>\r\n<channel>\r\n$<len(data)>\r\n<data>\r\n
        channel_bytes = channel.encode('utf-8')
        data_bytes = data.encode('utf-8') if isinstance(data, str) else data
        
        resp_message = (
            f"*3\r\n$7\r\nmessage\r\n${len(channel_bytes)}\r\n{channel}\r\n"
            f"${len(data_bytes)}\r\n{data}\r\n"
        ).encode('utf-8')
        
        return resp_message


# Fonction pour démarrer le proxy en tant que service
def start_proxy_service(host='localhost', redis_port=6379, proxy_port=6380):
    """
    Démarre le proxy Redis en tant que service.
    
    Args:
        host: Hôte Redis (défaut: localhost)
        redis_port: Port Redis (défaut: 6379)
        proxy_port: Port sur lequel le proxy écoute (défaut: 6380)
    """
    proxy = RedisProxy(
        redis_host=host,
        redis_port=redis_port,
        proxy_port=proxy_port
    )
    proxy.start()
