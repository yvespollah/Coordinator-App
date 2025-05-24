"""
Proxy Redis pour le contrôle des messages et souscriptions.
Intercepte toutes les commandes Redis pour appliquer des règles d'autorisation.
"""

import socket
import threading
import logging
import json
import traceback
from datetime import datetime
import jwt
from django.conf import settings
import redis

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RedisProxy')

# Définir un niveau de log plus élevé pour réduire les messages
logger.setLevel(logging.INFO)  # Utiliser WARNING au lieu de INFO pour réduire les logs

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

        # Toutes les addresses coorespondate à l'hote local
        self.coordinator_address = [('localhost', 6380), ('127.0.0.1', 6380)]
        
        # Canaux d'enregistrement et d'authentification (toujours autorisés)
        self.open_channels = {
            'auth/register': True,
            'auth/register_response': True,
            'auth/login': True,
            'auth/login_response': True,
            'coord/heartbeat/#': True,
            'coord/emergency': True,
            'task/assignment': True,
            'task/accept': True,
            'task/complete': True,
            'task/progress': True,
            'auth/volunteer_register': True,
            'auth/volunteer_register_response': True,
            'auth/volunteer_login': True,
            'auth/volunteer_login_response': True,
        }
        
        # Canaux réservés aux managers
        self.manager_channels = {
            'tasks/new': True,
            'tasks/assign': True,
            'tasks/status/#': True,
            'manager/status': True,
            'manager/requests': True,
            'workflow/submit': True,
            'workflow/submit_response': True,
        }
        
        # Canaux réservés aux volunteers
        self.volunteer_channels = {
            'volunteer/available': True,
            'volunteer/resources': True,
            'tasks/result/#': True,
            'volunteer/data': True,
            'task/status': True, 
        }

        
        
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
                logger.debug(f"Nouvelle connexion: {client_id}")
                
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
    
    def _remove_client(self, client_id):
        """Supprime un client de la liste des connexions"""
        if client_id in self.client_connections:
            try:
                # Fermer la socket si elle est encore ouverte
                if 'socket' in self.client_connections[client_id]:
                    self.client_connections[client_id]['socket'].close()
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture de la socket du client {client_id}: {e}")
            
            # Supprimer le client de la liste des connexions
            del self.client_connections[client_id]
            logger.info(f"Client {client_id} supprimé de la liste des connexions")
    
    def stop(self):
        """Arrête le proxy"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Fermer toutes les connexions client
        for client_id in list(self.client_connections.keys()):
            self._remove_client(client_id)
            
        
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
                elif command.command_type in ['PING', 'PONG']:
                    # Traiter les commandes PING/PONG directement
                    if command.command_type == 'PING':
                        logger.debug(f"PING reçu de {client_id}")
                        # Transmettre le PING au serveur Redis
                        redis_socket.send(data)
                        response = redis_socket.recv(4096)
                        client_socket.send(response)
                        continue
                    elif command.command_type == 'PONG':
                        logger.debug(f"PONG reçu de {client_id}")
                        # Transmettre le PONG au serveur Redis
                        redis_socket.send(data)
                        continue
                else:
                    # Ne pas logger les commandes CLIENT pour éviter de surcharger les logs
                    if command.command_type != 'CLIENT':
                        logger.info(f"Le message n'est pas pub/sub: {command.command_type},{client_id}")
                    elif command.command_type == 'CLIENT' and logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Commande CLIENT reçue de {client_id}")
                
                # Pour les autres commandes, les transmettre directement
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
        """Gère la commande PUBLISH"""
        channel = command.get_channel()
        message_str = command.get_message()
        
        if not channel or not message_str:
            logger.warning(f"Canal ou message manquant dans la commande PUBLISH: {raw_data}")
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
            
            # Le coordinateur peut publier dans tous les cannaux
            if client_socket.getpeername() in self.coordinator_address:
                authorized = True
            # Canaux nécessitant une authentification
            elif token:
                try:
                    # Vérifier le token JWT
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    logger.info(f"Token JWT valide pour {payload}")
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
                except jwt.InvalidTokenError as e:
                    logger.warning(f"Token JWT invalide pour {client_id}: {str(e)}")
                    authorized = False
            
            # Si non autorisé, renvoyer une erreur
            if not authorized:
                logger.warning(f"Accès non autorisé au canal {channel} pour {client_id}")
                error_response = b'-ERR NOAUTH Permission denied\r\n'
                client_socket.send(error_response)
                return True
            
            # Log du message original avant transformation
            # logger.info(f"Message original avant transformation: {message}")
            
            # Appliquer les transformateurs de messages
            for transformer in self.message_transformers:
                transformer_name = transformer.__name__ if hasattr(transformer, '__name__') else transformer.__class__.__name__
                message_before = message.copy() if isinstance(message, dict) else message
                message = transformer(client_id, channel, message, user_id, role)
                # logger.info(f"Après transformation {transformer_name}: {message}")
                
                # Vérifier si la structure du message a été préservée
                if 'data' in message_before and 'data' not in message:
                    logger.warning(f"La transformation {transformer_name} a supprimé le champ 'data'!")
            
            # Supprimer le token du message avant de le transmettre
            if isinstance(message, dict) and 'token' in message:
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
        
        # Traiter tous les canaux comme autorisés pour éviter les déconnexions
        # Dans un environnement de production, vous voudriez implémenter une vraie vérification d'autorisation
        logger.info(f"SUBSCRIBE aux canaux {channels}")
        
        # Mettre à jour les canaux souscrits
        if client_id in self.client_connections:
            self.client_connections[client_id]['subscribed_channels'].update(channels)
        
        # Transmettre la commande telle quelle au serveur Redis
        redis_socket.send(raw_data)
        
        # Transmettre la réponse au client
        response = redis_socket.recv(4096)
        client_socket.send(response)
        
        return True
    
    def add_metadata(self, client_id, channel, message, user_id=None, role=None):
        """Ajoute des métadonnées au message sans altérer sa structure"""
        # Vérifier si le message est un dictionnaire
        if not isinstance(message, dict):
            logger.warning(f"Message non dict dans add_metadata: {message}")
            return message
            
        # Faire une copie du message pour ne pas modifier l'original
        message_copy = message.copy()
        
        # Ajouter des informations sur l'expéditeur
        if user_id:
            message_copy['_sender_id'] = user_id
        if role:
            message_copy['_sender_role'] = role
        
        # Ajouter un timestamp
        message_copy['_timestamp'] = datetime.utcnow().isoformat()
        
        # Ajouter l'adresse IP du client
        if client_id:
            message_copy['_client_ip'] = client_id.split(':')[0]
        
        # Log pour déboguer
        logger.debug(f"Message après ajout de métadonnées: {message_copy}")
        
        return message_copy
    
    def filter_sensitive_data(self, client_id, channel, message, user_id=None, role=None):
        """Filtre les données sensibles des messages"""
        # Vérifier si le message est un dictionnaire
        if not isinstance(message, dict):
            logger.warning(f"Message non dict: {message}")
            return message
            
        # Pour le canal d'enregistrement, on préserve la structure complète du message
        if channel == 'auth/register':
            # Si le message contient des données dans le champ 'data', les préserver
            if 'data' in message and isinstance(message['data'], dict):
                # On ne touche pas aux données d'enregistrement
                return message
            else:
                # Si les données sont directement dans le message (ancien format)
                safe_keys = ['username', 'email', 'password', 'request_id', 'client_ip', 'client_info', 'sender', 'message_type', 'timestamp', 'data']
                return {k: v for k, v in message.items() if k in safe_keys or k.startswith('_')}
        
        return message

    def _listen_for_published_messages(self):
        """Écoute les messages publiés sur Redis et les transmet aux clients abonnés"""
        try:
            # Utiliser redis-py pour s'abonner aux canaux
            redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            pubsub = redis_client.pubsub()
            
            # S'abonner à tous les canaux connus
            all_channels = list(self.open_channels.keys()) + list(self.manager_channels.keys()) + list(self.volunteer_channels.keys())
            # Ajouter explicitement les canaux de réponse
            response_channels = [
                'auth/register_response',
                'auth/login_response',
                'auth/volunteer_register_response',
                'auth/volunteer_login_response'
            ]
            
            # S'assurer que tous les canaux de réponse sont inclus
            for channel in response_channels:
                if channel not in all_channels:
                    all_channels.append(channel)
            
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
                    
                    logger.info(f"Message {data}reçu sur {channel} à transmettre aux clients abonnés")
                    
                    # Convertir le message au format RESP pour le transmettre aux clients
                    resp_message = self._format_pubsub_message(channel, data)
                    
                    # Transmettre le message aux clients abonnés
                    clients_count = 0
                    for client_id, client_info in list(self.client_connections.items()):
                        # Vérifier si le client est abonné à ce canal
                        subscribed_channels = client_info.get('subscribed_channels', set())
                        
                        # Log pour déboguer
                        logger.debug(f"Client {client_id} est abonné aux canaux: {subscribed_channels}")
                        
                        if channel in subscribed_channels:
                            try:
                                client_socket = client_info['socket']
                                client_socket.send(resp_message)
                                clients_count += 1
                                logger.info(f"Message sur {channel} transmis au client {client_id}")
                            except Exception as e:
                                logger.error(f"Erreur lors de la transmission au client {client_id}: {e}")
                                # Supprimer le client si la connexion est perdue
                                self._remove_client(client_id)
                    
                    if clients_count == 0:
                        logger.warning(f"Aucun client abonné au canal {channel} pour recevoir le message")
                    else:
                        logger.info(f"Message transmis à {clients_count} clients abonnés au canal {channel}")
        
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
